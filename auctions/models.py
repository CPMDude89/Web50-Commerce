from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

# auction listings
class Listing(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField()
    image = models.FileField(upload_to="images")

    def __str__(self):
        return f"{self.name}"
