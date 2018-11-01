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
        'id', 'student.name', 'student.roll_no', 'student.batch',
        'campus_drive.company.name', 'campus_drive.drive_year' 'dateofjoining','id', 'id',
    ]
    order_columns = [
        'id', 'student.name', 'student.roll_no', 'student.batch',
        'campus_drive.company.name', 'campus_drive.drive_year' 'dateofjoining','id', 'id',
    ]

    max_display_length = 500

    def get_initial_queryset(self):
        return models.Placements.objects.filter(soft_delete=False).order_by('-id')

    def filter_queryset(self, qs):
        search = self.request.GET.get(u'search[value]', None)
        if search:
            qs = qs.filter(
                Q(id__icontains=search) | Q(student__name__icontains=search) | 
                Q(student__roll_no__icontains=search) | Q(student__batch__icontains=search) |
                Q(campus_drive__company__name__icontains=search) | 
		Q(campus_drive__drive_year__icontains=search) |
		Q(dateofjoining__icontains=search)
            )
        return qs

    def prepare_results(self, qs):
        data = []
        for item in qs:
            data.append([
                item.id,
                item.student.name,
                item.student.roll_no,
                item.student.batch,
                item.campus_drive.company.name,
                item.campus_drive.drive_year,
                item.dateofjoining,
                '/edit-placement/'+str(item.pk),
                '/delete-placement/'+str(item.pk),
            ])
        return data
