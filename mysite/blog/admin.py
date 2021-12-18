from django.contrib import admin
from django import forms
from .models import Post
from .models import Comment
from .models import Tag
from .models import PrivacyPolicy

from ckeditor_uploader.widgets import CKEditorUploadingWidget
from ckeditor.widgets import CKEditorWidget

class PostAdminForm(forms.ModelForm):
    body = forms.CharField(widget=CKEditorUploadingWidget())
    description = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = Post
        fields = "__all__"

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm


# Register your models here.

# admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Tag)

class PrivacyPolicyForm(forms.ModelForm):
    privacy = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = PrivacyPolicy
        fields = "__all__"

@admin.register(PrivacyPolicy)
class PrivacyPolicyAdmin(admin.ModelAdmin):
    form = PrivacyPolicyForm

# admin.site.register(PrivacyPolicy)

#class PostAdmin(admin.ModelAdmin):
    