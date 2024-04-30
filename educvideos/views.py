from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import permission_classes, api_view, authentication_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Profile, Group
from rest_framework.decorators import action


from .serializers import ProfileSerializer, CreateUserSerializer, WhoAmISerializer, GroupSerializer, GroupUserSerializer

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
            qs = qs.filter(usernemailame=email)

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

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ProfileSerializer(instance, data=request.data)
        if serializer.is_valid():
            updated_user = serializer.save()
            if 'password' in request.data:
                updated_user.set_password(request.data['password'])
                updated_user.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors)

    def destroy(self, request, *args, **kwargs):
        queryset = Profile.objects.all()

        if self.get_object().id:
            user = queryset.filter(id=self.get_object().id)
            if user.count() != 1:
                return Response(status=status.HTTP_204_NO_CONTENT)
            
            user.delete()
            return Response(status=status.HTTP_200_OK)
        
        return Response(status=status.HTTP_400_BAD_REQUEST)
    
    def list(self, request):
        group_name = request.query_params.get('group')

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
        


class ProfileGroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupUserSerializer
    http_method_names = ['get']

    def get_queryset(self):
        id_user = self.request.query_params.get('id_user')
        
        if id_user:
            profile = Profile.objects.get(id=id_user)
            groups = profile.id_group.all() if profile.id_group else []
            return groups
        else:
            return super().get_queryset()
        

@authentication_classes([JWTAuthentication])

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    http_method_names = ['get', 'post', 'put', 'delete']

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
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors)

    def destroy(self, request, *args, **kwargs):
        queryset = Group.objects.all()
        if self.get_object().id:
            group = queryset.filter(id=self.get_object().id)
            if group.count() != 1:
                return Response(status=status.HTTP_204_NO_CONTENT)
            group.delete()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
