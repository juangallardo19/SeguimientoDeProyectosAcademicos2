def user_role(request):
    if not request.user.is_authenticated:
        return {'es_docente': False}
    return {
        'es_docente': (
            request.user.groups.filter(name='docente').exists()
            or request.user.is_staff
            or request.user.is_superuser
        )
    }
