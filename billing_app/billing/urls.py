from django.urls import path
from . import views

urlpatterns = [
    path('', views.item_list, name='item_list'),
    path('external-update/', views.external_update_item, name='external_update_item'),
    path('fetch-items/', views.fetch_items, name='fetch_items'),
    path('check-notifications/', views.check_notifications, name='check_notifications'),
]
