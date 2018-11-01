from django.shortcuts import (render, render_to_response)
from django.http import (
    HttpResponse,
    HttpResponseRedirect,
    JsonResponse,
    Http404
)
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from placement import models
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.conf import settings
from django.core.cache import cache
from placement.helpers import context_helper
from django.template.context import RequestContext
from django.contrib.auth.models import User
from django.db.models import Q
from django.core import serializers
import json
from django.db.models.query_utils import Q
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six, timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template import loader
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from placement_portal.settings import DEFAULT_FROM_EMAIL
from django.views.generic import *
from string import ascii_letters, digits
from datetime import datetime, timedelta
import hashlib
import random

from .forms import AddForm



# Create your views here.

def mypage(request):
    form = AddForm(request.POST or None)
    if form.is_valid():
        form.save()
    return render(request, "add.html", {'form':form})


def handler404(request):

    """
    404 page handler.
    """

    response = render_to_response('404.html', {}, 
        context_instance=RequestContext(request))
    response.status_code = 404
    return response


def handler500(request):

    """
    500 error handler.
    """

    response = render_to_response('500.html', {}, 
        context_instance=RequestContext(request))
    response.status_code = 500
    return response


def index(request):

    """
    This view redirects user to home if logged in else it redirects user
    to login page.
    """

    if request.user.is_authenticated:
        return HttpResponseRedirect('home')
    return HttpResponseRedirect('login')


@login_required
def change_password(request):

    """
    Change password form
    """

    emp = models.Employee.objects.get(user=request.user)
    context_dict = {}
    if request.method == 'POST':
        form = AdminPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            context_dict["message"] = "Password changed successfully"
            history = models.History(
                user=emp,
                activity="",
                activity_type="Changed password"
            )
            history.save()
        else:
            context_dict["message"] = "Password not changed"
    return render(request, "ChangePassword.html", context_dict)


@login_required
def home(request):
    
    """
    This renders the home page.
    """

    context_dict = {}
    employee = models.Employee.objects.filter(
        user=request.user
    ).first()
    # context_dict = {
    #     context_helper.get_emp_info(employee)
    # }
    # print (context_dict)
    context_dict.update(context_helper.get_emp_info(employee))
    return render(request, "HomePage.html", context_dict)


def login_view(request):

    """
    Login view imported from templates.
    """
    if request.user.is_authenticated:
        return HttpResponseRedirect('home')
    next_url = request.GET.get('next', '/home')
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return HttpResponseRedirect(next_url)
            return render(
                request, 'index.html',
                {'message': 'Invalid login details'}
            )
    return render(request, "index.html", {})


def logout_view(request):

    """
    Log out user to the login page.
    """

    logout(request)
    return HttpResponseRedirect('login')


def password_reset(request):

    """
    View to take email and mail the link to
    reset password.
    """

    context_dict = {}
    if request.method == 'POST':
        email = request.POST.get('email')
        if email:
            user = models.Employee.objects.get(
                soft_delete=False, user__email=email
            )
            if not user:
                context_dict["message"] = "Email ID does'nt exist, Enter Correct details"
            mail = {
                'email': email,
                'domain': request.META['HTTP_HOST'],
                'site_name': 'Placement Portal',
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'user': user,
                'token': ''.join([random.choice(ascii_letters+digits) for i in range (128)]),
                'protocol': 'http',
            }
            try:
                reset_token = models.PasswordReset(
                    user=user,
                    token=mail['token'],
                    token_consumed=False,
                )
                reset_token.save()
            except Exception as e:
                print (e)
            subject_template_name = 'password_reset_email_subject.txt'
            email_template_name = 'password_reset_email.html'
            subject = loader.render_to_string(subject_template_name, mail)
            subject = ''.join(subject.splitlines())
            email_data = loader.render_to_string(email_template_name, mail)
            send_mail(subject, email_data, DEFAULT_FROM_EMAIL, [email], fail_silently=False)
            context_dict["message"] = "Email has been sent to your registered Email ID with instructions."
    return render(request, "password_reset_form.html", context_dict)


def password_resetenter(request, uidb64=None, token=None):

    """
    Enter new password for reset password.
    """

    context_dict = {}
    if request.method == 'POST':
        assert uidb64 is not None and token is not None
        uid = urlsafe_base64_decode(uidb64)
        user = models.Employee.objects.get(
            soft_delete=False, pk=uid
        )
        db_user = user.user
        reset_token = models.PasswordReset.objects.get(
            token=token, user=user
        )
        token_check = models.PasswordReset.objects.filter(
            user=user, soft_delete=False, token_consumed=False,
        ).exclude(token=token).first()
        update_fields = []
        token_check.token_consumed = True
        update_fields.append('token_consumed')
        token_check.soft_delete = True
        update_fields.append('soft_delete')
        token_check.save(update_fields=update_fields)
        time_threshold = timezone.now() - reset_token.password_request_created_at
        if time_threshold > timedelta(minutes=30):
            try:
                update_fields = []
                reset_token.token_consumed = True
                update_fields.append('token_consumed')
                reset_token.soft_delete = True
                update_fields.append('soft_delete')
                reset_token.save(update_fields=update_fields)
            except Exception as e:
                print (e)
        if reset_token.user == user and reset_token.token == token:
            if reset_token.token_consumed  == False and reset_token.soft_delete  == False:
                try:
                    update_fields = []
                    reset_token.token_consumed = True
                    update_fields.append('token_consumed')
                    reset_token.soft_delete = True
                    update_fields.append('soft_delete')
                    reset_token.save(update_fields=update_fields)
                except Exception as e:
                    print (e)
                form = AdminPasswordChangeForm(user=db_user, data=request.POST)
                if form.is_valid():
                    form.save()
                    history = models.History(
                        user=user,
                        activity = "",
                        activity_type = "Reset Password"
                    )
                    history.save()
                    context_dict["message"] = "Password changed successfully"
                else:
                    context_dict["message"] = "Password not changed"
            else:
                context_dict["message"] = "Link is no longer valid"
    return render(request, "reset.html", context_dict)


@login_required
def add_student(request):

    """
    Add student to the database.
    """

    emp = models.Employee.objects.get(user=request.user)
    if not emp.student_permit:
        raise Http404
    context_dict = {
        "all_courses": context_helper.course_helper(),
        "blood_groups": context_helper.blood_group_helper(),
        "guardian_types": context_helper.guardian_type_helper(),
        "gender_type": context_helper.gender_helper(),
    }
    if request.method == 'POST':
        sname = request.POST.get('sname')
        roll = request.POST.get('rno')
        dob = request.POST.get('dob')
        gender = request.POST.get('gender_picker')
        bgroup = request.POST.get('blood_group_picker')
        if bgroup == 'Choose option':
            bgroup = None
        phone = request.POST.get('phone')
        curradd = request.POST.get('curradd')
        permadd = request.POST.get('permadd')
        gname = request.POST.get('gname')
        course = request.POST.get('course_picker')
        batch = request.POST.get('batch')
        gtype = request.POST.get('guardian_type_picker')
        gphone = request.POST.get('gphone')
        email = request.POST.get('email')
        duplicate_student = models.Student.objects.filter(
            name=sname, dob=dob, guardian_name=gname,
            guardian_type=gtype, phone=phone, email=email
        ).first()
        if duplicate_student:
            context_dict["message"] = 'Student already exist.'
            duplicate_student.soft_delete=False
            duplicate_student.save()
            return render(request, "AddStudent.html", context_dict)
        address_flag = request.POST.get('address_flag')
        address_flag = True if address_flag == 'on' else False
        if address_flag == True:
            permadd = curradd
        try:
            student = models.Student(
                name=sname,
                roll_no=roll,
                dob=dob,
                gender=gender,
                blood_group=bgroup,
                phone=phone,
                curr_address=curradd,
                perm_address=permadd,
                guardian_name=gname,
                guardian_type=gtype,
                guardian_phone=gphone,
                course=models.Course.objects.get(pk=course),
                batch=batch,
                email=email,
                address_flag=address_flag
            )
            if "profile-img" in request.FILES:
                student.photo = request.FILES["profile-img"]
            student.save()
            history = models.History(
                user=emp,
                activity='Added roll number' + str(roll) +'.\n',
                activity_type="add student"
            )
            history.save()
            context_dict["message"] = 'Successfully added new student.'
            context_dict["success"] = True
        except Exception as e:
            context_dict["message"] = str(e)
            context_dict["success"] = False
            print(e)
    return render(
        request, "AddStudent.html", context_dict
    )


@login_required
def add_company(request):

    """
    Add company to the database.
    """

    emp = models.Employee.objects.get(user=request.user)
    if not emp.company_permit:
        raise Http404
    context_dict = {}
    if request.method == 'POST':
        cname = request.POST.get('c_name')
        c_add = request.POST.get('c_address')
        contact_person = request.POST.get('hr_name')
        c_phone = request.POST.get('c_phone')
        c_email = request.POST.get('c_email')
        duplicate_company = models.Company.objects.filter(
            name=cname,address=c_add, phone=c_phone,
            contact_person=contact_person, email=c_email,
        ).first()
        if duplicate_company:
            context_dict["message"] = 'Company already exists.'
            duplicate_company.soft_delete=False
            duplicate_company.save()
            return render(request, "AddCompany.html", context_dict)
        try:
            company = models.Company(
                name=cname,
                address=c_add,
                phone=c_phone,
                contact_person=contact_person,
                email=c_email,
            )
            company.save()
            history = models.History(
                user=emp,
                activity='Added Company' + str(cname) + '.\n',
                activity_type="add company"
            )
            history.save()
            context_dict["message"] = 'Company added Successfully.'
            context_dict["success"] = True
        except Exception as e:
            context_dict["message"] = str(e)
            context_dict["success"] = False
            print(e)
    return render(
        request, "AddCompany.html", context_dict
    )


@login_required
def edit_student(request, student_id):

    """
    View to edit the already existing student in database by taking student_id.
    """

    emp = models.Employee.objects.get(user=request.user)
    if not emp.student_permit:
        raise Http404
    student = models.Student.objects.filter(
        pk=student_id, soft_delete=False
    ).first()
    if not student:
        raise Http404
    context_dict = {
        "all_courses": context_helper.course_helper(),
        "blood_groups": context_helper.blood_group_helper(),
        "guardian_types": context_helper.guardian_type_helper(),
        "gender_types": context_helper.gender_helper(),
        'student_id': student_id
    }
    if request.method == 'POST':
        update_fields = []
        activity = ''
        sname = request.POST.get('sname')
        roll = request.POST.get('rno')
        dob = request.POST.get('dob')
        gender = request.POST.get('gender_picker')
        bgroup = request.POST.get('blood_group_picker')
        if bgroup == 'Choose option':
            bgroup = None
        phone = request.POST.get('phone')
        curradd = request.POST.get('curradd')
        permadd = request.POST.get('permadd')
        gname = request.POST.get('gname')
        course = request.POST.get('course_picker')
        batch = request.POST.get('batch')
        gtype = request.POST.get('guardian_type_picker')
        gphone = request.POST.get('gphone')
        email = request.POST.get('email')
        address_flag = request.POST.get('address_flag')
        print (address_flag)
        address_flag = True if address_flag == 'on' else False
        if address_flag == True:
            permadd = curradd
        try:
            if "profile-img" in request.FILES:
                student.photo = request.FILES["profile-img"]
                update_fields.append('photo')
                activity += 'Changed photo.\n'
            if student.name != sname:
                student.name = sname
                update_fields.append('name')
                activity += 'Changed name to '+ str(sname) +'.\n'
            if student.roll_no != roll:
                student.roll_no = roll
                update_fields.append('roll_no')
                activity += 'Changed roll number to '+ str(roll) +'.\n'
            if str(student.dob) != str(dob):
                student.dob = dob
                update_fields.append('dob')
                activity += 'Changed DOB to ' + str(dob) + '.\n'
            if student.gender != gender:
                student.gender = gender
                update_fields.append('gender')
                activity += 'Changed gender to ' + str(gender) + '.\n'
            if student.blood_group != bgroup:
                student.blood_group = bgroup
                update_fields.append('blood_group')
                activity += 'Changed blood group to ' + str(bgroup) + '.\n'
            if student.phone != phone:
                student.phone = phone
                update_fields.append('phone')
                activity += 'Changed phone number to ' + str(phone) + '.\n'
            if student.curr_address != curradd:
                student.curr_address = curradd
                update_fields.append('curr_address')
                activity += 'Changed current address to ' + str(curradd) + '.\n'
            if student.perm_address != permadd:
                student.perm_address = permadd
                update_fields.append('perm_address')
                activity += 'Changed permanent address to ' + str(permadd) + '.\n'
            if student.curr_address != curradd:
                student.curr_address = curradd
                update_fields.append('curr_address')
                activity += 'Changed current address to ' + str(curradd) + '.\n'
            if student.guardian_name != gname:
                student.guardian_name = gname
                update_fields.append('guardian_name')
                activity += 'Changed current address to ' + str(gname) + '.\n'
            if student.guardian_phone != gphone:
                student.guardian_phone = gphone
                update_fields.append('guardian_phone')
                activity += 'Changed guardian phone to ' + str(gphone) + '.\n'
            if student.guardian_type != gtype:
                student.guardian_type = gtype
                update_fields.append('guardian_type')
                activity += 'Changed current address to ' + str(gtype) + '.\n'
            if str(student.course.pk) != str(course):
                student.course = models.Course.objects.get(pk=course)
                update_fields.append('course')
                activity += 'Changed course to ' + str(course) + '.\n'
            if student.batch != batch:
                student.batch = batch
                update_fields.append('batch')
                activity += 'Changed batch to' + str(batch) + '.\n'
            if student.email != email:
                student.email = email
                update_fields.append('email')
                activity += 'Changed email to ' + str(email) + '.\n'
            if student.address_flag != address_flag:
                student.address_flag = address_flag
                update_fields.append('address_flag')
                activity += 'Changed address flag.'
            student.save(update_fields=update_fields)
            history = models.History(
                user=emp,
                activity=activity,
                activity_type="edit student"
            )
            history.save()
            context_dict["message"] = 'Successfully updated student.'
            context_dict["success"] = True
        except Exception as e:
            context_dict["message"] = str(e)
            context_dict["success"] = False
            print(e)
    context_dict.update(context_helper.get_student_info(student))
    if type(context_dict['dob']) == str:
        context_dict['dob'] = datetime.strptime(context_dict['dob'], '%Y-%m-%d')
    for i in context_dict['course']:
        try: del context_dict['all_courses'][i]
        except: pass
    for i in context_dict['blood_group']:
        try: context_dict['blood_groups'].remove(i)
        except: pass
    for i in context_dict['guardian_type']:
        try: context_dict['guardian_types'].remove(i)
        except: pass
    for i in context_dict['gender_type']:
        try: context_dict['gender_types'].remove(i)
        except: pass
    if context_dict.get('success', False):
        return HttpResponseRedirect('/view-students')
    return render(
        request, "EditStudent.html", context_dict
    )


@login_required
def edit_company(request, company_id):

    """
    View to edit company.
    """

    emp = models.Employee.objects.get(user=request.user)
    if not emp.company_permit:
        raise Http404
    company = models.Company.objects.filter(
        pk=company_id, soft_delete=False
    ).first()
    if not company:
        raise Http404
    context_dict = {
        'company_id': company_id
    }
    if request.method == 'POST':
        update_fields = []
        activity = ''
        cname = request.POST.get('c_name')
        c_add = request.POST.get('c_address')
        contact_person = request.POST.get('hr_name')
        c_phone = request.POST.get('c_phone')
        c_email = request.POST.get('c_email')
        try:
            if company.name != cname:
                company.name = cname
                update_fields.append('name')
                activity += 'Changed company name to '+ str(cname) +'.\n'
            if company.phone != c_phone:
                company.phone = c_phone
                update_fields.append('phone')
                activity += 'Changed company phone to '+ str(c_phone) +'.\n'
            if company.address != c_add:
                company.address = c_add
                update_fields.append('address')
                activity += 'Changed company address to '+ str(c_add) +'.\n'
            if company.contact_person != contact_person:
                company.contact_person = contact_person
                update_fields.append('contact_person')
                activity += 'Changed company contact person to '+ str(contact_person) +'.\n'
            if company.email != c_email:
                company.email = c_email
                update_fields.append('email')
                activity += 'Changed company email to '+ str(c_email) +'.\n'
            company.save(update_fields=update_fields)
            history = models.History(
                user=emp,
                activity=activity,
                activity_type="edit company"
            )
            history.save()
            context_dict["message"] = 'Successfully updated company.'
            context_dict["success"] = True
        except Exception as e:
            context_dict["message"] = str(e)
            context_dict["success"] = False
            print(e)
    context_dict.update(context_helper.get_company_info(company))
    if context_dict.get('success', False):
        return HttpResponseRedirect('/view-companies')
    return render(
        request, "EditCompany.html", context_dict
    )


@login_required
def view_students(request):

    """
    View students in data tables.
    """

    context_dict = {
        'title': 'All Students'
    }
    return render(
        request,
        'ViewStudent.html',
        context_dict
    )


@login_required
def view_company(request):

    """
    to view the details of all companies in the tabular form.
    """

    context_dict = {
        'title': 'All Companies'
    }
    return render(
        request,
        'ViewCompany.html',
        context_dict
    )


@login_required
def delete_student(request, student_id):

    """
    Delete student from data tables.
    """

    emp = models.Employee.objects.get(user=request.user)
    if not emp.student_permit:
        raise Http404
    student = models.Student.objects.filter(
        pk=student_id, soft_delete=False
    ).first()
    if not student:
        raise Http404
    student.soft_delete = True
    activity = 'Deleted student' + str(student) + '.\n'
    student.save(update_fields=['soft_delete'])
    history = models.History(
                user=emp,
                activity=activity,
                activity_type="delete student"
            )
    history.save()
    return HttpResponseRedirect('/view-students')


@login_required
def delete_company(request, company_id):

    """
    view to delete company by taking company id as argument.
    """

    emp = models.Employee.objects.get(user=request.user)
    if not emp.company_permit:
        raise Http404
    company = models.Company.objects.filter(
        pk=company_id, soft_delete=False
    ).first()
    if not company:
        raise Http404
    company.soft_delete = True
    activity = 'Deleted company' + str(company) + '.\n'
    company.save(update_fields=['soft_delete'])
    history = models.History(
                user=emp,
                activity=activity,
                activity_type="delete company"
            )
    history.save()
    return HttpResponseRedirect('/view-companies')


@login_required
def add_placement(request, student_id):

    """
    Add placement of the student using student_id and taking company from select picker.
    """

    emp = models.Employee.objects.get(user=request.user)
    if not emp.placement_permit:
        raise Http404
    dyears = models.CampusDrive.objects.filter(soft_delete=False).values(
        'drive_year'
    ).distinct()
    print (dyears)
    x = [i['drive_year'] for i in dyears]
    print (x)
    context_dict = {
        "all_drives" : context_helper.drives_info(),
        "dyears": x,
        'student_id': student_id,
    }
    student = models.Student.objects.filter(
        pk=student_id, soft_delete=False
    ).first()
    if not student:
        raise Http404
    context_dict.update(context_helper.get_student_info(student))
    if request.method == 'POST':
        drive = request.POST.get('drive_picker')
        doj = request.POST.get('doj')
        if doj == "":
            doj = None
        duplicate_placement = models.Placements.objects.filter(
            student=student, campus_drive=models.CampusDrive.objects.get(pk=drive),
        ).first()
        if duplicate_placement:
            context_dict["message"] = 'Placement already exists.'
            duplicate_placement.soft_delete = False
            duplicate_placement.save()
            return render(request, "AddPlacement.html", context_dict)
        try:
            placement = models.Placements(
                student = models.Student.objects.get(pk=student_id),
                campus_drive = models.CampusDrive.objects.get(pk=drive),
                dateofjoining = doj,
            )
            placement.save()
            history = models.History(
                user=emp,
                activity="",
                activity_type="add placement"
            )
            history.save()
            context_dict["message"] = 'Successfully added new placement.'
            context_dict["success"] = True
        except Exception as e:
            context_dict["message"] = str(e)
            context_dict["success"] = False
            print(e)
    return render(request, "AddPlacement.html", context_dict)


@login_required
def view_placement(request):

    """
    to view the details of all students placed in the tabular form.
    """

    context_dict = {
        'title': 'All Placements'
    }
    return render(
        request,
        'ViewPlacement.html',
        context_dict
    )


@login_required
def delete_placement(request, placements_id):

    """
    view to delete placement by taking placement id as argument.
    """

    emp = models.Employee.objects.get(user=request.user)
    if not emp.placement_permit:
        raise Http404
    placement = models.Placements.objects.filter(
        pk=placements_id, soft_delete=False
    ).first()
    if not placement:
        raise Http404
    placement.soft_delete = True
    activity = 'Deleted placement' + str(placement) + '.\n'
    placement.save(update_fields=['soft_delete'])
    history = models.History(
                user=emp,
                activity=activity,
                activity_type="delete placement"
            )
    history.save()
    return HttpResponseRedirect('/view-placements')


@login_required
def edit_placement(request, placements_id):

    """
    views to edit placement.
    """

    emp = models.Employee.objects.get(user=request.user)
    if not emp.placement_permit:
        raise Http404
    placement = models.Placements.objects.filter(
        pk=placements_id, soft_delete=False
    ).first()
    if not placement:
        raise Http404
    context_dict = {
        'placements_id': placements_id,
        "all_drives": context_helper.drives_info()
    }
    if request.method == 'POST':
        update_fields = []
        activity = ''
        drive = request.POST.get('company_select')
        doj = request.POST.get('doj')
        if doj == "":
            doj = None
        try:
            if str(placement.campus_drive.pk) != str(drive):
                try:
                    old_drive = placement.campus_drive
                    placement.campus_drive = models.CampusDrive.objects.get(pk=drive)
                    placement.save()
                except Exception as e:
                    placement.soft_delete = True
                    placement.campus_drive = old_drive
                    placement.save()
                    placement = models.Placements.objects.filter(
                        soft_delete=True, student=placement.student,
                        campus_drive__pk=drive
                    ).first()
                    placement.soft_delete = False
                    placement.campus_drive = models.CampusDrive.objects.get(pk=drive)
                    placement.save(update_fields=['soft_delete', 'drive'])
                update_fields.append('drive')
                activity += 'Changed drive to ' + str(drive) + '.\n'
            if placement.dateofjoining != doj:
                placement.dateofjoining = doj
                update_fields.append('dateofjoining')
                activity += 'Changed date of joining to ' + str(doj) + '.\n'
            placement.save(update_fields=update_fields)
            history = models.History(
                user=emp,
                activity=activity,
                activity_type="edit placement"
            )
            history.save()
            context_dict["message"] = 'Successfully updated company.'
            context_dict["success"] = True
        except Exception as e:
            context_dict["message"] = str(e)
            context_dict["success"] = False
            print(e)
    context_dict.update(context_helper.get_placement_info(placement))
    for i in context_dict['drive']:
        try: del context_dict['all_drives'][i]
        except: pass
    if context_dict.get('success', False):
        return HttpResponseRedirect('/view-placements')
    return render(
        request, "editPlacement.html", context_dict
    )


@login_required
def add_campus_drive(request):

    """
    Method to add the campus drive of company year wise.
    """

    context_dict = {}
    emp = models.Employee.objects.get(user=request.user)
    if not emp.placement_permit:
        raise Http404
    context_dict = {
        "all_companies": context_helper.company_select()
    }
    if request.method == 'POST':
        company = request.POST.get('company_picker')
        drive_year = request.POST.get('driveyear')
        package = request.POST.get('package')
        bond_period = request.POST.get('bond')
        dateofdrive = request.POST.get('dateofdrive')
        duplicate_drive = models.CampusDrive.objects.filter(
            company=models.Company.objects.get(pk=company), package=package,
            drive_year=drive_year, bond_period=bond_period,
        ).first()
        if duplicate_drive:
            context_dict["message"] = 'Campus Drive already exists.'
            duplicate_drive.soft_delete=False
            duplicate_drive.save()
            return render(request, "AddCampusDrive.html", context_dict)
        try:
            drive = models.CampusDrive(
                company = models.Company.objects.get(pk=company),
                drive_year = drive_year,
                bond_period = bond_period,
                package = package,
                dateofdrive = dateofdrive,
            )
            drive.save()
            history = models.History(
                user=emp,
                activity="added drive of" + str(company) + 
                    "for the year" + str(drive_year) + ".\n",
                activity_type="add campus drive."
            )
            history.save()
            context_dict["message"] = 'Successfully added new Campus Drive.'
            context_dict["success"] = True
        except Exception as e:
            context_dict["message"] = str(e)
            context_dict["success"] = False
            print(e)
    return render(request, "AddCampusDrive.html", context_dict)


@login_required
def edit_campus_drive(request, campusdrive_id):

    """
    Method to edit the campus drive of company year wise.
    """

    context_dict = {}
    emp = models.Employee.objects.get(user=request.user)
    if not emp.placement_permit:
        raise Http404
    drive = models.CampusDrive.objects.filter(
        pk=campusdrive_id, soft_delete=False
    ).first()
    if not drive:
        raise Http404
    context_dict = {
        'campusdrive_id': campusdrive_id,
        "all_companies": context_helper.company_select()
    }
    if request.method == 'POST':
        update_fields = []
        activity = ''
        company = request.POST.get('company_picker')
        drive_year = request.POST.get('driveyear')
        package = request.POST.get('package')
        bond_period = request.POST.get('bond')
        dateofdrive = request.POST.get('dateofdrive')
        try:
            if str(drive.company.pk) != str(company):
                try:
                    old_company = drive.company
                    drive.company = models.Company.objects.get(pk=company)
                    drive.save()
                except Exception as e:
                    drive.soft_delete = True
                    drive.company = old_company
                    drive.save()
                    drive = models.CampusDrive.objects.filter(
                        soft_delete=True, drive_year=drive.drive_year,
                        package=drive.package, bond_period=drive.bond_period, 
                        company__pk=company
                    ).first()
                    drive.soft_delete = False
                    drive.company = models.Company.objects.get(pk=company)
                    drive.save(update_fields=['soft_delete', 'company'])
                update_fields.append('company')
                activity += 'Changed company to ' + str(company) + '.\n'
            if drive.package != package:
                drive.package = package
                update_fields.append('package')
                activity += 'Changed name to '+ str(package) +'.\n'
            if drive.drive_year != drive_year:
                drive.drive_year = drive_year
                update_fields.append('drive_year')
                activity += 'Changed drive year to' + str(drive_year) + '.\n'
            if drive.bond_period != bond_period:
                drive.bond_period = bond_period
                update_fields.append('bond_period')
                activity += 'Changed bond period to' + str(bond_period) + '.\n'
            if drive.dateofdrive != dateofdrive:
                drive.dateofdrive = dateofdrive
                update_fields.append('dateofdrive')
                activity += 'Changed date of drive to' + str(dateofdrive) + '.\n'
            drive.save(update_fields=update_fields)
            history = models.History(
                user=emp,
                activity=activity,
                activity_type='Edit campus Drive'
            )
            history.save()
            context_dict["message"] = 'Successfully Edited Campus Drive.'
            context_dict["success"] = True
        except Exception as e:
            context_dict["message"] = str(e)
            context_dict["success"] = False
            print(e)
    context_dict.update(context_helper.get_drive_info(drive))
    for i in context_dict['company']:
        try: del context_dict['all_companies'][i]
        except: pass
    if context_dict.get('success', False):
        return HttpResponseRedirect('/view-drives')
    return render(
        request, "EditCampusDrive.html", context_dict
    )


@login_required
def view_campus_drive(request):

    """
    to view the details of all students placed in the tabular form.
    """

    context_dict = {
        'title': 'All Campus Drives'
    }
    return render(
        request,
        'ViewCampusDrive.html',
        context_dict
    )
    # celery_test_task.delay(5,5)


@login_required
def delete_campus_drive(request, campusdrive_id):

    """
    view to delete placement by taking placement id as argument.
    """

    emp = models.Employee.objects.get(user=request.user)
    if not emp.placement_permit:
        raise Http404
    drive = models.CampusDrive.objects.filter(
        pk=campusdrive_id, soft_delete=False
    ).first()
    if not drive:
        raise Http404
    drive.soft_delete = True
    activity = 'Deleted Campus Drive' + str(drive) + '.\n'
    drive.save(update_fields=['soft_delete'])
    history = models.History(
                user=emp,
                activity=activity,
                activity_type="Deleted Campus Drive"
            )
    history.save()
    return HttpResponseRedirect('/view-drives')


def _search_result(request):
    context_dict = {}
    #if not student:
    #    raise Http404
    if request.method == 'GET':
        roll = request.GET.get('rollno')
    #roll = 100
        #if (student.roll_no == roll):
    student = models.Student.objects.filter(
        soft_delete=False, roll_no=roll
    )
    student_serial = serializers.serialize('json', student)
    #serializer = studentSerializer(student)
    #context_dict = {student}
    #if roll is None:
    #   context_dict.update('Not assigned')
    return JsonResponse(student_serial, safe=False)
    #return HttpResponse(json.dumps(data, separators=(',' , ':')), content_type='application/json')


def _search_result_(request):
    student = models.Student.objects.all().values(
        'name', 'dob', 'course', 'roll_no'
    ).filter(roll_no=611) #can add _list with values to display only values
    student_list = list(student)      #used to serialize data
    return JsonResponse(student_list, safe=False)
    #return JsonResponse({'student':list(student)}, safe=False)   another way to return


def search(request):
    # roll = 101
    context_dict = {}
    if request.method == 'GET':
        roll = request.GET.get('roll')
    student = models.Student.objects.filter(
        soft_delete=False, roll_no=roll,
    ).first()
    if not student:
        raise Http404
    context_dict.update(context_helper.get_student_info(student))
    return render(request, "search.html", context_dict)


def bar_chart(request):
    
    """
    Anaylitics for package
    """

    pname = models.Placements.objects.filter(
        soft_delete=False
    ).values_list('company__name', flat=True)
    package = models.Placements.objects.filter(
        soft_delete=False
    ).values_list('package', flat=True)
    print (pname)
    print (package)
    context_dict = {
        'ylabel': 'Package',
        'datasets': [
            {
                'label': 'Companies',
                'dataset': package
            },
            # {
            #     'label': 'X2',
            #     'dataset': [1,2,3,4]
            # }
        ],
        'labels': pname
    }
    return render(request, "bcharts.html", context_dict)


def pie_chart(request):

    """
    Anaylitics fot he student and company
    """

    pdata = models.Placements.objects.filter(
        soft_delete=False
    ).values_list('company__name', flat=True)
    ps = models.Placements.objects.filter(
        soft_delete=False
    ).values_list('student__id', flat=True)
    dataset = {}
    for i in range(len(pdata)):
        dataset[pdata[i]] = ps[i]
    context_dict = {
        'ylabel': 'Companies',
        'dataset': dataset
    }
    return render(request, "pcharts.html", context_dict)


def test_search(request):
    context_dict = {}
    param = request.GET.get('search_param')
    if param:
        results = models.Student.objects.filter(
            Q(roll_no__icontains=param)|Q(name__icontains=param)
        )[:20]
        context_dict['rows'] = results
    return render(request, 'test_search.html', context_dict)


def year_ajax(request):
    if request.method=="POST":
        print(request.POST)
        year = request.POST.get("year")
        companies = models.CampusDrive.objects.filter(drive_year=year).values(
            'company', 'company__name'
        ).distinct()
        if 'csrfmiddlewaretoken' not in request.POST:
            return render(request, 'foo.html', {'companies': companies})
    return render(request, 'year_ajax_test.html', {})
