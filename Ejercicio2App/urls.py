from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('', views.ProyectoListView.as_view(), name='proyecto-list'),
    path('proyectos/', views.ProyectoListView.as_view(), name='proyecto-list'),
    path('proyectos/nuevo/', views.ProyectoCreateView.as_view(), name='proyecto-create'),
    path('proyectos/<int:pk>/', views.ProyectoDetailView.as_view(), name='proyecto-detail'),
    path('proyectos/<int:pk>/editar/', views.ProyectoUpdateView.as_view(), name='proyecto-update'),
    path('proyectos/<int:pk>/eliminar/', views.ProyectoDeleteView.as_view(), name='proyecto-delete'),
    path('proyectos/<int:pk>/docente/', views.docente_actualizar_proyecto, name='docente-actualizar'),
]