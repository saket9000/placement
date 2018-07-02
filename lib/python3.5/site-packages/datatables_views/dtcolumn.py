# coding=utf-8
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe


class DTColumn(object):
    """
    Datatable column
    """
    filter_template_path = 'datatables_views/filters/field.jinja2'

    template_name=None

    name = ""
    hidden = False
    field_type="html"
    render_func = None
    className = ""
    cellType = "td"
    filter_func = None
    order_func=None

    def __init__(
            self,
            name="",
            hidden=False,
            field_type=None,
            className="",
            cellType=None,
            search_choices=None,
            render_func=None,
            template_name=None,
            filter_func=None,
            order_func=None
    ):
        self.name = name if name is not None else self.name
        self.hidden = hidden if hidden is not None else False
        self.field_type=field_type if field_type is not None else self.field_type
        if render_func is not None:
            self.render_func = render_func
        else:
            self.render_func = lambda m: "" if not self.template_name else render_to_string(self.template_name, {"column": m})
        self.className = str(className) if className is not None else self.className
        self.cellType = str(cellType) if cellType is not None else self.cellType
        self.template_name = template_name if template_name is not None else self.template_name
        self.filter_func = filter_func
        self.order_func = order_func

        if filter_func and search_choices:
            self.search_choices = search_choices or None
        else:
            self.search_choices = None

    def render(self, item):
        return self.render_func(item)

    def render_filter(self, column_counter=0):
        rendered = render_to_string(self.filter_template_path, {'field': self, 'counter': column_counter})
        return mark_safe(rendered)


class DTFilterColumn(DTColumn):
    """
    Default column with filtering
    """
    hidden = False


class DTOperationsColumn(DTColumn):
    """
    Column without filtering and ordering.
    Usable for place operations buttons.
    """
    hidden = False


class DTHiddenFilterColumn(DTColumn):
    """
    Hidden column that must be filtered.
    """
    name=""
    hidden = True
