from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
import os
import random
import subprocess


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
    file_link = models.FileField(upload_to='videos/')
    upload_date = models.DateTimeField(auto_now_add=True)
    id_teacher = models.ForeignKey('Profile', on_delete=models.CASCADE)
    id_discipline = models.ForeignKey('Discipline', on_delete=models.CASCADE)
    preview_image = models.ImageField(upload_to='video_previews/', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:  
            super().save(*args, **kwargs)

            video_path = self.file_link.path

            try:
                cmd = [
                    'ffprobe',
                    '-v', 'error',
                    '-show_entries', 'format=duration',
                    '-of', 'default=noprint_wrappers=1:nokey=1',
                    video_path
                ]
                result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
                duration = float(result.stdout)

                random_second = random.uniform(1, duration)

                preview_name = os.path.splitext(os.path.basename(video_path))[0] + '_preview.jpg'
                preview_path = os.path.join(settings.MEDIA_ROOT, 'video_previews', preview_name)

                os.makedirs(os.path.dirname(preview_path), exist_ok=True)

                cmd = [
                    'ffmpeg',
                    '-ss', str(random_second),
                    '-i', video_path,
                    '-vframes', '1',
                    preview_path
                ]
                subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

                self.preview_image.name = os.path.join('video_previews', preview_name)

            except subprocess.CalledProcessError as e:
                print(f"Error generating preview: {e}")

            except Exception as e:
                print(f"An error occurred: {e}")

        super().save(*args, **kwargs)

class Comment(models.Model):
    content = models.TextField()
    id_author = models.ForeignKey('Profile', on_delete=models.SET_NULL, blank=True, null=True)
    id_video = models.ForeignKey('VideoMaterials', on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)


class View(models.Model):
    id_video = models.ForeignKey('VideoMaterials', on_delete=models.CASCADE)
    id_user = models.ForeignKey('Profile', on_delete=models.CASCADE)

