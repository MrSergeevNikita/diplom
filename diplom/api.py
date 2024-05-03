from rest_framework import routers
from educvideos import views
from django.urls import path, re_path


router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'groups', views.GroupViewSet, basename='groups')
router.register(r'video', views.VideoMaterialsViewset, basename='video')
router.register(r'discipline', views.DisciplineViewset, basename='discipline')
router.register(r'comment', views.CommentViewset, basename='comment')
router.register(r'view', views.ViewViewset, basename='view')