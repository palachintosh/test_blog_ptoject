from django.contrib import admin
from django import forms
from .models import Note

from ckeditor_uploader.widgets import CKEditorUploadingWidget
from ckeditor.widgets import CKEditorWidget


# Register your models here.


class NoteAdminForm(forms.ModelForm):
    body = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = Note
        fields = "__all__"


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    form = NoteAdminForm