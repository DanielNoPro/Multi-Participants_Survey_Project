import logging

from django.contrib.auth.base_user import BaseUserManager


class PasswordlessUserAccountManager(BaseUserManager):

    def create_superuser(self, username, email, phone_number, password, **other_fields):
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError('Superuser must be assigned to is_staff=True')

        if other_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must be assigned to is_superuser=True')
        user = self.create_user(username, email, phone_number, password, **other_fields)
        user.set_password(password)
        user.save()
        return user

    def create_user(self, username, email, phone_number, password, **other_fields):
        logging.info("Create user")
        other_fields.setdefault('is_active', True)
        if not email:
            raise ValueError('Email address is required!')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, phone_number=phone_number, password=password, **other_fields)
        if password is None:
            user.set_unusable_password()
        user.save()
        return user
