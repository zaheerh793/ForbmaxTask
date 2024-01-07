from django.db import models
from django.contrib.auth.models import User


class Group(models.Model):
    group_name = models.CharField(max_length=255)
    creation_name = models.CharField(max_length=255)
    users = models.ManyToManyField(User)

    def __str__(self):
        return self.group_name


def upload_to(instance, filename):
    return f'content/{instance.user.username}/{filename}'


class Content(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    tag_group = models.ForeignKey(Group, on_delete=models.CASCADE)
    visibility_choices = [('public', 'Public'), ('private', 'Private')]
    visibility = models.CharField(max_length=10, choices=visibility_choices)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    media_file = models.FileField(upload_to=upload_to, blank=True, null=True)

    def __str__(self):
        return self.title
