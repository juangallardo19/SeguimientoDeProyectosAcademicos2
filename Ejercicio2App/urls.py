from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('', views.ProyectoListView.as_view(), name='proyecto-list'),
    path('proyectos/', views.ProyectoListView.as_view(), name='proyecto-list'),
    path('proyectos/nuevo/', views.ProyectoCreateView.as_view(), name='proyecto-create'),
]