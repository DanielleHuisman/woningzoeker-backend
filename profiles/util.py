import secrets
import string

from .models import Profile


def generate_token(profile: Profile):
    profile.token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
    profile.save()
