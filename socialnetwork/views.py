from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone, formats
from socialnetwork.models import Post, Profile, Comment
from socialnetwork.forms import LoginForm, RegisterForm, PostForm, ProfileForm
from socialnetwork.MyMemoryList import MyMemoryList
import json
from django.db import transaction

# Create your views here.

ENTRY_LIST = MyMemoryList()


@ensure_csrf_cookie
def add_comment(request):
    response = HttpResponse()

    if not request.user.id or not request.user.is_authenticated:
        return _my_json_error_response("You must be logged in to do this operation.", status=401)

    if request.method != "POST":
        return _my_json_error_response("You must use a POST request for this operation.", status=405)

    if not 'comment_text' in request.POST or not request.POST['comment_text']:
        return _my_json_error_response("You must enter a comment to add.", status=400)

    if not 'post_id' in request.POST or not request.POST['post_id']:
        return _my_json_error_response("No post id provided.", status=400)

    if not request.POST['post_id'].isdecimal():
        return _my_json_error_response("Invalid post id.", status=400)

    if not Post.objects.filter(id=request.POST['post_id']).exists():
        return _my_json_error_response("Post does not exist.", status=400)

    if request.POST['post_id'].strip() == '':
        return _my_json_error_response("No post id provided.", status=400)

    if not 'csrfmiddlewaretoken' in request.POST or not request.POST['csrfmiddlewaretoken']:
        return _my_json_error_response("Invalid CSRF token.", status=403)

    new_comment = Comment(
        text=request.POST['comment_text'], creation_time=timezone.now(), creator=request.user, post_id=request.POST['post_id'])
    new_comment.save()

    current_page = str(request.META.get('HTTP_REFERER'))
    if "global" in current_page or current_page == "http://localhost:8000/":
        response = get_global(request)
    elif "follower" in current_page:
        response = get_follower(request)

    return response


@ensure_csrf_cookie
def get_global(request):
    if not request.user.id or not request.user.is_authenticated:
        return _my_json_error_response("You must be logged in to do this operation", status=401)

    response_data = {}
    posts = []
    comments = []
    for model_item in Post.objects.all().order_by('-date_time'):
        post_item = {
            'id': model_item.id,
            'text': model_item.text,
            'user_id': model_item.profile.id,
            'fname': model_item.profile.first_name,
            'lname': model_item.profile.last_name,
            'date_time': formats.date_format(model_item.date_time, "n/j/Y g:i A")
        }
        posts.append(post_item)

    for model_item in Comment.objects.all().order_by('-creation_time'):
        comment_item = {
            'id': model_item.id,
            'comment_text': model_item.text,
            'post_id': model_item.post.id,
            'user_id': model_item.creator.id,
            'fname': model_item.creator.first_name,
            'lname': model_item.creator.last_name,
            'date_time': formats.date_format(model_item.creation_time, "n/j/Y g:i A")
        }
        comments.append(comment_item)

    response_data = {
        'posts': posts,
        'comments': comments
    }

    response_json = json.dumps(response_data, default=str)
    response = HttpResponse(response_json, content_type='application/json')
    response['Access-Control-Allow-Origin'] = '*'
    return response


@ensure_csrf_cookie
def get_follower(request):
    if not request.user.id or not request.user.is_authenticated:
        return _my_json_error_response("You must be logged in to do this operation", status=401)

    response_data = {}
    posts = []
    comments = []

    for model_item in Post.objects.all().order_by('-date_time'):
        if model_item.profile in request.user.profile.following.all():
            post_item = {
                'id': model_item.id,
                'text': model_item.text,
                'user_id': model_item.profile.id,
                'fname': model_item.profile.first_name,
                'lname': model_item.profile.last_name,
                'date_time': formats.date_format(model_item.date_time, "n/j/Y g:i A")
            }
            posts.append(post_item)

    follower_posts_id = [sub['id'] for sub in posts]
    for model_item in Comment.objects.all().order_by('-creation_time'):
        if model_item.post.id in follower_posts_id:
            comment_item = {
                'id': model_item.id,
                'comment_text': model_item.text,
                'post_id': model_item.post.id,
                'user_id': model_item.creator.id,
                'fname': model_item.creator.first_name,
                'lname': model_item.creator.last_name,
                'date_time': formats.date_format(model_item.creation_time, "n/j/Y g:i A")
            }
            comments.append(comment_item)

    response_data = {
        'posts': posts,
        'comments': comments
    }

    response_json = json.dumps(response_data, default=str)
    response = HttpResponse(response_json, content_type='application/json')
    response['Access-Control-Allow-Origin'] = '*'
    return response


def login_action(request):
    context = {}

    if request.method == 'GET':
        context['form'] = LoginForm()
        return render(request, 'socialnetwork/login.html', context)

    form = LoginForm(request.POST)
    context['form'] = form

    if not form.is_valid():
        return render(request, 'socialnetwork/login.html', context)

    new_user = authenticate(
        username=form.cleaned_data['username'], password=form.cleaned_data['password'])

    login(request, new_user)
    return redirect(reverse('globalstream'))


def logout_action(request):
    logout(request)
    return redirect(reverse('login'))


def register_action(request):
    context = {}

    if request.method == 'GET':
        context['form'] = RegisterForm()
        return render(request, 'socialnetwork/register.html', context)

    form = RegisterForm(request.POST)
    context['form'] = form

    if not form.is_valid():
        return render(request, 'socialnetwork/register.html', context)

    new_user = User.objects.create_user(username=form.cleaned_data['username'],
                                        password=form.cleaned_data['password'],
                                        email=form.cleaned_data['email'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'])

    new_user.save()

    new_user_profile = Profile.objects.create(user=new_user)
    new_user_profile.save()

    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])

    login(request, new_user)
    return redirect(reverse('globalstream'))


@login_required
def global_action(request):
    if not request.user.id or not request.user.is_authenticated:
        return _my_json_error_response("You must be logged in to do this operation", status=401)

    context = {
        'form': PostForm(), 'posts': Post.objects.all()}

    if request.method == 'GET':
        return render(request, 'socialnetwork/globalstream.html', context)

    if 'text' not in request.POST or not request.POST['text']:
        return render(request, 'socialnetwork/globalstream.html', context)

    new_post = Post(profile=request.user,
                    text=request.POST['text'], date_time=timezone.now())

    new_post.save()

    return render(request, 'socialnetwork/globalstream.html', context)


@login_required
def follower_action(request):
    if not request.user.id or not request.user.is_authenticated:
        return _my_json_error_response("You must be logged in to do this operation", status=401)

    context = {'posts': Post.objects.all()}
    return render(request, 'socialnetwork/followerstream.html', context)


@login_required
def get_picture(request, user_id):
    profile = get_object_or_404(Profile, id=user_id)
    if profile.content_type == 'text/html; charset=utf-8':
        return None
    return HttpResponse(profile.picture, content_type=profile.content_type)


@login_required
@transaction.atomic
def my_profile(request):
    context = {'profile': request.user.profile,
               'form': ProfileForm(initial={'bio': request.user.profile.bio})}

    if request.method == 'GET':
        return render(request, 'socialnetwork/myprofile.html', context)

    profile = Profile.objects.select_for_update().get(id=request.user.id)
    form = ProfileForm(request.POST, request.FILES, instance=profile)

    if not form.is_valid():
        return render(request, 'socialnetwork/myprofile.html', context)

    profile.bio = form.cleaned_data['bio']
    profile.picture = form.cleaned_data['picture']
    profile.content_type = form.cleaned_data['picture'].content_type

    profile.save()

    context = {'profile': profile,
               'form': ProfileForm(initial={'bio': profile.bio})}

    return render(request, 'socialnetwork/myprofile.html', context)


@login_required
def other_profile(request, user_id):
    if (user_id == request.user.id):
        return my_profile(request)

    user = get_object_or_404(User, id=user_id)

    return render(request, 'socialnetwork/otherprofile.html', {'profile': user.profile})


@login_required
def unfollow(request, user_id):
    user_to_unfollow = get_object_or_404(User, id=user_id)
    request.user.profile.following.remove(user_to_unfollow)
    request.user.profile.save()
    return render(request, 'socialnetwork/otherprofile.html',
                  {'profile': user_to_unfollow.profile})


@login_required
def follow(request, user_id):
    user_to_follow = get_object_or_404(User, id=user_id)
    request.user.profile.following.add(user_to_follow)
    request.user.profile.save()
    return render(request, 'socialnetwork/otherprofile.html',
                  {'profile': user_to_follow.profile})


def _my_json_error_response(message, status=200):
    response_json = '{ "error": "' + message + '" }'
    return HttpResponse(response_json, content_type='application/json', status=status)
