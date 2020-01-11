from django.db import models

class CommonTag(models.Model):
    class Meta:
        abstract = True
    
    tag = models.CharField(max_length=256)
    
    def __str__(self):
        return self.tag


class Post(CommonTag):
    title = models.CharField(max_length=150, db_index=True)

    def __str__(self):
        return self.title


class Tag(CommonTag):
    slug = slug = models.SlugField(max_length=100, unique=True)
    
    def __str__(self):
        return '{}'.format(self.tag)