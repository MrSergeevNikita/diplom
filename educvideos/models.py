from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class Group(models.Model):
    name = models.CharField(max_length=50)

class Profile(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    id_group = models.ManyToManyField('Group', blank=True, null=True)
    email = models.EmailField(unique=True)
    patronymic = models.CharField(max_length=20, null=True, blank=True)
    username = models.CharField(max_length=150, unique=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

class Discipline(models.Model):
    name_discipline = models.CharField(max_length=100)
    id_teacher = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='disciplines_taught')


class StudentDiscipline(models.Model):
    id_student = models.ForeignKey('Profile', on_delete=models.CASCADE)
    id_discipline = models.ForeignKey('Discipline', on_delete=models.CASCADE)

class VideoMaterials(models.Model):
    title = models.CharField(max_length=32)
    file_link = models.FileField()
    upload_date = models.DateTimeField(auto_now_add=True)
    id_teacher = models.ForeignKey('Profile', on_delete=models.CASCADE)
    id_discipline = models.ForeignKey('Discipline', on_delete=models.CASCADE)

class Comment(models.Model):
    content = models.TextField()
    id_author = models.ForeignKey('Profile', on_delete=models.SET_NULL, blank=True, null=True)
    id_video = models.ForeignKey('VideoMaterials', on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)


class View(models.Model):
    id_video = models.ForeignKey('VideoMaterials', on_delete=models.CASCADE)
    id_user = models.ForeignKey('Profile', on_delete=models.CASCADE)

