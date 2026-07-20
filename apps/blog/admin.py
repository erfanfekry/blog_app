from django.contrib import admin
from .models import *
from django.contrib.auth.models import User

# Inlines classes
class CommentInline(admin.StackedInline):
    model = Comment
    extra = 0
    readonly_fields = ['name', 'body']

class ImageInline(admin.StackedInline):
    model = Image
    extra = 0
    readonly_fields = ['title', 'description']

# Admin classes
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'publish', 'reading_time',  'status']
    ordering = ['-publish', 'author']
    list_filter = ['status', 'author', 'publish']
    raw_id_fields = ['author']
    date_hierarchy = 'publish'
    prepopulated_fields = {'slug': ['title']}
    list_editable = ['status', 'category']
    list_display_links = ['title']
    inlines = [CommentInline, ImageInline]

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject', 'phone']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'name', 'created', 'active']
    list_filter = ['active', 'created', "updated"]
    search_fields = ['name', 'body']
    list_editable = ['active']


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['post', f'title', 'created',]

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'date_of_birth', 'bio', 'job', 'image_file']

