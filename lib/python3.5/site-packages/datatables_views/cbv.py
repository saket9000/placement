# coding=utf-8
from django.views.generic import TemplateView
import itertools

from django.http import HttpResponse
import json
from django.utils.cache import add_never_cache_headers


def jsonResp(data):
    """
    Используется для ajax
    Сериализует data используя json.dumps и возвращает HttpResponse объект
    """

    resp = HttpResponse(
        json.dumps(data),
        content_type="application/json"
    )
    add_never_cache_headers(resp)
    return resp


class DataTableListView(TemplateView):
    model = None
    queryset = None
    template_name = "core/datatablelist.jinja2"
    table_id = "dt_table"
    dt_fields = []

    _filtered_count = 0

    def get_context_data(self, *a, **k):
        context = super(DataTableListView, self).get_context_data(*a, **k)
        context["table_fields"] = self.get_table_fields()
        context["table_id"] = self.table_id or "dt_table"
        return context

    def get_table_fields(self):
        return self.dt_fields

    def filter_res(self, qs):
        i = 0
        try:
            while True:
                col_search = self.request.POST["columns["+str(i)+"][search][value]"]
                if col_search:
                    filter_func = self.get_table_fields()[i].filter_func
                    if filter_func:
                        qs = filter_func(qs, unicode(col_search))
                i += 1
        except KeyError:
            pass
        return qs.distinct()

    def post_queryset(self):
        if self.queryset is not None:
            return self.queryset
        else:
            return self.model.objects.all()

    def post_list(self):
        qs = self.post_queryset()
        qs = self.filter_res(qs)
        self._filtered_count = qs.count()
        qs = self.order_res(qs)
        return (self.post_serialize_item(m) for m in qs)

    def post_serialize_item(self, item):
        return map(
            lambda dtfield: dtfield.render(item),
            self.get_table_fields()
        )

    def order_res(self, qs):
        def order_column(qs, column_index, direction):
            order_func = self.get_table_fields()[column_index].order_func
            if order_func:
                qs = order_func(qs, direction == "asc")
            return qs.distinct()

        try:
            i = 0
            while True:
                order_col = int(self.request.POST["order["+str(i)+"][column]"])
                direction = self.request.POST["order["+str(i)+"][dir]"]
                if order_col and direction:
                    qs = order_column(qs, order_col, direction)
                i += 1
        except KeyError:
            pass
        return qs.distinct()

    def paginate_res(self, res):

        try:
            start = int(self.request.POST.get("start", 0))
        except:
            start = 0
        try:
            length = int(self.request.POST.get("length", None))
            if length < 0:
                length = None
        except:
            return res

        return [x for x in itertools.islice(res, start, int(start+length) if length else None)]

    def post(self, request):
        res = self.post_list()
        return jsonResp({
            "recordsTotal": self.post_queryset().count(),
            'recordsFiltered': self._filtered_count,
            'data': list(self.paginate_res(res))
        })
