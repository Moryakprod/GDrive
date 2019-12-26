# from django import forms
# from django.forms import formset_factory
#
#
#
#
# class FileList(forms.Form):
#     id = forms.CharField(max_length=200)
#     name = forms.CharField(max_length=200)
#     type = forms.CharField(max_length=200)
#
#
# FileListSet = formset_factory(FileList)
#
#
# SOME_CHOICES = [
#     (1, '111'),
#     (2, '222'),
#     (3, '333'),
#     (4, '444')
# ]
#
# class MyForm(forms.Form):
#     my_field = forms.MultipleChoiceField(choices=id, widget=forms.CheckboxSelectMultiple())
#
#     def clean_my_field(self):
#         if len(self.cleaned_data['files']) > 3:
#             raise forms.ValidationError('Select no more than 3.')
#         return self.cleaned_data['files']
#
