from django.db import models

# Create your models here.


class Color(models.Model):
    name = models.CharField(max_length=255, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='product')
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    colors = models.ManyToManyField(Color, blank=True)

    def __str__(self):
        return self.name


