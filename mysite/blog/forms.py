from django import forms
from .models import Tag
from .models import Post
from .models import Comment
from django.core.exceptions import ValidationError
from .models import gen_slug


# Post create model

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'slug', 'body', 'tags']

        widgets = {
            'title': forms.TextInput(attrs={"class": "form-control"}),
            'slug': forms.TextInput(attrs={"class": "form-control"}),
            'body': forms.Textarea(attrs={"class": "form-control"}),
            'tags': forms.SelectMultiple(attrs={"class": "form-control"}),
            #'tag_title': forms.TextInput(attrs={"class": "form-control"}),
        }
    

    def clean_slug(self):
        new_slug = self.cleaned_data['slug'].lower()
        
        if new_slug == 'create':
            raise ValidationError('You can not make a "Create" slug!')
        if new_slug == '':
            ps = self.cleaned_data['title'].lower()
            new_slug = gen_slug(ps)
            return new_slug
        return new_slug

#Tag create model

class TagForm(forms.ModelForm):
    # title = forms.CharField(max_length=50)
    # slug = forms.CharField(max_length=50)

    # title.widget.attrs.update({'class': 'form-control'})
    # slug.widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = Tag
        fields = ['tag_title', 'slug']

        widgets = {
            'tag_title': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
        }


    def clean_slug(self):
        new_slug = self.cleaned_data['slug'].lower()

        if new_slug == 'create':
            raise ValidationError('You can not make a "Create" tag!')

        if Tag.objects.filter(slug__iexact=new_slug).count():
            raise ValidationError('We have "{}" slug already'.format(new_slug))
        return new_slug


class FilterForm(forms.ModelForm):
    class Meta:
        fields = ['tags', 'date', 'user']

        widgets = {
            'tags': forms.TextInput(attrs={'class': 'form-control'}),
            'date': forms.TextInput(attrs={'class': 'form-control'}),
            'user': forms.TextInput(attrs={'class': 'form-control'})
        }
    
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'comment_body']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'comment_body': forms.Textarea(attrs={'class': 'form-control form-size'})
        }



    # def save(self):
    #     new_tag = Tag.objects.create(
    #         tag_title=self.cleaned_data['title'], 
    #         slug=self.cleaned_data['slug']
    #     )
    #     return new_tag
