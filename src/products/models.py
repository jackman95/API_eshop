from django.db import models

class AttributeName(models.Model):
    nazev = models.CharField(max_length=255, blank=False)
    kod = models.CharField(max_length=255, blank=True)
    zobrazit = models.BooleanField(default=False)

class AttributeValue(models.Model):
    hodnota = models.CharField(max_length=255, blank=False)

class Attribute(models.Model):
    nazev_atributu = models.ForeignKey(AttributeName, on_delete=models.CASCADE, null=False, blank=False)
    hodnota_atributu = models.ForeignKey(AttributeValue, on_delete=models.CASCADE, null=False, blank=False)

class Product(models.Model):
    nazev = models.CharField(max_length=255, blank=False)
    description = models.TextField(blank=True)
    cena = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    mena = models.CharField(max_length=10, blank=False)
    published_on = models.DateTimeField(null=True, blank=True)
    is_published = models.BooleanField(default=False)

class ProductAttributes(models.Model):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, null=False, blank=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=False, blank=False)

class Image(models.Model):
    obrazek = models.URLField(null=False)
    nazev = models.CharField(max_length=255, blank=True)

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=False)
    obrazek = models.ForeignKey(Image, on_delete=models.CASCADE, null=False)
    nazev = models.CharField(max_length=255, blank=True)

class Catalog(models.Model):
    nazev = models.CharField(max_length=255, blank=False)
    obrazek = models.ForeignKey(Image, on_delete=models.CASCADE, null=True, blank=True)
    products = models.ManyToManyField(Product, blank=False)
    attributes = models.ManyToManyField(Attribute, blank=False)
