from django.db import router
from rest_framework.routers import DefaultRouter
from django.urls import include, path
from . import views


app_name = 'Order'

# router  = DefaultRouter()
# router.register('', views.OrderAPIViewSet, basename='orders')

urlpatterns = [
    path('order/<int:product_id>/product', views.OrderAPIViewSet.as_view(),  name='order'),
]
