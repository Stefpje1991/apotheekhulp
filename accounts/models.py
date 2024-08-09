from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, first_name, last_name, email, role, password=None):
        if not email:
            raise ValueError("User moet een mailadres hebben")

        email = self.normalize_email(email)
        username = email  # Assign username directly from email
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            username=username,  # Ensure username is set here
            role=role
        )
        user.set_password(password)
        user.is_active = True
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, email, username, role, password=None):
        user = self.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            role=User.ADMIN  # Use the defined constant for the role
        )
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    ASSISTENT = 1
    APOTHEEK = 2
    ADMIN = 3

    ROLE = (
        (ASSISTENT, 'Assistent'),
        (APOTHEEK, 'Apotheek'),
        (ADMIN, 'Admin')
    )

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.EmailField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    role = models.PositiveSmallIntegerField(choices=ROLE, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role']

    objects = UserManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return True

    def get_role_display(self):
        return dict(self.ROLE).get(self.role, 'Unknown')


class Assistent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    assistent_btwNummer = models.CharField(max_length=50, null=True, blank=True)
    assistent_btwPlichtig = models.BooleanField(default=True)
    assistent_naamBedrijf = models.CharField(max_length=200, null=True, blank=True)
    assistent_straatBedrijf = models.CharField(max_length=200, null=True, blank=True)
    assistent_huisnummerBedrijf = models.CharField(max_length=10, null=True, blank=True)
    assistent_postcodeBedrijf = models.CharField(max_length=10, null=True, blank=True)
    assistent_stadBedrijf = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Apotheek(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # Add other fields as required
    apotheek_btwNummer = models.CharField(max_length=50, null=True, blank=True)
    apotheek_btwPlichtig = models.BooleanField(default=True)
    apotheek_naamBedrijf = models.CharField(max_length=200, null=True, blank=True)
    apotheek_straatBedrijf = models.CharField(max_length=200, null=True, blank=True)
    apotheek_huisnummerBedrijf = models.CharField(max_length=10, null=True, blank=True)
    apotheek_postcodeBedrijf = models.CharField(max_length=10, null=True, blank=True)
    apotheek_stadBedrijf = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.apotheek_naamBedrijf