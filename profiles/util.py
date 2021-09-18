import secrets
import string
from datetime import date

from .models import Profile


def generate_token(profile: Profile):
    profile.token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
    profile.save()


def get_age(profile: Profile):
    today = date.today()
    return today.year - profile.birthdate.year - ((today.month, today.day) < (profile.birthdate.month, profile.birthdate.day))
