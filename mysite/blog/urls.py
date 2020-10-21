from django.urls import path
from .views import *
#from django.conf.urls import handler404, handler500


urlpatterns = [
	path('', PostList.as_view(), name="home_blog_page"),
	path('change_language/', ChangeLG.as_view(), name="change_lang_ajax_url"),
	path('search/', CustomSearch.as_view(), name='search_func_url'),
	path('about/', AboutBlog.as_view(), name="about_blog_url"),
	path('post/create/', PostCreate.as_view(), name="post_create_url"),

	path('post/<str:slug>/', PostPage.as_view(), name="post_page_url"), #Post page url
	
	path('post/<str:slug>/update/', PostUpdate.as_view(), name="post_update_url"),
	path('post/<str:slug>/delete/', PostDelete.as_view(), name="post_delete_url"),
	# path('post/<str:slug>/', post_page, name="post_page_url")
	path('tags/', tags_list, name="tags_list_url"),
	path('tag/create/', TagCreate.as_view(), name="tag_create_url"),
	path('tag/<str:slug>/', TagDetail.as_view(), name="tag_detail_url"),
	path('tag/<str:slug>/delete/', TagDelete.as_view(), name="tag_delete_url"),
	#path('', FilterFormView.as_view(), name="filter_form_include"),
]

#handler404 = e_handler404