from rest_framework import serializers
from .models import Group, Profile, Discipline, VideoMaterials, Comment, View, StudentDiscipline


class DisciplineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discipline
        fields = '__all__'

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']

class GroupUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name']


class VideoMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoMaterials
        fields = '__all__'

class ViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = View
        fields = '__all__'

class StudentDisciplineSerializer(serializers.ModelSerializer):
    discipline = DisciplineSerializer(source='id_discipline')
    
    class Meta:
        model = StudentDiscipline
        fields = '__all__'

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'
        extra_kwargs = {
            'username': {'required': False},
            'password': {'required': False},
            'email': {'required': False}
        }

class ProfileShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'patronymic']

class CommentSerializer(serializers.ModelSerializer):
    fio  = ProfileShortSerializer(source='id_author')
    class Meta:
        model = Comment
        fields = '__all__' 

class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'patronymic', 'email', 'password','is_student', 'is_teacher', 'is_admin', 'id_group']

class WhoAmISerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['id', 'first_name', 'last_name','patronymic', 'email', 'is_student', 'is_teacher', 'is_admin', 'id_group']
        