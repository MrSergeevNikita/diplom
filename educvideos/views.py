from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import permission_classes, api_view, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Profile, Group, VideoMaterials, Discipline, Comment, View
from rest_framework.decorators import action
from django.contrib.auth.hashers import check_password

from .serializers import ProfileSerializer, CreateUserSerializer, WhoAmISerializer, GroupSerializer, VideoMaterialSerializer, DisciplineSerializer, CommentSerializer, ViewSerializer

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
            qs = qs.filter(last_name=lastname)
            
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

    # def update(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     serializer = ProfileSerializer(instance, data=request.data)
    #     if serializer.is_valid():
    #         updated_user = serializer.save()
    #         if 'password' in request.data:
    #             updated_user.set_password(request.data['password'])
    #             updated_user.save()
    #         return Response(data=serializer.data, status=status.HTTP_200_OK)
    #     return Response(serializer.errors)
    def update(self, request, *args, **kwargs):
        pk = kwargs.get('pk')

        # Используем get_object_or_404 для получения объекта профиля (пользователя)
        instance = get_object_or_404(Profile, pk=pk)
        serializer = ProfileSerializer(instance, data=request.data)
        password = instance.password
        print(password)
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
            else: updated_user = serializer.save()
            
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
    
    def list(self, request):
        group_name = request.query_params.get('group')
        print(group_name)
        if group_name:
            group_exists_name = Group.objects.filter(name=group_name).exists()

            if group_exists_name:
                users = Profile.objects.filter(id_group__name=group_name)
                serializer = WhoAmISerializer(users, many=True)
                return Response(serializer.data)
            else:
                return Response({'error': 'Group with specified name does not exist'}, status=status.HTTP_404_NOT_FOUND)
        else:
            users = Profile.objects.all()
            serializer = ProfileSerializer(users, many=True)
            return Response(serializer.data)
    

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    http_method_names = ['get', 'post', 'put', 'delete']
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Group.objects.all()
        if self.request.method == 'GET':
            params = self.request.query_params.dict()
            try:
                queryset = queryset.filter(id=params['id'])
            except:
                pass
            try:
                queryset = queryset.filter(name=params['name'])
            except:
                pass
            try:
                id_user = self.request.query_params.get('id_user')
        
                if id_user:
                    profile = Profile.objects.get(id=id_user)
                    groups = profile.id_group.all() if profile.id_group else []
                    return groups
                else:
                    return super().get_queryset()
            except:
                pass
        return queryset

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
            qs = qs.filter(title=title)

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

        return qs

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
        if not request.data.get('title') or not request.data.get('id_discipline')or not request.data.get('id_teacher'):
            return Response(status=status.HTTP_400_BAD_REQUEST, data='title or file_link or id_discipline is absent')

        post = VideoMaterialSerializer(data=request.data)

        if post.is_valid():
            post.save()
            return Response(data=post.data, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data='unable to parse the body')
        

        


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

        return qs

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
            return Response(status=status.HTTP_400_BAD_REQUEST, data='id_video or id_user  is absent')
        
        post = ViewSerializer(data=request.data)

        if post.is_valid():
            post.save()
            return Response(data=post.data, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data='unable to parse the body')
        
