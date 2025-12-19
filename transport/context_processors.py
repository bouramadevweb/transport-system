from .models import Notification, Mission


def notifications_processor(request):
    """
    Context processor pour fournir les notifications et le compte des missions en cours
    à tous les templates
    """
    if request.user.is_authenticated:
        # Récupérer les notifications non lues (limitées à 5 pour le dropdown)
        notifications = Notification.objects.filter(
            utilisateur=request.user,
            is_read=False
        )[:5]

        # Compter toutes les notifications non lues
        notifications_count = Notification.objects.filter(
            utilisateur=request.user,
            is_read=False
        ).count()

        # Compter les missions en cours
        missions_en_cours_count = Mission.objects.filter(
            statut='en cours'
        ).count()

        return {
            'notifications': notifications,
            'notifications_count': notifications_count,
            'missions_en_cours_count': missions_en_cours_count,
        }
    else:
        return {
            'notifications': [],
            'notifications_count': 0,
            'missions_en_cours_count': 0,
        }
