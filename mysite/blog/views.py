from django.shortcuts import render
from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.utils import timezone
from .models import Post
from .models import Tag
from .forms import TagForm
from .forms import PostForm
from .forms import FilterForm
from .forms import CommentForm

from django.views.generic import View
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.core.paginator import PageNotAnInteger
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.template import RequestContext
from .utils import *
import time

# Create your views here.


# def post_list(request):
# 	posts = Post.objects.all()

	
# 	search_q = request.GET.get('search', '')
# 	if search_q:
# 		posts = Post.objects.filter(Q(title__icontains=search_q) | Q(body__icontains=search_q))
# 	else:
# 		posts = Post.objects.all()

# 	paginator = Paginator(posts, 5)
# 	pages = request.GET.get('page')
# 	pag_range = paginator.page_range
# 	try:
# 		count_posts = paginator.page(pages)
# 	except PageNotAnInteger:
# 		count_posts = paginator.page(1)

# 	return render(request, 'blog/index.html', context={'post_count': count_posts, 'pag_range': pag_range})



class Variables:
	#model = None
	def post_filter_list(self):
		post_filter = self.objects.filter(date_pub__lte=timezone.now()).order_by('-date_pub')
		return(post_filter)



class CustomSearch(PaginatorObjectsMixine, View):
	model = Post
	def get(self, request):
		search_q = request.GET.get('search', '')

		if search_q:
			posts = self.model.objects.filter(Q(title__icontains=search_q) | Q(body__icontains=search_q))
		else:
			posts = Variables.post_filter_list(self.model)
			#posts = self.model.objects.filter(date_pub__lte=timezone.now()).order_by('-date_pub')
		
		return PaginatorObjectsMixine.pag_page_mixine(None, request, posts)


	# def get(self, request):
	# 	search_q = request.GET.get('search', '')
	# 	if search_q:
	# 		posts = self.model.objects.filter(Q(title__icontains=search_q) | Q(body__icontains=search_q))
	# 	else:
	# 		posts = self.model.objects.all()
	# 	return render(request, 'blog/index.html', context={'posts': posts})


class AboutBlog(View):
	def get(self, request):
		return render(request, 'blog/about_blog.html')


class PostList(PaginatorObjectsMixine, View):
	model = Post
	
	def get(self, request):
		posts = Variables.post_filter_list(self.model)
		return PaginatorObjectsMixine.pag_page_mixine(self.model, request, posts)


class FilterFormView(View):
	model_form = FilterForm
	
	def get(self, request):
		filter_form = self.model_form
		test = 'test str'
		return render(request, 'blog/filter_form_include.html', context={'filter_form': filter_form, 'test': test})

class PostPage(ObjectDetailMixine, View):
	form_model = CommentForm
	model = Post
	template = 'blog/post.html'



def tags_list(request):
	tags = Tag.objects.all()
	admin = True
	return render(request, 'blog/tags_list.html', context={'tags': tags, 'admin_tag_obj': admin})



class TagDetail(TagDetailMixine, View):
	model = Tag
	template = 'blog/tag_detail.html'


class TagCreate(LoginRequiredMixin, ObjectCreateMixine, View):
	form_model = TagForm
	template = 'blog/tag_create.html'
	raise_exception = True
	


class PostCreate(LoginRequiredMixin, ObjectCreateMixine, View):
	form_model = PostForm
	template = 'blog/post_create.html'
	raise_exception = True



class PostUpdate(LoginRequiredMixin, ObjectUpdateMixine, View):
	model = Post
	model_form = PostForm
	template = 'blog/post_update.html'
	raise_exception = True



class TagDelete(LoginRequiredMixin, ObjectDeleteMixin, View):
	model = Tag
	template = 'blog/tag_delete.html'
	red_template = 'home_blog_page'
	raise_exception = True


class PostDelete(LoginRequiredMixin, ObjectDeleteMixin, View):
	model = Post
	template = 'blog/post_delete.html'
	red_template = 'home_blog_page'
	raise_exception = True


def e_handler404(request, exception):
	print("we're here")
	context = RequestContext(request)
	print(context)
	response = render_to_response('404.html', context={"context": context})
	response.status_code = 404
	return response

def e_handler500(request):
	context = RequestContext(request)
	print("my", context)
	response = render_to_response('500.html', context={"context": context})
	response.status_code = 500
	return response