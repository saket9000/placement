from .models import Student


def add_celery(num1, num2):
    return num1 + num2


def add_schedule():
    stud = Student.objects.all()
    for i in stud:
        i.celery_schedule += 1
        i.save()
    print ("ADDING")