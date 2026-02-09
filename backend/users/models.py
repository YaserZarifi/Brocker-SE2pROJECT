import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model for BourseChain.
    Extends Django's AbstractUser with brokerage-specific fields.
    """

    class Role(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        ADMIN = "admin", "Admin"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.CUSTOMER)
    wallet_address = models.CharField(max_length=42, blank=True, null=True, help_text="Ethereum wallet address")
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    cash_balance = models.DecimalField(max_digits=15, decimal_places=2, default=10_000_000)

    # Use email as the login field
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        ordering = ["-date_joined"]
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.email})"
