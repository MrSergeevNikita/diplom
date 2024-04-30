from rest_framework import routers
from educvideos import views
from django.urls import path, re_path


router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'group', views.ProfileGroupViewSet, basename='group')
router.register(r'groups', views.GroupViewSet, basename='groups')
