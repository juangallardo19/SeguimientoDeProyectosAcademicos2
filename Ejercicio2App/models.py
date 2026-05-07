from django.db import models
from django.contrib.auth.models import User


class Proyecto(models.Model):
    ESTADO_CHOICES = [
        ('enviado', 'Enviado'),
        ('revision', 'En Revisión'),
        ('aprobado', 'Aprobado'),
    ]

    titulo = models.CharField(max_length=200, verbose_name='Título')
    descripcion = models.TextField(verbose_name='Descripción')
    estudiante = models.ForeignKey(
        User,
        related_name='proyectos',
        on_delete=models.CASCADE,
        verbose_name='Estudiante'
    )
    documento = models.FileField(
        upload_to='proyectos/',
        blank=True,
        null=True,
        verbose_name='Documento PDF'
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='enviado',
        verbose_name='Estado'
    )
    fecha_envio = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de envío')
    fecha_revision = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de revisión')
    calificacion = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Calificación'
    )

    class Meta:
        ordering = ['-fecha_envio']
        verbose_name = 'Proyecto'
        verbose_name_plural = 'Proyectos'

    def __str__(self):
        return self.titulo

    def comentarios_activos(self):
        return self.estado != 'aprobado'


class Comentario(models.Model):
    proyecto = models.ForeignKey(
        Proyecto,
        related_name='comentarios',
        on_delete=models.CASCADE,
        verbose_name='Proyecto'
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Usuario'
    )
    texto = models.TextField(verbose_name='Comentario')
    fecha = models.DateTimeField(auto_now_add=True, verbose_name='Fecha')

    class Meta:
        ordering = ['fecha']
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'

    def __str__(self):
        return f'Comentario de {self.usuario.username} - {self.proyecto.titulo}'