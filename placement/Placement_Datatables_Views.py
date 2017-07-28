from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from placement import models
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.db.models import Q
from django.utils import timezone
import pytz
import datetime
from django.conf import settings


class PlacementListDatatable(BaseDatatableView):
    model = models.Placements

    columns = [
        'id', 'student.name', 'student.roll_no', 'company.name', 'package',
        'bond_period','dateofplacement', 'dateofjoining','id', 'id',
    ]
    order_columns = [
        'id', 'student.name', 'student.roll_no', 'company.name', 'package',
        'bond_period','dateofplacement', 'dateofjoining','id', 'id',
    ]

    max_display_length = 500

    def get_initial_queryset(self):
        return models.Placements.objects.filter(soft_delete=False).order_by('-id')

    """def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            qs = qs.filter(
                Q(name__icontains=search) | Q(roll_no__icontains=search) | 
                Q(name__icontains=search) | Q(package__icontains=search) |
                Q(bond_period__icontains=search)
            )
        return qs"""

    def prepare_results(self, qs):
        data = []
        for item in qs:
            data.append([
                item.id,
                item.student.name,
                item.student.roll_no,
                item.company.name,
                item.package,
                item.bond_period,
                item.dateofplacement,
                item.dateofjoining,
                '/edit-placement/'+str(item.pk),
                '/delete-placement/'+str(item.pk),
            ])
        return data
