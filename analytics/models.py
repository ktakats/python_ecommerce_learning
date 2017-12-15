from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from .signals import object_viewed_signal
from .utils import get_client_ip
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

def object_viewed_receiver(sender, instance, request, *args, **kwargs):
    c_type = ContentType.objects.get_for_model(sender) # instance.__class__
    new_view_obj = ObjectViewed.objects.create(
        user = request.user,
        ip_address = get_client_ip(request),
        content_type = c_type,
        object_id = instance.id
    )

object_viewed_signal.connect(object_viewed_receiver)