from django.conf.urls import *
from placement import views
from django.contrib.auth.views import *
from django.contrib.auth.decorators import login_required
from placement import student_datatables_views
from placement import Company_Datatables_Views
from placement import Placement_Datatables_Views
from placement import drive_datatables_views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login$', views.login_view, name = 'login_view'),
    url(r'^accounts/login', views.login_view, name = 'login_view'),
    url(r'^home$', views.home, name = 'home'),
    url(r'^logout$', views.logout_view, name = 'logout_view'),
    url(r'^add-student$', views.add_student, name = 'add_student'),
    url(r'^edit-student/(?P<student_id>[0-9]+)$', views.edit_student, name = 'edit_student'),
    url(r'^delete-student/(?P<student_id>[0-9]+)$', views.delete_student, name = 'delete_student'),
    url(r'^view-students/$', views.view_students, name='view-students'),
    url(r'^view-students-dt/$', login_required(student_datatables_views.StudentListDatatable.as_view()), 
        name='view-students-dt'),
    url(r'^add-company$', views.add_company, name = 'add_company'),
    url(r'^edit-company/(?P<company_id>[0-9]+)$', views.edit_company, name='edit_company'),
    url(r'^view-companies/$', views.view_company, name='view-companies'),
    url(r'^view-companies-dt/$', login_required(Company_Datatables_Views.CompanyListDatatable.as_view()), 
        name='view-companies-dt'),
    url(r'^delete-company/(?P<company_id>[0-9]+)$', views.delete_company, name='delete_company'),
    url(r'^add-placement/(?P<student_id>[0-9]+)$', views.add_placement, name='add_placement'),
    url(r'^view-placements/$', views.view_placement, name='view-placements'),
    url(r'^view-placements-dt/$', login_required(Placement_Datatables_Views.PlacementListDatatable.as_view()), 
        name='view-placements-dt'),
    url(r'^delete-placement/(?P<placements_id>[0-9]+)$', views.delete_placement, name='delete_placement'),
    url(r'^edit-placement/(?P<placements_id>[0-9]+)$', views.edit_placement, name='edit_placement'),
    url(r'^bcharts$', views.bar_chart, name='bcharts'),
    url(r'^pcharts$', views.pie_chart, name='pcharts'),
    url(r'^cpassword$', views.change_password, name='cpassword'),
    url(r'^password_reset/$', views.password_reset, name='password_reset'),
    url(r'^reset-password/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>.+)$', views.password_resetenter, 
        name='password_resetenter'),
    url(r'^test-search/$', views.test_search, name='test_search'),
    url(r'^add-drive/$', views.add_campus_drive, name='add-drive'),
    url(r'^edit-drive/(?P<campusdrive_id>[0-9]+)$', views.edit_campus_drive, name='edit-drive'),
    url(r'^view-drives/$', views.view_campus_drive, name='view-drive'),
    url(r'^view-drive-dt/$', login_required(drive_datatables_views.DriveListDatatable.as_view()), 
        name='view-drive-dt'),
    url(r'^delete-drive/(?P<campusdrive_id>[0-9]+)$', views.delete_campus_drive, name='delete-drive'),
    url(r'^year-ajax$', views.year_ajax, name='year_ajax'),

    url(r'^my-page$', views.mypage, name='my-page'),
]