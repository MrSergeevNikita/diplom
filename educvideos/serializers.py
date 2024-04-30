from rest_framework import serializers
from .models import Group, Profile, Discipline, VideoMaterials, Comment, View


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

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'

class VideoMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoMaterials
        fields = '__all__'

class ViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = View
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
    
    def update(self, instance, validated_data):
        groups_data = validated_data.pop('groups', None)
        
        # Обновляем основные поля профиля
        instance = super().update(instance, validated_data)
        
        # Обновляем связи с группами
        if groups_data is not None:
            instance.groups.set(groups_data)

        return instance

class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name', 'email', 'password']

class WhoAmISerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['first_name', 'last_name','patronymic', 'email', 'is_student', 'is_teacher', 'is_admin', 'id_group']
        