from django.db import models
from django.shortcuts import reverse

# Create your models here.


class Note(models.Model):
    lang_choice = [
        ('PL', 'Polski'),
        ('RU', 'Russian'),
    ]

    title = models.CharField(max_length=150, db_index=True)
    slug = models.SlugField(max_length=200, blank=True, unique=True)
    body = models.TextField(blank=True, db_index=True)
    date_pub = models.DateTimeField(auto_now_add=True)
    lang_filter = models.CharField(verbose_name="Site side: ", max_length=2, choices=lang_choice, blank=True, default='RU')

    def get_absolute_url(self):
        return reverse('note_page_url', kwargs={'slug': self.slug})
    
    def __str__(self):
        return self.title