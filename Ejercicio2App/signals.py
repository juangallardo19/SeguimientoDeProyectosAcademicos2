from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Comentario


@receiver(post_save, sender=Comentario)
def notificar_nuevo_comentario(sender, instance, created, **kwargs):
    if not created:
        return

    proyecto = instance.proyecto
    estudiante = proyecto.estudiante
    comentador = instance.usuario

    if comentador == estudiante:
        return

    if not estudiante.email:
        return

    asunto = f'[Ejercicio2] Nuevo comentario en "{proyecto.titulo}"'
    mensaje = f'''
Hola {estudiante.get_full_name() or estudiante.username},

{comentador.get_full_name() or comentador.username} dejó un comentario en tu proyecto:

"{instance.texto}"

Puedes revisar tu proyecto en la plataforma.

Saludos,
Sistema de Seguimiento de Proyectos Académicos
'''.strip()

    try:
        send_mail(
            subject=asunto,
            message=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[estudiante.email],
            fail_silently=True,
        )
    except Exception as e:
        print(f'Error enviando correo: {e}')