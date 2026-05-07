from django.contrib import admin
from .models import Proyecto, Comentario


@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'estudiante', 'estado', 'calificacion', 'fecha_envio']
    list_filter = ['estado', 'fecha_envio']
    search_fields = ['titulo', 'estudiante__username']
    list_editable = ['estado', 'calificacion']


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ['proyecto', 'usuario', 'fecha']
    list_filter = ['fecha']
    search_fields = ['texto', 'usuario__username', 'proyecto__titulo']