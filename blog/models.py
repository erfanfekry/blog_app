import os.path

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from django_resized import ResizedImageField

from config import settings


# override Manager's get_queryset method
class PublishManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Post.Status.PUBLISHED.PUBLISHED)


class Post(models.Model):
    class Category(models.TextChoices):
        CELEBRITY = 'Celebrity', 'Celebrity'
        CARTOON = 'Cartoon', 'Cartoon'
        ADMIN ='Admin' , 'Admin'
        OTHER = 'Other', 'Other'

    class Status(models.TextChoices):
        PUBLISHED = 'PB', 'Published'
        DRAFT = 'DF', 'Draft'
        REJECTED = 'RJ', 'Rejected'

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=200)
    description = models.TextField()
    slug = models.SlugField(max_length=200)
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.PUBLISHED)
    category = models.CharField(max_length=10, choices=Category.choices, default=Category.OTHER)
    reading_time = models.PositiveIntegerField(default=0)

    objects = models.Manager()
    published = PublishManager()

    class Meta:
        ordering = ['-publish']
        indexes = [models.Index(fields=['-publish'])]

    def __str__(self):  # override
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'id': self.id})

    def delete(self, *args, **kwargs):
        for img in self.images.all():
            img_storage, img_path = img.image_file.storage,img.image_file.path
            print('img_storage: ', img_storage, '\nimg_path: ',  img_path)

            img_storage.delete(img_path)
        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Ticket(models.Model):
    message = models.TextField()
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    subject = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']
        indexes = [models.Index(fields=['-created'])]

    def __str__(self):  # override
        return self.subject


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=200)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created']
        indexes = [models.Index(fields=['-created'])]

    def __str__(self):  # override
        return f'{self.name} : {self.post}'

def upload_to_callable(instance, filename):
    username = instance.post.author.username
    if not filename:
        filename = 'anonymous'
    return f'{username}/{filename}'


class Image(models.Model):

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    title = models.CharField(max_length=250, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    image_file = ResizedImageField(size=[500, 500], quality=100,
                                   crop=['middle', 'center'], scale=0.5, upload_to='account_images')

    class Meta:
        ordering = ['image_file']
        indexes = [models.Index(fields=['image_file'])]

    def __str__(self):  # override
        return self.title if self.title else self.image_file.name

    def save(self, *args, **kwargs):
        if not self.title:
            filename = os.path.basename(self.image_file.name)
            filename, _ = os.path.splitext(filename)
            self.title = slugify(filename)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        img_storage, img_path = self.image_file.storage, self.image_file.path
        img_storage.delete(img_path)
        super().delete(*args, **kwargs)

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='account')
    date_of_birth = models.DateTimeField(null=True, blank=True, verbose_name='Birth Date')
    bio = models.TextField(null=True, blank=True, verbose_name='Biography')
    job = models.CharField(max_length=250, null=True, blank=True,verbose_name='Job')
    image_file = ResizedImageField(size=[500, 500], quality=70,
                                   crop=['middle', 'center'], scale=0.5, upload_to='account_images',
                                   null=True, blank=True, verbose_name='Profile Image')

    def __str__(self):
        return self.user.username