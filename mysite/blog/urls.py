from django.urls import path
from .views import *
from .change_theme import ChangeTheme


urlpatterns = [
	path('', PostList.as_view(), name="home_blog_page"),
	path('change_language/', ChangeLG.as_view(), name="change_lang_ajax_url"),
	path('change_theme/', ChangeTheme.as_view(), name="change_theme_url"), #change theme url
	path('search/', CustomSearch.as_view(), name='search_func_url'),
	path('about/', AboutBlog.as_view(), name="about_blog_url"),
	path('privacy_policy/', PrivacyPolicy.as_view(), name="privacy_policy_url"),
	path('post/create/', PostCreate.as_view(), name="post_create_url"),

	path('post/<str:slug>/', PostPage.as_view(), name="post_page_url"), #Post page url
	
	path('post/<str:slug>/update/', PostUpdate.as_view(), name="post_update_url"),
	path('post/<str:slug>/delete/', PostDelete.as_view(), name="post_delete_url"),
	path('tags/', tags_list, name="tags_list_url"),
	path('tag/create/', TagCreate.as_view(), name="tag_create_url"),
	path('tag/<str:slug>/', TagDetail.as_view(), name="tag_detail_url"),
	path('tag/<str:slug>/delete/', TagDelete.as_view(), name="tag_delete_url"),
]

