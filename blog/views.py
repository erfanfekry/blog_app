from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from django.views.generic import ListView, DetailView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.contrib import messages
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank, TrigramSimilarity
from .models import *
from .forms import *


def index(request):
    return render(request, 'blog/index.html')

def post_list(request, category=None):
    if category:
        posts = Post.published.filter(category=category)
    else:
        posts = Post.published.all()

    paginator = Paginator(posts, 3)
    page_number = request.GET.get('page', 1)
    print('page', page_number)
    try:
        current_page = paginator.get_page(page_number)
    except PageNotAnInteger:
        current_page = paginator.get_page(1)
    except EmptyPage:
        current_page = paginator.get_page(paginator.num_pages)
    context = {
        'posts' : current_page,
        'category': category
    }
    return render(request, 'blog/post_list.html', context)


# class PostListView(LoginRequiredMixin, ListView):
#     def get_queryset(self):
#         return Post.published.exclude(author__username=self.request.user.username)
#     context_object_name = 'posts'
#     template_name = 'blog/post_list.html'
#     paginate_by = 2
#     # queryset = Post.published.all()

@login_required
def post_detail(request, id):
    post = get_object_or_404(Post, id=id, status=Post.Status.PUBLISHED)
    if request.method == 'POST':
        print(request.POST)
    form = CommentForm()
    form.fields['body'].label = 'Message'
    comments = post.comments.filter(active=True)
    context = {
        "post": post,
        "comments": comments,
        "form": form,
    }
    return render(request, 'blog/post_detail.html', context)


#
# class PostDetailView(DetailView):
#     model = Post
#     template_name = 'blog/post_detail.html'
@login_required
def ticket(request):
    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            Ticket.objects.create(message=cleaned_data['message'], name=cleaned_data['name'],
                                  email=cleaned_data['email'], phone=cleaned_data['phone'],
                                  subject=cleaned_data['subject']
                                  )
            return redirect('blog:home')
    else:
        form = TicketForm()
    return render(request, 'forms/ticket.html', {'form': form})

@login_required
@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
    context = {
        "post": post,
        "comment": comment,
        "form": form,
    }
    return render(request, 'forms/comment.html', context)

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            for img in request.FILES.getlist('img'):
                Image.objects.create(post=post, image_file=img)
            return redirect('blog:post_list')
    else:
        form = PostForm()
    return render(request, 'forms/create_post.html', {'form': form})


def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(data=request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            # search_query = SearchQuery(query)
            # search_vector = SearchVector('title', 'description')
            # search_vector_ranked = SearchVector('title', weight='A') +\
            #                 SearchVector('description', weight='B') +\
            #                 SearchVector('slug', weight='D')

            # results = Post.published.filter(Q(title__icontains=query) # Q method + django field
            #                                  & Q(description__contains=query))

            # results = Post.published.filter(Q(title__search=query)
            #                               | Q(description__search=query)) # Q method + postgrse 'search' lookup

            # results = Post.published.annotate(search=SearchVector('description')).\ # SearchVector()
            #     filter(search=query)

            # results = Post.published.annotate(search=SearchVector('title', 'description')).\ # SearchQuery()
            #     filter(search=search_query)

            # results = Post.published.annotate(search=search_vector, rank=SearchRank(search_vector, search_query)) .\
            #     filter(search=search_query).order_by('-rank') # SearchRank()

            results_1 = Post.published.annotate(similarity=TrigramSimilarity('title', query)) \
                .filter(similarity__gt=0.07)
            results_2 = Post.published.annotate(similarity=TrigramSimilarity('description', query)) \
                .filter(similarity__gt=0.07)
            results_3 = Post.objects.annotate(similarity=TrigramSimilarity('images__title', query)) \
                .filter(similarity__gt=0.07)
            results_4 = Post.objects.annotate(similarity=TrigramSimilarity('images__description', query)) \
                .filter(similarity__gt=0.07)

            results = ((results_1 | results_2) | (results_3 | results_4)).distinct().order_by('-similarity')
    context = {
        'query': query,
        'results': results,
        'form': form
    }
    return render(request, 'blog/search.html', context)

@login_required
def profile(request):
    user = request.user
    posts = Post.published.filter(author=user)
    context = {
        'posts': posts
    }
    return render(request, 'blog/profile.html', context=context)

@login_required
def delete_post(request, post_id):
    post = Post.published.get(id=post_id)
    if request.method == 'POST':
        if 'action_button' in request.POST:
            if request.POST.get('action_button') == 'Yes':
                post.delete()
                messages.success(request, f'Post "{post.title}" was successfully deleted!')
            return redirect('blog:profile')

    return render(request, 'forms/delete_post.html', {'post': post})
@login_required
def edit_post(request, post_id):
    post = Post.published.get(id=post_id)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            for img in request.FILES.getlist('img'):
                Image.objects.create(post=post, image_file=img)
            return redirect('blog:post_list')
    else:
        form = PostForm(instance=post)
    return render(request, 'forms/create_post.html', {'form': form, 'post':post})
@login_required
def delete_image(request, image_id):
    img = get_object_or_404(Image, id=image_id)
    img.delete()
    return redirect("blog:profile")

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd['username'], password=cd['password'])
            print('User: ', user)
            if isinstance(user, User):
                if user.is_active:
                    login(request, user)
                    messages.success(request, f"User '{user.username}' logged in!")
                    return redirect("blog:post_list")
                else:
                    messages.error(request, f"User '{user.username}' is suspended!")
            else:
                messages.error(request, 'Entered Username or password is wrong!')
    else:
        form = LoginForm()
    return render(request, 'forms//login.html', {'form': form})

@login_required
def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect(request.META.get('HTTP_REFERER'))

def user_register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = form.save(commit=False)
            user.set_password(cd['password'])
            user.save()
            Account.objects.create(user=user)
            return render(request, 'registration/register-done.html', {'user':user})
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})

def user_register_done(request):
        user = request.user
        return render(request, 'registration/register-done.html', {'user':user})
@login_required
def account_edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=request.user)
        account_form = AccountEditForm(request.POST, request.FILES, instance=request.user.account)
        if user_form.is_valid() and account_form.is_valid():
            user_form.save()
            account_form.save()
            messages.success(request, 'Profile was successfully updated.')
            return redirect('blog:profile')
    else:
        user_form = UserEditForm(instance=request.user)
        account_form = AccountEditForm(instance=request.user.account)

    context = {
        'user_form': user_form,
        'account_form': account_form
    }
    return render(request, 'registration/user_edit.html', context)