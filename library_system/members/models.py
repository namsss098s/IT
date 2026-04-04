from django.db import models


class Member(models.Model):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    )

    fullname = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    is_disabled = models.BooleanField(default=False)

    def __str__(self):
        return self.fullname