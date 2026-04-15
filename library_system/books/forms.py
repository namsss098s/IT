from django import forms
from .models import Book, Edition


# 📚 BOOK FORM
class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'title',
            'category',
            'description',
            'publisher',
            'price',
            'authors'
        ]

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'publisher': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'authors': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }


# 📦 EDITION FORM (dùng riêng khi cần)
class EditionForm(forms.ModelForm):
    class Meta:
        model = Edition
        fields = [
            'edition_number',
            'quantity'
        ]

        widgets = {
            'edition_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']

        if quantity < 0:
            raise forms.ValidationError("Quantity cannot be negative")

        return quantity


# 🔥 UPDATE STOCK FORM (QUAN TRỌNG cho admin/custom view)
class UpdateStockForm(forms.Form):
    edition_id = forms.IntegerField(widget=forms.HiddenInput())
    new_quantity = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )