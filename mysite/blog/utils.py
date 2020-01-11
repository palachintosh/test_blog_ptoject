from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.shortcuts import redirect
from django.core.paginator import Paginator
from django.core.paginator import PageNotAnInteger
from django.utils.safestring import mark_safe
from .models import *
import time


class ObjectDetailMixine:
    model = None
    template = None
    comment_model = Comment
    form_model = None

    def get(self, request, slug):
        form = self.form_model
        #get_comment = self.comment_model.objects.all()
        #get_post = self.model.objects.get(slug__iexact=slug)
        #get_comment = self.model.objects.get(slug__iexact=slug)

        

        get_object = get_object_or_404(self.model, slug__iexact=slug)
        get_comment = self.comment_model.objects.filter(comments=get_object)


        return render(request, self.template, context={
                                self.model.__name__.lower(): get_object,
                                'admin_obj': get_object,
                                'comment': get_comment,
                                'comment_form': form
                                })
    def post(self, request, slug):
        if request.POST:
            print("slug: ", slug)
            bound_form = self.form_model(request.POST)
            #get_post = get_object_or_404(self.model, slug__iexact=slug)

            if bound_form.is_valid():
                add_comment = bound_form.save(commit=False)
                add_comment.comments = self.model.objects.get(slug__iexact=slug)
                
                bound_form.save()
                #add_comment = self.comment_model.objects.all()
                #return redirect("post_page_url", permanent=True, args=[slug])
                return redirect(reverse("post_page_url", kwargs={'slug': slug}))

class TagDetailMixine:
    model = None
    template = None
    
    def get(self, request, slug):
        get_tag = self.model.objects.get(slug__iexact=slug)
        return render(request, self.template, context={
                                self.model.__name__.lower(): get_tag,
                                'admin_tag_obj': get_tag,
                                })


class ObjectCreateMixine:

    form_model = None
    template = None

    def get(self, request):
        form = self.form_model
        return render(request, self.template, context={"post_form": form})

    def post(self, request):
        bound_form = self.form_model(request.POST)

        if bound_form.is_valid():
            new_object = bound_form.save()

            return redirect(new_object)
        return render(request, self.template, context={"form": bound_form})

class ObjectUpdateMixine:

    model = None
    model_form = None
    template = None

    def get(self, request, slug):
        obj = self.model.objects.get(slug__iexact=slug)
        bound_form = self.model_form(instance=obj)

        return render(request, self.template, context={'form': bound_form, self.model.__name__.lower(): obj})


    def post(self, request, slug):
        obj = self.model.objects.get(slug__iexact=slug)
        print('this is', obj)
        bound_form = self.model_form(request.POST, instance=obj)

        if bound_form.is_valid():
            new_obj = bound_form.save()
            return redirect(new_obj)

        return render(request, self.template, context={'form': bound_form, self.model.__name__.lower(): obj})

class ObjectDeleteMixin:
    model = None
    template = None
    red_template = None

    def get(self, request, slug):
        obj = self.model.objects.get(slug__iexact=slug)
        return render(request, self.template, context={'tag': obj})

    def post(self, request, slug):
        obj = self.model.objects.get(slug__iexact=slug)
        obj.delete()
        counter = 0
        while counter < 3:
            counter += 1
            time.sleep(1)
        return redirect(reverse(self.red_template))

class PaginatorObjectsMixine:
    model = None

    def pag_page_mixine(self, request, posts):

        #posts = self.model.objects.all()
        paginator = Paginator(posts, 5)
        pages = request.GET.get('page')
        pag_range = paginator.page_range

        pag_range_count_str = 0

        for i in pag_range:
            pag_range_count_str += 1

        #print(str(pag_range_count_str))

        #first = True
        #print(pag_range)
        try:
            count_posts = paginator.page(pages)
        except PageNotAnInteger:
            count_posts = paginator.page(1)
        
        first_post = str(Post.objects.order_by('id').last())

        print(first_post)
        print(type(pag_range))
        print(type(count_posts))
        return render(request,
                      'blog/index.html',
                      context={
                          'post_count': count_posts,
                          'pag_range': pag_range,
                          'first_post': first_post,
                      })
