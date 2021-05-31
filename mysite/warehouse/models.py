from django.db import models
from django.shortcuts import reverse
from .utils import gen_slug

# Create your models here.


class Warehouses(models.Model):

    title = models.CharField(max_length=150, db_index=True)
    slug = models.SlugField(max_length=200, blank=True, unique=True)
    description = models.TextField(blank=True, max_length=300, db_index=True)
    date_pub = models.DateTimeField(auto_now_add=True)

    # lang_filter = models.CharField(verbose_name="Site side: ", max_length=2, choices=lang_choice, blank=True, default='RU')

    def get_absolute_url(self):
        return reverse('select_warehouse_url', kwargs={'slug': self.slug})
    
    def get_update_url(self):
        return reverse('update_warehouse_url', kwargs={'slug': self.slug})

    def get_delete_url(self):
        return reverse('delete_warehouse_url', kwargs={'slug': self.slug})


    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = gen_slug(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Product(models.Model):
    title = models.CharField(max_length=200, db_index=True)
    barcode = models.CharField(max_length=50, blank=True, unique=True, db_index=True)
    quantity = models.PositiveIntegerField()
    active_stamp = models.BooleanField()
    olx_stamp = models.BooleanField()
    price = models.PositiveIntegerField()
    slug = models.SlugField(max_length=200, blank=True, unique=True)
    description = models.TextField(blank=True, max_length=1000, db_index=True)
    date_pub = models.DateTimeField(auto_now_add=True)

    #Relations
    warehouse_products = models.ManyToManyField('Warehouses', blank=True, related_name="related_products")

    def get_absolute_url(self):
        return reverse('related_products_url', kwargs={'slug': self.slug})
    
    def get_update_url(self):
        return reverse('update_product_url', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = gen_slug(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
