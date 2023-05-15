"""webapps URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from socialnetwork import views

urlpatterns = [
    path('', views.global_action, name='home'),
    path('accounts/login/', views.login_action, name='reroute'),
    path('login', views.login_action, name='login'),
    path('logout', views.logout_action, name='logout'),
    path('register', views.register_action, name='register'),
    path('globalstream', views.global_action, name='globalstream'),
    path('followerstream', views.follower_action, name='followerstream'),
    path('myprofile', views.my_profile, name="myprofile"),
    path('other/<int:user_id>', views.other_profile, name="otherprofile"),
    path('picture/<int:user_id>', views.get_picture, name="picture"),
    path('follow/<int:user_id>', views.follow, name='follow'),
    path('unfollow/<int:user_id>', views.unfollow, name='unfollow'),
    path('socialnetwork/get-global', views.get_global, name="get-global"),
    path('socialnetwork/get-follower', views.get_follower, name="get-follower"),
    path('socialnetwork/add-comment', views.add_comment, name="ajax-add-comment")
]
