from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User


def index(request):
    post_list = Post.objects.all().order_by('-pub_date')
    paginator = Paginator(post_list, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'posts/index.html', {'page': page,
                                                'paginator': paginator,
                                                'post_list': post_list,
                                                })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.group.all().order_by('-pub_date')
    post_list = posts
    paginator = Paginator(post_list, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, 'posts/index.html', {'page': page,
                                                'paginator': paginator,
                                                'group': group,
                                                }
                  )


@login_required
def new_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, files=request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect(reverse('posts:index'))
        return render(request, 'posts/new_post.html', {'form': form})
    form = PostForm()
    return render(request, 'posts/new_post.html', {'form': form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post = Post.objects.filter(author__username=username).all()
    posts = author.posts.all().order_by('-pub_date')
    paginator = Paginator(posts, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'posts/profile.html', {'author': author,
                                                  'post': post,
                                                  'page': page,
                                                  'paginator': paginator
                                                  })


def post_view(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    count = post.author.posts.count()
    comments = post.comments.all()
    form = CommentForm(request.POST or None)
    return render(request, 'posts/post.html', {'post': post,
                                               'author': post.author,
                                               'count': count,
                                               'comments': comments,
                                               'form': form,
                                               })


@login_required
def post_edit(request, username, post_id):
    item = get_object_or_404(Post, author__username=username, id=post_id)
    if request.user != item.author:
        redirect(reverse(
            'posts:post_view', args=[username, post_id]))
    form = PostForm(request.POST or None, instance=item)
    if form.is_valid():
        form.save()
        return redirect(reverse(
            'posts:post_view', args=[username, post_id]))
    return render(request,
                  'posts/new_post.html',
                  {'form': form, 'item': item})


def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    return render(request, 'misc/500.html', status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    author = post.author
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect(reverse('posts:post_view',
                            kwargs={'username': author.username,
                                    'post_id': post.id}))


@login_required
def follow_index(request):
    """Страница с постами авторов на которые подписан пользователь"""
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'posts/follow.html',
        {
            'post': posts,
            'page': page,
            'paginator': paginator,
        }
    )


@login_required
def profile_follow(request, username):
    """Функция для подписки на автора"""
    author = get_object_or_404(User, username=username)
    currently_user = request.user
    if currently_user != author:
        Follow.objects.get_or_create(user=currently_user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    """Функция для отписки от автора"""
    author = get_object_or_404(User, username=username)
    currently_user = request.user
    Follow.objects.filter(user=currently_user, author=author).delete()
    return redirect('posts:profile', username=username)
