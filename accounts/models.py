from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import random

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    USER_TYPES = (
        ('organization', 'Organization'),
        ('student', 'Student'),
    )
    name = models.CharField(max_length=255)
    age = models.PositiveIntegerField()
    education = models.CharField(max_length=255)
    profession = models.CharField(max_length=50, choices=(('fresher','Fresher'),('experienced','Experienced')))
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'age', 'education', 'profession', 'user_type']

    objects = UserManager()

    def __str__(self):
        return self.email

    def generate_otp(self):
        otp = f"{random.randint(100000, 999999)}"
        self.otp = otp
        self.save()
        return otp