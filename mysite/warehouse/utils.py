from django.utils.text import slugify
from django.core.exceptions import ValidationError
from time import CLOCK_THREAD_CPUTIME_ID, time
from django.shortcuts import render, redirect
from django.utils import timezone

def gen_slug(s):
    #new_slug = slugify(s, allow_unicode=True)
    print(s)
    s.lower() 
    format_string = slugify(s, allow_unicode=True)
    s_translate = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'e',
        'ж': 'j', 'з': 'z', 'и': 'i', 'й': 'j', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'c', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ъ': '',
        'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya', '0': '0', '1': '1', '2': '2',
        '3': '3', '4': '4', '5': '5', '6': '6', '7': '7', '8': '8', '9': '9'
        }

    s_encode = []

    for i in format_string:
        try:
            if i == '-' or i == '_':
                s_encode.append(i)
            s_encode.append(s_translate.get(i, i))
                #s_encode.append(s_translate[i])
        except:
            raise ValidationError("Slug can't be generated!")
    new_slug = ''.join(map(str, s_encode))
    print(s_encode, new_slug)
    return new_slug + '-' + str(int(time()))


class ObjectCreateMixin:

    model_form = None
    model = None
    template = None

    def get(self, request):
        main_object = self.model.objects.filter(date_pub__lte=timezone.now()).order_by('-date_pub')
        form = self.model_form
        
        return render(request, self.template, context={
            "object_create_form": form,
            self.model.__name__.lower(): main_object
        })

    def post(self, request):
        bound_form = self.model_form(request.POST)

        if bound_form.is_valid():
            new_object = bound_form.save()

            return redirect(new_object)
        return render(request, self.template, context={"form": bound_form})


class ObjectUpdateMixin:
    model = None
    model_form = None
    template = None

    def get(self, request, slug):

        object = self.model.objects.get(slug__iexact=slug)
        bound_form = self.model_form(instance=object)
        all_warehouses = self.model.objects.filter(date_pub__lte=timezone.now()).order_by('-date_pub')

        return render(request, self.template, context={
            'war_create_form': bound_form,
            self.model.__name__.lower(): all_warehouses,
        })
    

    def post(self, request, slug):
        old_object = self.model.objects.get(slug__iexact=slug)
        bound_form = self.model_form(request.POST, instance=old_object)

        if bound_form.is_valid():
            new_object = bound_form.save()

            return redirect(new_object)

        return render(request, self.template, context={"war_create_form": bound_form})

