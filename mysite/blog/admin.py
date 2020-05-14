from django.contrib import admin
from django import forms
from .models import Post 
from .models import Comment
from .models import Tag

from ckeditor_uploader.widgets import CKEditorUploadingWidget
from ckeditor.widgets import CKEditorWidget

class PostAdminForm(forms.ModelForm):
    body = forms.CharField(widget=CKEditorUploadingWidget())

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

#class PostAdmin(admin.ModelAdmin):
    