from blog.models import Post
from django.contrib.sessions.backends.db import SessionStore

from importlib import import_module
from django.conf import settings

SessionStore = import_module(settings.SESSION_ENGINE).SessionStore



class CustomLikeValidators:

    def __init__(self, current_like=0, related_post=None, request=None):
        self.related_post = str(related_post)
        self.request = request
        self.session_key_from_request = self.request.session.session_key

        try:
            self.current_like = int(current_like)
        except:
            return None

    
    def like_string_validator(self):
        if not type(self.current_like) is int:
            return False

        return self.current_like

    def session_exists_check(self):
        
        if 'liked_post_slug' in self.request.session:
            return True

        else:
            s = SessionStore(session_key=self.session_key_from_request)
            s['liked_post_slug'] = [self.related_post]
            s.save()
            self.request.session['liked_post_slug'] = [self.related_post]

            return False

    def like_was_added_before(self, checked_session_instance):
        if checked_session_instance['liked_post_slug'].count(self.related_post):

            checked_session_instance['liked_post_slug'].remove(self.related_post)
            self.request.session['liked_post_slug'].remove(self.related_post)
            
            self.request.session.modified = True
            checked_session_instance.save()
            
            return True


    def session_undefined(self, checked_session_instance):
        try:
            checked_session_instance['liked_post_slug'].append(self.related_post)
            checked_session_instance.save()

            self.request.session['liked_post_slug'].append(self.related_post)
            self.request.session.modified = True
            
            return True

        except:
            return None


    def likes_add_ident(self):
        self.request.session.set_test_cookie()

        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()

            if self.session_exists_check():
                try:
                    s = SessionStore(session_key=self.session_key_from_request)

                    if self.like_was_added_before(s):
                        return self.current_like - 1

                    else:
                        if self.session_undefined(s):
                            return self.current_like + 1

                        # return None
                except:
                    return None

            else:
                return self.current_like + 1

    def like_checked_for_user(self, only_check=False):
        checked_session_instance = SessionStore(session_key=self.session_key_from_request)
        
        if checked_session_instance['liked_post_slug'].count(self.related_post):
            if only_check:
                return True
            return None
