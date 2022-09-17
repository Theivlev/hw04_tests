from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic.base import TemplateView

from .forms import PostForm
from .models import Group, Post, User
from .utilits import get_pages_paginator


def index(request):
    posts = Post.objects.select_related('group')
    page_obj = get_pages_paginator(request, posts, Post.OUTPUT_OF_POSTS)
    context = {
        'posts': posts,
        'title': 'Последние обновления на сайте',
        'page_obj': page_obj,
    }

    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()[:Post.OUTPUT_OF_POSTS]
    page_obj = get_pages_paginator(request, posts, Post.OUTPUT_OF_POSTS)
    context = {
        'group': group,
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


class JustStaticPage(TemplateView):
    template_name = 'app_name/just_page.html'


def profile(request, username):
    template = 'posts/profile.html'
    user = get_object_or_404(User, username=username)
    profile_list = Post.objects.filter(author=user)
    count_posts = profile_list.count()
    page_obj = get_pages_paginator(request, profile_list, Post.OUTPUT_OF_POSTS)
    context = {'author': user,
               'profile_list': profile_list,
               'count_posts': count_posts,
               'page_obj': page_obj,

               }

    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, id=post_id)
    context = {'post': post,
               }

    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    if request.method == 'POST':
        form = PostForm(request.POST or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', post.author)

    form = PostForm()
    return render(request, template, {'form': form})


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(instance=post)
    context = {
        'is_edit': True,
        'form': form
    }
    if request.method == 'POST':
        form = PostForm(request.POST or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:post_detail', post_id)

    return render(request, template, context)
