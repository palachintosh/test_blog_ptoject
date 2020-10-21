from django.views.generic import View
from blog.models import Post
from django.http import JsonResponse
from .likes_validator import CustomLikeValidators


from django.http import HttpResponseBadRequest


# Create your views here.


class LikeResponse(View):
    model = Post

    def post(self, request):

        if request.POST:
            get_post = self.model.objects.get(slug=request.POST.get('slug'))
            get_like_number = int(request.POST.get('like_index'))

            cl = CustomLikeValidators(current_like=get_like_number,
                                      related_post=request.POST.get('slug'),
                                      request=request)
            cl_is_valid = cl.likes_add_ident()

            if cl_is_valid:
                get_post.like = cl_is_valid
                get_post.save()

                remove_like = False

                if get_like_number > get_post.like:
                    remove_like = True

                data = {
                    'remove_like': remove_like,
                    'like_updated': get_post.like,
                }

            else:
                return HttpResponseBadRequest(
                    "Value invalid! Restart page and try again!")

            return JsonResponse(data)


class LikeCheck(View):
    def get(self, request):
        ses_check = CustomLikeValidators(related_post=request.GET.get('slug'), request=request)
        like_checked = ses_check.like_checked_for_user(only_check=True)

        data = {
            'like_checked': like_checked,
        }

        return JsonResponse(data)