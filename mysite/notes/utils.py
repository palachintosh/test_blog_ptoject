from django.core.paginator import Paginator
from django.core.paginator import PageNotAnInteger


class PaginatorObjectsMixine:
    model = None

    def pag_page_mixine(self, request, notes):

        paginator = Paginator(notes, 15)
        pages = request.GET.get('page')
        pag_range = paginator.page_range

        pag_range_count_str = 0

        for i in pag_range:
            pag_range_count_str += 1

        try:
            count_notes = paginator.page(pages)
        except PageNotAnInteger:
            count_notes = paginator.page(1)

        data = { 'pag_notes': count_notes,
                'pag_range': pag_range }

        print(data)
        return data
                          