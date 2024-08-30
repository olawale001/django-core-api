from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views


app_name = 'auth'

router = DefaultRouter()
router.register('signup', views.SignUpUserAPI, basename='signup')
router.register('auth', views.AuthenticationViewset, basename='auth_views')

urlpatterns = [
    path('', include(router.urls)),
    path('login', views.LonginUserApi.as_view(), name='login'),
]