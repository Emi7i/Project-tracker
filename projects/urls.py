from django.urls import path
from . import views

urlpatterns = [
    path('', views.project_list, name='project_list'),
    path('create/', views.project_create, name='project_create'),
    path('update/<int:pk>/', views.project_update, name='project_update'),
    path('delete/<int:pk>/', views.project_delete, name='project_delete'),
    path('api/project/<int:pk>/', views.project_detail_api, name='project_detail_api'),
    path('reorder/', views.reorder_projects, name='reorder_projects'),
    path('update-status/<int:pk>/', views.update_project_status, name='update_project_status'),
]
