import base64

from cryptography.fernet import Fernet, MultiFernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils.encoding import force_bytes, force_str
from django.utils.functional import cached_property


class FernetSettings:
    @cached_property
    def keys(self):
        keys = getattr(settings, 'FERNET_KEYS', [])
        if len(keys) == 0:
            raise ImproperlyConfigured(f'settings.FERNET_KEYS array does not exist or has zero entries.')

        if getattr(settings, 'FERNET_USE_KDF', True):
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=settings.SECRET_KEY.encode('utf-8'),
                iterations=100000
            )

            return [base64.urlsafe_b64encode(kdf.derive(force_bytes(key))) for key in keys]

        return keys

    @cached_property
    def fernet(self):
        if len(self.keys) == 1:
            return Fernet(self.keys[0])
        return MultiFernet([Fernet(key) for key in self.keys])


class EncryptedField(models.Field):

    settings = FernetSettings()

    def __init__(self, *args, **kwargs):
        if kwargs.get('primary_key'):
            raise ImproperlyConfigured(f'{self.__class__.__name__} does not support primary_key.')
        if kwargs.get('unique'):
            raise ImproperlyConfigured(f'{self.__class__.__name__} does not support unique.')
        if kwargs.get('db_index'):
            raise ImproperlyConfigured(f'{self.__class__.__name__} does not support db_index.')
        super().__init__(*args, **kwargs)

    def get_internal_type(self):
        return 'BinaryField'

    def get_db_prep_save(self, value, connection):
        value = super().get_db_prep_save(value, connection)
        if value is not None:
            encrypted_value = EncryptedField.settings.fernet.encrypt(force_bytes(value))
            return connection.Database.Binary(encrypted_value)
        return value

    def from_db_value(self, value, expression, connection):
        if value is not None:
            decrypted_value = force_str(EncryptedField.settings.fernet.decrypt(value))

            parent = super()
            if hasattr(parent, 'from_db_value'):
                return parent.from_db_value(decrypted_value, expression, connection)

            return decrypted_value
        return value


class EncryptedCharField(EncryptedField, models.CharField):
    pass


class EncryptedTextField(EncryptedField, models.TextField):
    pass


class EncryptedJSONField(EncryptedField, models.JSONField):
    pass


# Deregister all existing field lookups, except isnull
for encrypted_field in [EncryptedField, EncryptedCharField, EncryptedTextField]:
    for lookup_name in encrypted_field.get_lookups().keys():
        if lookup_name != 'isnull':
            encrypted_field.register_lookup(None, lookup_name)
