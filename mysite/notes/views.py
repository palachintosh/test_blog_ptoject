from django.shortcuts import render
from django.views.generic import View
from django.utils import timezone
from .models import Note
from .utils import PaginatorObjectsMixine

# Create your views here.

class Notes(PaginatorObjectsMixine, View):
    model = Note

    def get(self, request):
        notes = self.model.objects.filter(date_pub__lte=timezone.now()).order_by('-date_pub')
        pagination_notes = PaginatorObjectsMixine.pag_page_mixine(self.model, request, notes)

        return render(request, "notes/notes.html", context=pagination_notes)