# -*- coding: utf-8 -*-
import logging

from django.db.models import Q
from django.utils.html import escape

from .mixins import JSONResponseView

logger = logging.getLogger(__name__)


class DatatableMixin(object):
    """ JSON data for datatables
    """
    model = None
    columns = []
    order_columns = []
    max_display_length = 100  # max limit of records returned, do not allow to kill our server by huge sets of data
    pre_camel_case_notation = False  # datatables 1.10 changed query string parameter names
    none_string = ''
    escape_values = True  # if set to true then values returned by render_column will be escaped
    
    @property
    def _querydict(self):
        if self.request.method == 'POST':
            return self.request.POST
        else:
            return self.request.GET

    def initialize(self, *args, **kwargs):
        if 'iSortingCols' in self._querydict:
            self.pre_camel_case_notation = True

    def get_order_columns(self):
        """ Return list of columns used for ordering
        """
        return self.order_columns

    def get_columns(self):
        """ Returns the list of columns that are returned in the result set
        """
        return self.columns

    def render_column(self, row, column):
        """ Renders a column on a row. column can be given in a module notation eg. document.invoice.type
        """
        # try to find rightmost object
        obj = row
        parts = column.split('.')
        for part in parts[:-1]:
            if obj is None:
                break
            obj = getattr(obj, part)

        # try using get_OBJECT_display for choice fields
        if hasattr(obj, 'get_%s_display' % parts[-1]):
            value = getattr(obj, 'get_%s_display' % parts[-1])()
        else:
            value = getattr(obj, parts[-1], None)

        if value is None:
            value = self.none_string

        if self.escape_values:
            value = escape(value)
            
        if value and hasattr(obj, 'get_absolute_url'):
            return '<a href="%s">%s</a>' % (obj.get_absolute_url(), value)
        return value

    def ordering(self, qs):
        """ Get parameters from the request and prepare order by clause
        """

        # Number of columns that are used in sorting
        sorting_cols = 0
        if self.pre_camel_case_notation:
            try:
                sorting_cols = int(self._querydict.get('iSortingCols', 0))
            except ValueError:
                sorting_cols = 0
        else:
            sort_key = 'order[{0}][column]'.format(sorting_cols)
            while sort_key in self._querydict:
                sorting_cols += 1
                sort_key = 'order[{0}][column]'.format(sorting_cols)

        order = []
        order_columns = self.get_order_columns()

        for i in range(sorting_cols):
            # sorting column
            sort_dir = 'asc'
            try:
                if self.pre_camel_case_notation:
                    sort_col = int(self._querydict.get('iSortCol_{0}'.format(i)))
                    # sorting order
                    sort_dir = self._querydict.get('sSortDir_{0}'.format(i))
                else:
                    sort_col = int(self._querydict.get('order[{0}][column]'.format(i)))
                    # sorting order
                    sort_dir = self._querydict.get('order[{0}][dir]'.format(i))
            except ValueError:
                sort_col = 0

            sdir = '-' if sort_dir == 'desc' else ''
            sortcol = order_columns[sort_col]

            if isinstance(sortcol, list):
                for sc in sortcol:
                    order.append('{0}{1}'.format(sdir, sc.replace('.', '__')))
            else:
                order.append('{0}{1}'.format(sdir, sortcol.replace('.', '__')))

        if order:
            return qs.order_by(*order)
        return qs

    def paging(self, qs):
        """ Paging
        """
        if self.pre_camel_case_notation:
            limit = min(int(self._querydict.get('iDisplayLength', 10)), self.max_display_length)
            start = int(self._querydict.get('iDisplayStart', 0))
        else:
            limit = min(int(self._querydict.get('length', 10)), self.max_display_length)
            start = int(self._querydict.get('start', 0))

        # if pagination is disabled ("paging": false)
        if limit == -1:
            return qs

        offset = start + limit

        return qs[start:offset]

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return self.model.objects.all()

    def extract_datatables_column_data(self):
        """ Helper method to extract columns data from request as passed by Datatables 1.10+
        """
        request_dict = self._querydict
        col_data = []
        if not self.pre_camel_case_notation:
            counter = 0
            data_name_key = 'columns[{0}][name]'.format(counter)
            while data_name_key in request_dict:
                searchable = True if request_dict.get('columns[{0}][searchable]'.format(counter)) == 'true' else False
                orderable = True if request_dict.get('columns[{0}][orderable]'.format(counter)) == 'true' else False

                col_data.append({'name': request_dict.get(data_name_key),
                                 'data': request_dict.get('columns[{0}][data]'.format(counter)),
                                 'searchable': searchable,
                                 'orderable': orderable,
                                 'search.value': request_dict.get('columns[{0}][search][value]'.format(counter)),
                                 'search.regex': request_dict.get('columns[{0}][search][regex]'.format(counter)),
                                 })
                counter += 1
                data_name_key = 'columns[{0}][name]'.format(counter)
        return col_data

    def filter_queryset(self, qs):
        """ If search['value'] is provided then filter all searchable columns using istartswith
        """
        if not self.pre_camel_case_notation:
            # get global search value
            search = self._querydict.get('search[value]', None)
            col_data = self.extract_datatables_column_data()
            q = Q()
            for col_no, col in enumerate(col_data):
                # apply global search to all searchable columns
                if search and col['searchable']:
                    q |= Q(**{'{0}__istartswith'.format(self.columns[col_no].replace('.', '__')): search})

                # column specific filter
                if col['search.value']:
                    qs = qs.filter(**{
                        '{0}__istartswith'.format(self.columns[col_no].replace('.', '__')): col['search.value']})
            qs = qs.filter(q)
        return qs

    def prepare_results(self, qs):
        data = []
        for item in qs:
            data.append([self.render_column(item, column) for column in self.get_columns()])
        return data

    def handle_exception(self, e):
        logger.exception(str(e))
        raise e

    def get_context_data(self, *args, **kwargs):
        try:
            self.initialize(*args, **kwargs)

            qs = self.get_initial_queryset()

            # number of records before filtering
            total_records = qs.count()

            qs = self.filter_queryset(qs)

            # number of records after filtering
            total_display_records = qs.count()

            qs = self.ordering(qs)
            qs = self.paging(qs)

            # prepare output data
            if self.pre_camel_case_notation:
                aaData = self.prepare_results(qs)

                ret = {'sEcho': int(self._querydict.get('sEcho', 0)),
                       'iTotalRecords': total_records,
                       'iTotalDisplayRecords': total_display_records,
                       'aaData': aaData
                       }
            else:
                data = self.prepare_results(qs)

                ret = {'draw': int(self._querydict.get('draw', 0)),
                       'recordsTotal': total_records,
                       'recordsFiltered': total_display_records,
                       'data': data
                       }
            return ret
        except Exception as e:
            return self.handle_exception(e)


class BaseDatatableView(DatatableMixin, JSONResponseView):
    pass
