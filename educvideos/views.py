from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import permission_classes, api_view, authentication_classes
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Profile


from .serializers import ProfileSerializer, CreateUserSerializer, WhoAmISerializer

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

    def get_queryset(self):
        queryset = Profile.objects.all()
        if self.request.method == 'GET':
            params = self.request.query_params.dict()
            try:
                queryset = queryset.filter(username=params['username'])
            except:
                pass
            try:
                queryset = queryset.filter(first_name__icontains=params['first_name'])
            except:
                pass
            try:
                queryset = queryset.filter(last_name__icontains=params['last_name'])
            except:
                pass
        return queryset

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

