from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
# Create your models here.

User = settings.AUTH_USER_MODEL

class ObjectViewed(models.Model):
    user = models.ForeignKey(User, blank=True, null=True)
    ip_address = models.CharField(max_length=220, blank=True, null=True)
    content_type = models.ForeignKey(ContentType) #Product, Order, Cart, Address etc.
    object_id = models.PositiveIntegerField() # Product id, Order id etc
    content_object = GenericForeignKey('content_type', 'object_id') #Product instance etc
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s viewed on %s" % (self.content_object, self.timestamp)

    class Meta:
        ordering = ['-timestamp'] # most recent first
        verbose_name = 'Object viewed'
        verbose_name_plural = 'Objects viewed'