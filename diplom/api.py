from rest_framework import routers
from educvideos import views

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')