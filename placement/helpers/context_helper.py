import os
from placement import models
from django.conf import settings


def course_helper():
    courses = models.Course.objects.filter(soft_delete=False)
    return {i.pk: i.name for i in courses}


def blood_group_helper():
    blood_groups = [
        ('A+', 'A-Positive'),
        ('A-', 'A-Negative'),
        ('B+', 'B-Positive'),
        ('B-', 'B-Negative'),
        ('O+', 'O-Positive'),
        ('O-', 'O-Negative'),
        ('AB+', 'AB-Positive'),
        ('AB-', 'AB-Negative'),
    ]
    return blood_groups


def guardian_type_helper():
    guardian_type = [
        ('F', 'Father'),
        ('M', 'Mother'),
        ('G', 'Guradian'),
    ]
    return guardian_type


def gender_helper():
    gender_type =[
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    return gender_type

def get_student_info(student):

    blood_groups = blood_group_helper()
    guardians = guardian_type_helper()
    genders = gender_helper()
    info = {
        'sname': student.name,
        'curradd': student.curr_address,
        'permadd': student.perm_address,
        'roll': student.roll_no,
        'gender_type': [i for i in genders if student.gender in i],
        'course': {student.course.pk: student.course.name},
        'phone': student.phone,
        'gname': student.guardian_name,
        'guardian_phone': student.guardian_phone,
        'batch': student.batch,
        'email': student.email,
        'blood_group': [i for i in blood_groups if student.blood_group in i],
        'dob': student.dob,
        'guardian_type': [i for i in guardians if student.guardian_type in i],
        'address_flag': student.address_flag,
        'photo': os.path.join(settings.MEDIA_URL, student.photo.name) if student.photo else None,
    }
    return info


def get_company_info(company):
   
    info = {
        'c_name': company.name,
        'c_add': company.address,
        'c_phone': company.phone,
        'c_email': company.email,
        'hr_name': company.contact_person
    }
    return info


def company_select():
    company = models.Company.objects.filter(soft_delete=False)
    return {i.pk: i.name for i in company}


def drive_year_info():
    dyears = models.CampusDrive.objects.filter(soft_delete=False)
    return dyears


def drives_info():
    drive = models.CampusDrive.objects.filter(soft_delete=False)
    return {i.pk: i.company for i in drive}


def get_placement_info(placement):
    info = {
        'sname': placement.student.name,
        'rollno': placement.student.roll_no,
        'batch': placement.student.batch,
        'drive': {placement.campus_drive.pk: placement.campus_drive.company},
        'doj': placement.dateofjoining,
    }
    return info

def get_emp_info(employee):
    
    blood_groups = blood_group_helper()
    genders = gender_helper()
    info = {
        'ename': employee.name,
        'dob': employee.dob,
        'gender': [i for i in genders if employee.gender in i],
        'phone': employee.phone,
        'address': employee.curr_address,
        'emp_id': employee.e_id,
        'bgroup': [i for i in blood_groups if employee.blood_group in i],
        'photo': os.path.join(settings.MEDIA_URL, employee.photo.name) if employee.photo else None,
    }
    return info

def get_drive_info(drive):
    info = {
        'company' : {drive.company.pk: drive.company.name},
        'package' : drive.package,
        'bond_period' : drive.bond_period,
        'dateofdrive' : drive.dateofdrive,
        'drive_year' : drive.drive_year,
    }
    return info
