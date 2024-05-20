from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import permission_classes, api_view, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import GroupDiscipline, Profile, Group, VideoMaterials, Discipline, Comment, View, StudentDiscipline, VideoLike
from rest_framework.decorators import action
from django.db.models import Count, Q
from django.contrib.auth.hashers import check_password
import subprocess
from django.conf import settings
from rest_framework.exceptions import ValidationError
from django.db.models import Min
import os
import random
import subprocess

from .serializers import GroupDisciplineSerializer, ProfileSerializer, CreateUserSerializer, ProfileSerializerTwo, WhoAmISerializer, GroupSerializer, VideoMaterialSerializer, DisciplineSerializer, CommentSerializer, ViewSerializer, StudentDisciplineSerializer, VideoLikeSerializer, SecondVideoLikeSerializer

@api_view()
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def User(request):
    return Response({
        'data': WhoAmISerializer(request.user).data
    })


class UserViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    http_method_names = ['get', 'post', 'put', 'delete']
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()

        id = self.request.query_params.get('id')
        if id:
            return qs.filter(id=id)

        email = self.request.query_params.get('email')
        if email:
            qs = qs.filter(email=email)

        firstname = self.request.query_params.get('firstname')
        if firstname:
            qs = qs.filter(first_name=firstname)

        lastname = self.request.query_params.get('lastname')
        if lastname:
            qs = qs.filter(last_name__icontains=lastname)

        group = self.request.query_params.get('group')
        if group:
            qs = qs.filter(id_group=group)

        group_name = self.request.query_params.get('id_group.name')
        if group_name:
            qs = qs.filter(id_group__name=group_name)
        
        return qs
            
    
    def create(self, request, *args, **kwargs):
            serializer = CreateUserSerializer(data=request.data)
            if serializer.is_valid():
                email = serializer.validated_data.get('email')
                if Profile.objects.filter(email=email).exists():
                    return Response(status=status.HTTP_409_CONFLICT, data='User with this email is already registered')
                new_user = serializer.save()
                new_user.set_password(serializer.validated_data.get('password'))
                new_user.save()
                return Response(data=serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        pk = kwargs.get('pk')

        instance = get_object_or_404(Profile, pk=pk)
        serializer = ProfileSerializerTwo(instance, data=request.data)
        password = instance.password
        if serializer.is_valid():
            current_password = request.data.get('current_password')
            new_password = request.data.get('new_password')
            if new_password:
                if current_password:
                    if check_password(current_password, password):
                        instance.set_password(new_password)
                        instance.save()
                    else:
                        return Response({"error": "Текущий пароль неверен."}, status=status.HTTP_400_BAD_REQUEST)
                else: return Response({"error": "Не введен текущий пароль."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        qs = super().get_queryset()
        id = request.GET.get('id')

        if id:
            qs_item = qs.filter(id=id)

            if qs_item.count() != 1:
                return Response(status=status.HTTP_204_NO_CONTENT)

            qs_item.delete()
            return Response(status=status.HTTP_200_OK, data='deleted successfully')

        return Response(status=status.HTTP_400_BAD_REQUEST, data='invalid id value')
    
    

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    http_method_names = ['get', 'post', 'put', 'delete']
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()

        id = self.request.query_params.get('id')
        if id:
            return qs.filter(id=id)

        name = self.request.query_params.get('name')
        if name:
            qs = qs.filter(name=name)

        id_user = self.request.query_params.get('id_user')
        if id_user:
            profile = Profile.objects.get(id=id_user)
            groups = profile.id_group.all() if profile.id_group else []
            qs = groups
        else:
             qs = super().get_queryset()
            
        return qs

    def create(self, request, *args, **kwargs):
        if not request.data.get('name'):
            return Response(status=status.HTTP_400_BAD_REQUEST, data='Name is missing')
        new_group = GroupSerializer(data=request.data)
        if new_group.is_valid():
            new_group.save()
            return Response(data=new_group.data, status=status.HTTP_201_CREATED)
        return Response(new_group.errors)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = GroupSerializer(instance, data=request.data)
        if serializer.is_valid():
            updated_group = serializer.save()
            updated_group.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors)

    def delete(self, request):
        qs = super().get_queryset()
        id = request.GET.get('id')

        if id:
            qs_item = qs.filter(id=id)

            if qs_item.count() != 1:
                return Response(status=status.HTTP_204_NO_CONTENT)

            qs_item.delete()
            return Response(status=status.HTTP_200_OK, data='deleted successfully')

        return Response(status=status.HTTP_400_BAD_REQUEST, data='invalid id value')
    
class VideoMaterialsViewset(viewsets.ModelViewSet):
    queryset = VideoMaterials.objects.all()
    serializer_class = VideoMaterialSerializer
    http_method_names = ['get', 'post', 'put', 'delete']
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()

        id = self.request.query_params.get('id')
        if id:
            return qs.filter(id=id)

        title = self.request.query_params.get('title')
        if title:
            qs = qs.filter(title__icontains=title)

        upload_date = self.request.query_params.get('upload_date')
        if upload_date:
            qs = qs.filter(upload_date=upload_date)
        
        file_link = self.request.query_params.get('file_link')
        if file_link:
            qs = qs.filter(file_link=file_link)

        id_discipline = self.request.query_params.get('id_discipline')
        if id_discipline:
            qs = qs.filter(id_discipline=id_discipline)

        id_teacher = self.request.query_params.get('id_teacher')
        if id_teacher:
            qs = qs.filter(id_teacher=id_teacher)

        return qs.order_by('-upload_date')

    def put(self, request):
        instance = self.get_object()
        serializer = VideoMaterials(instance, data=request.data)
        if serializer.is_valid():
            updated_group = serializer.save()
            updated_group.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors)

    def delete(self, request):
        qs = super().get_queryset()
        id = request.GET.get('id')

        if id:
            qs_item = qs.filter(id=id)

            if qs_item.count() != 1:
                return Response(status=status.HTTP_204_NO_CONTENT)

            qs_item.delete()
            return Response(status=status.HTTP_200_OK, data='deleted successfully')

        return Response(status=status.HTTP_400_BAD_REQUEST, data='invalid id value')

    def create(self, request, *args, **kwargs):
        if not request.data.get('title') or not request.data.get('id_discipline')or not request.data.get('id_teacher') or not request.data.get('file_link'):
            return Response(status=status.HTTP_400_BAD_REQUEST, data='title or file_link or id_discipline is absent')
        
        serializer = VideoMaterialSerializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            video_path = instance.file_link.path

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

                instance.preview_image.name = os.path.join('video_previews', preview_name)
                instance.save()

            except subprocess.CalledProcessError as e:
                print(f"Error generating preview: {e}")

            except Exception as e:
                print(f"An error occurred: {e}")

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        


class DisciplineViewset(viewsets.ModelViewSet):
    queryset = Discipline.objects.all()
    serializer_class = DisciplineSerializer
    http_method_names = ['get', 'post', 'put', 'delete']
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()

        id = self.request.query_params.get('id')
        if id:
            return qs.filter(id=id)

        name_discipline = self.request.query_params.get('name_discipline')
        if name_discipline:
            qs = qs.filter(name_discipline=name_discipline)

        id_teacher = self.request.query_params.get('id_teacher')
        if id_teacher:
            qs = qs.filter(id_teacher=id_teacher)

        return qs

    def put(self, request):
        instance = self.get_object()
        serializer = DisciplineSerializer(instance, data=request.data)
        if serializer.is_valid():
            updated_group = serializer.save()
            updated_group.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors)

    def delete(self, request):
        qs = super().get_queryset()
        id = request.GET.get('id')

        if id:
            qs_item = qs.filter(id=id)

            if qs_item.count() != 1:
                return Response(status=status.HTTP_204_NO_CONTENT)

            qs_item.delete()
            return Response(status=status.HTTP_200_OK, data='deleted successfully')

        return Response(status=status.HTTP_400_BAD_REQUEST, data='invalid id value')

    def create(self, request, *args, **kwargs):
        if not request.data.get('name_discipline') or not request.data.get('id_teacher'):
            return Response(status=status.HTTP_400_BAD_REQUEST, data='name_discipline or id_teacher is absent')

        post = DisciplineSerializer(data=request.data)

        if post.is_valid():
            post.save()
            return Response(data=post.data, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data='unable to parse the body')
        
class CommentViewset(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    http_method_names = ['get', 'post', 'put', 'delete']
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()

        id = self.request.query_params.get('id')
        if id:
            return qs.filter(id=id)

        content = self.request.query_params.get('content')
        if content:
            qs = qs.filter(content=content)

        id_author = self.request.query_params.get('id_author')
        if id_author:
            qs = qs.filter(id_author=id_author)

        id_video = self.request.query_params.get('id_video')
        if id_video:
            qs = qs.filter(id_video=id_video)

        return qs.order_by('-creation_date')

    def put(self, request):
        instance = self.get_object()
        serializer = CommentSerializer(instance, data=request.data)
        if serializer.is_valid():
            updated_group = serializer.save()
            updated_group.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors)

    def delete(self, request):
        qs = super().get_queryset()
        id = request.GET.get('id')

        if id:
            qs_item = qs.filter(id=id)

            if qs_item.count() != 1:
                return Response(status=status.HTTP_204_NO_CONTENT)

            qs_item.delete()
            return Response(status=status.HTTP_200_OK, data='deleted successfully')

        return Response(status=status.HTTP_400_BAD_REQUEST, data='invalid id value')

    def create(self, request, *args, **kwargs):
        if not request.data.get('content') or not request.data.get('id_video') or not request.data.get('id_author'):
            return Response(status=status.HTTP_400_BAD_REQUEST, data='content, user or id_video or id_author is absent')
        
        post = CommentSerializer(data=request.data)

        if post.is_valid():
            post.save()
            return Response(data=post.data, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data='unable to parse the body')


class ViewViewset(viewsets.ModelViewSet):
    queryset = View.objects.all()
    serializer_class = ViewSerializer
    http_method_names = ['get', 'post', 'delete']
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()

        id = self.request.query_params.get('id')
        if id:
            return qs.filter(id=id)

        id_video = self.request.query_params.get('id_video')
        if id_video:
            qs = qs.filter(id_video=id_video)

        id_user = self.request.query_params.get('id_user')
        if id_user:
            qs = qs.filter(id_user=id_user)

        return qs

    def delete(self, request):
        qs = super().get_queryset()
        id = request.GET.get('id')

        if id:
            qs_item = qs.filter(id=id)

            if qs_item.count() != 1:
                return Response(status=status.HTTP_204_NO_CONTENT)

            qs_item.delete()
            return Response(status=status.HTTP_200_OK, data='deleted successfully')

        return Response(status=status.HTTP_400_BAD_REQUEST, data='invalid id value')

    def create(self, request, *args, **kwargs):
        if not request.data.get('id_video') or not request.data.get('id_user'):
            return Response(status=status.HTTP_400_BAD_REQUEST, data='id_user or id_video is absent')

        post = ViewSerializer(data=request.data)
        print(request.data)

        if post.is_valid():
            post.save()
            return Response(data=post.data, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data='unable to parse the body')
              
class StudentDisciplineViewset(viewsets.ModelViewSet):
    queryset = StudentDiscipline.objects.all()
    serializer_class = StudentDisciplineSerializer
    http_method_names = ['get', 'post', 'put', 'delete']
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()

        id = self.request.query_params.get('id')
        if id:
            return qs.filter(id=id)

        id_student = self.request.query_params.get('id_student')
        if id_student:
            return qs.filter(id_student=id_student)
            
        id_discipline = self.request.query_params.get('id_discipline')
        if id_discipline:
            qs = qs.filter(id_discipline=id_discipline)
        
        return qs

    def put(self, request):
        instance = self.get_object()
        serializer = StudentDisciplineSerializer(instance, data=request.data)
        if serializer.is_valid():
            updated_group = serializer.save()
            updated_group.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors)

    def delete(self, request):
        qs = super().get_queryset()
        id = request.GET.get('id')

        if id:
            qs_item = qs.filter(id=id)

            if qs_item.count() != 1:
                return Response(status=status.HTTP_204_NO_CONTENT)

            qs_item.delete()
            return Response(status=status.HTTP_200_OK, data='deleted successfully')

        return Response(status=status.HTTP_400_BAD_REQUEST, data='invalid id value')

    def create(self, request, *args, **kwargs):
        if not request.data.get('id_student') or not request.data.get('id_discipline') :
            return Response(status=status.HTTP_400_BAD_REQUEST, data='id_discipline or id_student is absent')
        
        post = StudentDisciplineSerializer(data=request.data)

        if post.is_valid():
            post.save()
            return Response(data=post.data, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data='unable to parse the body')
        

class VideoLikeViewset(viewsets.ModelViewSet):
    queryset = VideoLike.objects.all()
    serializer_class = VideoLikeSerializer
    http_method_names = ['get', 'post', 'put', 'delete']
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = self.queryset
        id_user = self.request.query_params.get('id_user')
        id_video = self.request.query_params.get('id_video')

        if id_user:
            queryset = queryset.filter(id_user=id_user)
        if id_video:
            queryset = queryset.filter(id_video=id_video)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        likes_count = queryset.filter(reaction=VideoLike.LIKE).count()
        dislikes_count = queryset.filter(reaction=VideoLike.DISLIKE).count()

        response_data = {
            'likes_count': likes_count,
            'dislikes_count': dislikes_count
        }

 
        id_user = self.request.query_params.get('id_user')
        id_video = self.request.query_params.get('id_video')
        info = VideoLikeSerializer(queryset, many=True)
        if id_user:
            queryset = self.get_queryset().filter(id_user=id_user)
            serializer = VideoLikeSerializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        
        if id_video:
            response_data = {
                'likes_count': likes_count,
                'dislikes_count': dislikes_count
            }
            serializer = SecondVideoLikeSerializer(queryset, many=True)
            response_data['data'] = serializer.data     
            return Response(response_data, status=status.HTTP_200_OK)
        
        return Response(info.data, status=status.HTTP_200_OK)

    def put(self, request):
        instance = self.get_object()
        serializer = VideoLikeSerializer(instance, data=request.data)
        if serializer.is_valid():
            updated_like = serializer.save()
            updated_like.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors)

    def delete(self, request):
        qs = super().get_queryset()
        id = request.GET.get('id')

        if id:
            qs_item = qs.filter(id=id)

            if qs_item.count() != 1:
                return Response(status=status.HTTP_204_NO_CONTENT)

            qs_item.delete()
            return Response(status=status.HTTP_200_OK, data='deleted successfully')

        return Response(status=status.HTTP_400_BAD_REQUEST, data='invalid id value')

    def create(self, request, *args, **kwargs):
        if not request.data.get('id_user') or not request.data.get('id_video') or not request.data.get('reaction')  :
            return Response(status=status.HTTP_400_BAD_REQUEST, data='id_user, id_video or reaction is absent')
        
        post = VideoLikeSerializer(data=request.data)

        if post.is_valid():
            post.save()
            return Response(data=post.data, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data='unable to parse the body')

class GroupDisciplineViewset(viewsets.ModelViewSet):
    queryset = GroupDiscipline.objects.all()
    serializer_class = GroupDisciplineSerializer
    http_method_names = ['get', 'post', 'put', 'delete']
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        allowed_params = {'id', 'id_group', 'id_discipline'}
        request_params = set(self.request.query_params.keys())

        invalid_params = request_params - allowed_params
        if invalid_params:
            raise ValidationError(f"Invalid parameters: {', '.join(invalid_params)}")
        
        id_group = self.request.query_params.get('id_group')
        if not id_group:
            raise ValidationError("Missing required parameter: id_group")

        id = self.request.query_params.get('id')
        if id:
            return qs.filter(id=id)

        id_group = self.request.query_params.get('id_group')
        if id_group:
            id_group_list = id_group.split(',')
            qs = qs.filter(id_group__in=id_group_list)
            subquery = qs.values('id_discipline').annotate(min_id=Min('id')).values('min_id')

            qs = qs.filter(id__in=subquery)
        
        else: return qs
            
        id_discipline = self.request.query_params.get('id_discipline')
        if id_discipline:
            qs = qs.filter(id_discipline=id_discipline)

        return qs
    
    def put(self, request):
        instance = self.get_object()
        serializer = GroupDisciplineSerializer(instance, data=request.data)
        if serializer.is_valid():
            updated_group = serializer.save()
            updated_group.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors)

    def delete(self, request):
        qs = super().get_queryset()
        id = request.GET.get('id')

        if id:
            qs_item = qs.filter(id=id)

            if qs_item.count() != 1:
                return Response(status=status.HTTP_204_NO_CONTENT)

            qs_item.delete()
            return Response(status=status.HTTP_200_OK, data='deleted successfully')

        return Response(status=status.HTTP_400_BAD_REQUEST, data='invalid id value')

    def create(self, request, *args, **kwargs):
        if not request.data.get('id_group') or not request.data.get('id_discipline') :
            return Response(status=status.HTTP_400_BAD_REQUEST, data='id_discipline or id_group is absent')
        
        post = GroupDisciplineSerializer(data=request.data)

        if post.is_valid():
            post.save()
            return Response(data=post.data, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data='unable to parse the body')
        