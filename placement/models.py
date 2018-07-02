from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class TimeStampModel(models.Model):

    """ 
    Abstract class for all models to store created, updated and
    deleted informarion (Time Manage).
    """

    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_at = models.DateTimeField(auto_now=True, auto_now_add=False)
    soft_delete = models.BooleanField(default=False)

    class Meta:
        abstract = True


class Person(TimeStampModel):

    """
    Abstract class used for teachers and students basic information.
    """

    BLOOD_TYPE = (
        ('A+', 'A-Positive'),
        ('A-', 'A-Negative'),
        ('B+', 'B-Positive'),
        ('B-', 'B-Negative'),
        ('O+', 'O-Positive'),
        ('O-', 'O-Negative'),
        ('AB+', 'AB-Positive'),
        ('AB-', 'AB-Negative'),
    )

    GENDER_TYPE = (
        ('M', 'Male'),
        ('F', 'Female'),
    )

    name = models.CharField(max_length=50, db_index=True)
    gender = models.CharField(max_length=2, null=False, choices=GENDER_TYPE, blank=True)
    dob = models.DateField(null=True, blank=True)
    phone = models.BigIntegerField()
    curr_address = models.TextField()
    perm_address = models.TextField(null=True)
    address_flag = models.BooleanField(default=False)
    photo = models.ImageField(upload_to='profile-images', null=True)
    blood_group = models.CharField(max_length=3, null=True, choices=BLOOD_TYPE, blank=True)
    celery_schedule = models.IntegerField(default=0)

    class Meta:
        abstract = True


class Course(TimeStampModel):

    """
    Course details.
    """

    name = models.CharField(max_length=100, null=False, db_index=True, unique=True)
    abbr = models.CharField(max_length=20, db_index=True, unique=True)
    duration = models.IntegerField()

    def __str__(self):
        return str(self.name)

    def __unicode__(self):
        return unicode(self.name)


class Student(Person):

    """
    Student information model.
    """

    GUARDIAN_TYPE = (
        ('F', 'Father'),
        ('M', 'Mother'),
        ('G', 'Guradian')
    )

    roll_no = models.SlugField()
    guardian_name = models.CharField(max_length=50)
    guardian_type = models.CharField(max_length=1, choices=GUARDIAN_TYPE)
    guardian_phone = models.CharField(max_length=15)
    course = models.ForeignKey(Course, db_index=True, on_delete=models.CASCADE)
    batch = models.IntegerField()
    email = models.CharField(max_length=100, null=False, unique=True)

    def __str__(self):
        return str(str(self.roll_no) + '-' + self.name)

    def __unicode__(self):
        return unicode(str(self.roll_no) + '-' + self.name)


class Employee(Person):

    """
    Employee details and their rights to portal.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    e_id = models.CharField(max_length=20, db_index=True, unique=True)
    student_permit = models.BooleanField(default=False)
    company_permit = models.BooleanField(default=False)
    placement_permit = models.BooleanField(default=False)

    def __str__(self):
        return str(self.e_id + '-' + self.name)

    def __unicode__(self):
        return unicode(self.e_id + '-' + self.name)


class Company(TimeStampModel):

    """
    Company details.
    """

    name = models.CharField(max_length=200, db_index=True)
    address = models.TextField()
    phone = models.BigIntegerField()
    contact_person = models.CharField(max_length=100, db_index=True)
    email = models.CharField(max_length=100)

    def __str__(self):
        return str(self.name + '-' + str(self.contact_person))

    def __unicode__(self):
        return unicode(self.name + '-' + str(self.contact_person))


class CampusDrive(TimeStampModel):

    """
    Campus drive details of every company year by year.
    """

    company = models.ForeignKey(Company, db_index=True, on_delete=models.CASCADE)
    drive_year = models.IntegerField()
    package = models.CharField(max_length=10, db_index=True)
    bond_period = models.IntegerField()
    dateofdrive = models.DateField(null=False, blank=True)

    def __str__(self):
        return str(str(self.company) + '-' + str(self.drive_year))

    def __unicode__(self):
        return str(str(self.company) + '-' + str(self.drive_year))


class Placements(TimeStampModel):

    """
    Placement details of student placed in companies.
    """

    student = models.ForeignKey(Student, db_index=True, on_delete=models.CASCADE)
    campus_drive = models.ForeignKey(CampusDrive, on_delete=models.CASCADE)
    dateofjoining = models.DateField(null=True, blank=True)

    def __str__(self):
        return str(str(self.student) + '-' + str(self.campus_drive))

    def __unicode__(self):
        return unicode(str(self.student) + '-' + str(self.campus_drive))

    class Meta:
        unique_together = ["student", "campus_drive"]


class History(TimeStampModel):

    """
    Record of changes that is made by the user.
    """

    user = models.ForeignKey(Employee, on_delete=models.CASCADE)
    activity = models.TextField(null=True, blank=True)
    activity_type = models.CharField(max_length=50)

    def __str__(self):
        return str(str(self.user) + '-' + self.activity_type)

    def __unicode__(self):
        return unicode(str(self.user) + '-' + self.activity_type)


class PasswordReset(TimeStampModel):

    """
    Password reset model.
    """

    user = models.ForeignKey(Employee, on_delete=models.CASCADE)
    password_request_created_at = models.DateTimeField(auto_now_add=True)
    token = models.TextField()
    token_consumed = models.BooleanField(default=False)

    def __str__(self):
        return str(str(self.user) + '-' + str(self.token_consumed))

    def __unicode__(self):
        return str(str(self.user) + '-' + str(self.token_consumed))
