from django import forms
from .models import BorrowTransaction


class ConfirmTicketForm(forms.ModelForm):

    class Meta:
        model = BorrowTransaction
        fields = [] 