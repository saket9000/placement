from django.contrib import admin
from placement.models import *

# Register your models here.

class DeleteNotAllowedAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False


class EmployeeAdmin(DeleteNotAllowedAdmin):
    list_display = [
        "e_id", "user", "name", "dob", "phone", "blood_group",
        "student_permit", "placement_permit", 
        "company_permit", "soft_delete", "photo",
    ]
    list_filter = [
        "student_permit", "placement_permit",
        "company_permit", "soft_delete",
    ]


class StudentAdmin(DeleteNotAllowedAdmin):
    list_display = [
        "roll_no", "name", "dob", "phone", "blood_group",
        "guardian_name", "guardian_phone", "batch",
        "email", "course", "soft_delete"
    ]
    list_filter = [
        "course", "batch", "soft_delete"
    ]


class CourseAdmin(DeleteNotAllowedAdmin):
    list_display = [
        "name", "abbr", "duration", "soft_delete",
    ]
    list_filter = [
        "duration", "soft_delete"
    ]


class CompanyAdmin(DeleteNotAllowedAdmin):
    list_display = [
        "name", "address", "phone", "soft_delete",
    ]


class PlacementsAdmin(DeleteNotAllowedAdmin):
    list_display = [
        "student", "campus_drive", "soft_delete",
    ]
    list_filter = [
        "campus_drive", "soft_delete"
    ]

class CampusDriveAdmin(DeleteNotAllowedAdmin):
    list_display = [
        "company", "drive_year", "package","soft_delete",
    ]
    list_filter = [
        "company", "drive_year", "soft_delete"
    ]


class HistoryAdmin(DeleteNotAllowedAdmin):
    list_display = [
        "user", "activity_type", "activity"
    ]
    list_filter = [
        "user", "activity_type"
    ]
    readonly_fields = [
        "user", "activity", "activity_type", "soft_delete"
    ]

    def has_add_permission(self, request):
        return False

    def has_delete_permissions(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super(HistoryAdmin, self).save_model(request, obj, form, change)


class PasswordResetAdmin(DeleteNotAllowedAdmin):
    list_display = [
        "user", "password_request_created_at", "token_consumed"
    ]
    list_filter = [
        "password_request_created_at", "token_consumed"
    ]
    readonly_fields = [
        "user", "password_request_created_at", "token",
        "token_consumed", "soft_delete",
    ]

    def has_add_permission(self, request):
        return False

    def has_delete_permissions(self, request, obj=None):
        return False

        
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Placements, PlacementsAdmin)
admin.site.register(CampusDrive, CampusDriveAdmin)
admin.site.register(History, HistoryAdmin)
admin.site.register(PasswordReset, PasswordResetAdmin)
admin.site.disable_action("delete_selected")
