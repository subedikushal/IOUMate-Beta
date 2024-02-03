from api.models import User, EmailVerificationToken
from django.utils import timezone
def message(msg, success, other=None):
    if other is None:
        other = {}
    return {'message': msg, 'success': success, 'data': other}


def delete_expired_objects():
    EmailVerificationToken.objects.filter(
        created_at__lt=timezone.now() - timezone.timedelta(minutes=1)).to_be_verified_users.delete()
