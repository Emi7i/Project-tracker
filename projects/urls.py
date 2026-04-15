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
    path('update-priority/<int:pk>/', views.update_project_priority, name='update_project_priority'),
    path('set-sort/', views.set_sort, name='set_sort'),
    path('set-group/', views.set_group, name='set_group'),
    path('swap-type-order/', views.swap_type_order, name='swap_type_order'),
    path('settings/', views.settings_view, name='settings'),
    path('settings/create-profile/', views.create_profile, name='create_profile'),
    path('settings/activate-profile/<int:profile_id>/', views.activate_profile, name='activate_profile'),
    path('settings/delete-profile/<int:profile_id>/', views.delete_profile, name='delete_profile'),
    path('settings/create-type-definition/', views.create_type_definition, name='create_type_definition'),
    path('settings/create-status-definition/', views.create_status_definition, name='create_status_definition'),
    path('settings/create-priority-definition/', views.create_priority_definition, name='create_priority_definition'),
    path('settings/reorder-type-definitions/', views.reorder_type_definitions, name='reorder_type_definitions'),
    path('settings/reorder-status-definitions/', views.reorder_status_definitions, name='reorder_status_definitions'),
    path('settings/reorder-priority-definitions/', views.reorder_priority_definitions, name='reorder_priority_definitions'),
    path('settings/delete-type-definition/<int:def_id>/', views.delete_type_definition, name='delete_type_definition'),
    path('settings/delete-status-definition/<int:def_id>/', views.delete_status_definition, name='delete_status_definition'),
    path('settings/delete-priority-definition/<int:def_id>/', views.delete_priority_definition, name='delete_priority_definition'),
]
