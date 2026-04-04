from django.contrib.auth.models import User
from django.db import models


class StaffProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    is_manager = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username