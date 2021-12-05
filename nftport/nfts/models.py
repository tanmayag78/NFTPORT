from django.db import models
from django.core.files.base import ContentFile


# Create your models here.


class NftData(models.Model):
    contract_address = models.TextField()
    token_id = models.BigIntegerField()
    name = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(null=True, blank=True)
    image_uri = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='images/', null=True, blank=True)

    class Meta:
        unique_together = ('contract_address', 'token_id')
