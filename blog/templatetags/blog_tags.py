from django import template
from ..models import Post, Comment
from django.db.models import Count
from markdown import markdown
from django.utils.safestring import mark_safe
from django.db.models import Max, Min
from django.contrib.auth.models import User



register = template.Library()

@register.simple_tag
def total_posts():
    return Post.published.count()

@register.simple_tag
def total_comments():
    return Comment.objects.filter(active=True).count()

@register.simple_tag
def last_post_date():
    return Post.published.order_by('-publish').first().publish

@register.simple_tag
def popular_posts(count):
    return Post.published.annotate(comment_count=(Count('comments'))).order_by('-comment_count')[:count]

@register.simple_tag
def r_time_most_least():
    least_val =  Post.published.aggregate(t_min = Min('reading_time'))['t_min']
    most_val =  Post.published.aggregate(t_max = Max('reading_time'))['t_max']
    least_qs =  Post.published.filter(reading_time=least_val).first()
    most_qs = Post.published.filter(reading_time=most_val).first()
    return [least_qs, most_qs]

@register.simple_tag
def post_date():
    newest =  Post.published.order_by('-publish').first()
    latest =  Post.published.order_by('publish').first()
    return [newest, latest]

@register.simple_tag
def user_activeness():
    post_count = User.objects.annotate(post_count=Count('posts')).order_by('-post_count')
    most_active =  post_count.first()
    least_active =  post_count.last()
    return [most_active, least_active]

@register.inclusion_tag("partials/recent_posts.html")
def recent_posts(count=4):
    r_posts = Post.published.order_by('-publish')[:count]
    context = {'r_posts': r_posts}
    return context

@register.filter(name='markdown')
def to_markdown(text):
    return mark_safe(markdown(text))

@register.filter
def word_censor(text:str):
    censored_text = text.replace('shut up', '<censored>').replace('Shut up', '<censored>')
    return censored_text