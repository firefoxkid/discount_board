from django.core.paginator import Paginator
from django.shortcuts import redirect, render, get_object_or_404

from .models import Group, Post, Follow, Comment
from .forms import PostForm, CommentForm

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required


User = get_user_model()
PAGIN_SET = 10


def index(request):
    post_list = Post.objects.all().order_by('-pub_date')
    paginator = Paginator(post_list, PAGIN_SET)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    is_index = True
    return render(request,
                  'index.html',
                  {'page': page,
                   'post_list': post_list,
                   'is_index': is_index
                   })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, PAGIN_SET)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group.html",
                  {'group': group,
                   'page': page,
                   'posts': posts
                   })


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts_of_author = author.posts.all()
    posts_count = posts_of_author.count()
    paginator = Paginator(posts_of_author, PAGIN_SET)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    username = author.username
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user, author=author
        ).exists()
    else:
        following = False

    return render(request, 'posts/profile.html',
                  {'posts_count': posts_count,
                   'username': username,
                   'page': page,
                   'posts_of_author': posts_of_author,
                   'author': author,
                   'following': following
                   })


def post_view(request, username, post_id):
    post = get_object_or_404(Post,
                             author__username=username,
                             id=post_id,
                             )
    from_post_view = True
    comments = post.comments.all()
    form = CommentForm()
    username = post.author.username
    return render(request, 'posts/post.html',
                  {'post': post,
                   'post_id': post_id,
                   'username': username,
                   'author': post.author,
                   'comments': comments,
                   'form': form,
                   'from_post_view': from_post_view
                   })


@login_required
def new_post(request):
    current_user = request.user
    username = current_user.username
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('index')
    return render(request, 'posts/new_post.html',
                  {'form': form,
                   'current_user': current_user,
                   'new': True,
                   'username': username
                   })


@login_required
def post_edit(request, username, post_id):
    edited_post = get_object_or_404(Post,
                                    pk=post_id,
                                    author__username=username
                                    )
    if edited_post.author != request.user:
        return redirect('post', username=username, post_id=post_id)
    form = PostForm(request.POST or None,
                    instance=edited_post,
                    files=request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('post', username, post_id)
    return render(
        request,
        'posts/new_post.html',
        {'form': form,
         'username': username,
         'edit': True,
         'edited_post': edited_post
         }
    )


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('post', username, post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, PAGIN_SET)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'follow.html', {'page': page})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('profile', username=username)


@login_required
def post_del(request, username, post_id):
    edited_post = get_object_or_404(Post,
                                    pk=post_id,
                                    )
    if edited_post.author != request.user:
        return redirect('post', username=username, post_id=post_id)
    edited_post.delete()
    return redirect('index')


@login_required
def comment_del(request, username, post_id, comment_id):
    post = get_object_or_404(Post, id=post_id)
    comment = get_object_or_404(Comment,
                                id=comment_id,
                                post=post
                                )
    if comment.author != request.user:
        return redirect('post', username, post_id)
    comment.delete()
    return redirect('post', username, post_id)
