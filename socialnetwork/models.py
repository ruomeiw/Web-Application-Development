from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Post(models.Model):
    profile = models.ForeignKey(User, default=None, on_delete=models.PROTECT)
    text = models.CharField(
        max_length=140, default=None, blank=True, verbose_name='New Post:')
    date_time = models.DateTimeField()

    def __str__(self):
        return f"Post(id={self.id})"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    bio = models.CharField(max_length=200)
    picture = models.FileField(blank=True)
    content_type = models.CharField(max_length=50, blank=True)
    following = models.ManyToManyField(
        User, blank=True, related_name='followed_users')

    def __str__(self):
        return f"Profile(id={self.id})"


class Comment(models.Model):
    text = models.CharField(max_length=140)
    creation_time = models.DateTimeField()
    creator = models.ForeignKey(User, default=None, on_delete=models.PROTECT)
    post = models.ForeignKey(Post, default=None, on_delete=models.PROTECT)

    def __str__(self):
        return f"Comment(id={self.id})"
