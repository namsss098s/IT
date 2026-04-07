from django import forms
from .models import BorrowTransaction


class BorrowForm(forms.ModelForm):
    class Meta:
        model = BorrowTransaction
        fields = ['book', 'member', 'due_date']