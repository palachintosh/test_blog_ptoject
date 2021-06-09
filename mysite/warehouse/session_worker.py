# Session Mixins
# Ever mixin gets request in parameter and work with it


class SessionMixin:
    def __init__(self, request):
        self.request = request

    def session_update_var(self):
        success_update = False

        if self.request.session.get('success_update'):
            success_update = True
            self.request.session['success_update'] = False

        return success_update