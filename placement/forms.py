from django import forms
from placement.tasks import celery_test_task


class AddForm(forms.Form):
    num2 = forms.IntegerField(label="num2")
    num1 = forms.IntegerField(label="num1")

    def save(self):
        celery_test_task.delay(
            self.cleaned_data['num1'], self.cleaned_data['num2'])
