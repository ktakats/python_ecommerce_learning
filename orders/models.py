from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import pre_save, post_save
import math
from carts.models import Cart
from billing.models import BillingProfile
from udemy_ecomm.utils import unique_order_id_generator
from addresses.models import Address
from products.models import Product

# Create your models here.

ORDER_STATUS_CHOICES =(
    ('created', 'Created'),
    ('paid', 'Paid'),
    ('shipped', 'Shipped'),
    ('refunded', 'Refunded')
)

class OrderManagerQuerySet(models.query.QuerySet):
    def by_request(self, request):
        my_profile, created = BillingProfile.objects.new_or_get(request)
        return self.filter(billing_profile=my_profile)

    def not_created(self):
        return self.exclude(status='created')

class OrderManager(models.Manager):
    def get_queryset(self):
        return OrderManagerQuerySet(self.model, using=self._db)

    def by_request(self, request):
        return self.get_queryset().by_request(request)

    def new_or_get(self, billing_profile, cart_obj):
        qs = self.get_queryset().filter(billing_profile=billing_profile, cart=cart_obj, active=True, status="created")
        created = False
        if qs.count() == 1:
            obj = qs.first()
        else:
            obj = self.model.objects.create(billing_profile=billing_profile, cart=cart_obj)
            created = True
        return obj, created

class Order(models.Model):
    order_id = models.CharField(max_length=120, blank=True) #Random, unique id
    billing_profile = models.ForeignKey(BillingProfile, null=True, blank=True)
    shipping_address = models.ForeignKey(Address, related_name="shipping_address", null=True, blank=True)
    billing_address = models.ForeignKey(Address, related_name="billing_address", null=True, blank=True)
    cart = models.ForeignKey(Cart)
    status = models.CharField(max_length=120, default="created", choices=ORDER_STATUS_CHOICES)
    shipping_total = models.DecimalField(default=5.99, max_digits=100, decimal_places=2)
    total = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)

    objects=OrderManager()

    class Meta:
        ordering = ['-timestamp', '-updated']

    def __str__(self):
        return self.order_id

    def get_absolute_url(self):
        return reverse("orders:detail", kwargs={'order_id': self.order_id})

    def get_status(self):
        if self.status == "refunded":
            return "Refunded"
        elif self.status == "shipped":
            return "Shipped"
        return "Shipping soon"

    def update_total(self):
        cart_total=self.cart.total
        shipping_total=self.shipping_total
        total = format(math.fsum([cart_total, shipping_total]), '.2f')
        self.total = total
        self.save()
        return total

    def check_done(self):
        billing_profile = self.billing_profile
        shipping_address = self.shipping_address
        billing_address = self.billing_address
        total = self.total
        if billing_profile and billing_address and (shipping_address or self.cart.is_digital) and total>0:
            return True
        return False

    def update_purchases(self):
        for p in self.cart.products.all():
            obj, created = ProductPurchase.objects.get_or_create(
                order_id=self.order_id,
                product=p,
                billing_profile=self.billing_profile
            )
        return ProductPurchase.objects.filter(order_id=self.order_id).count()

    def mark_paid(self):
        if self.status != 'paid':
            if self.check_done():
                self.status = "paid"
                self.save()
                self.update_purchases()
        return self.status


def pre_save_create_order_id(sender, instance, *args, **kwargs):
    if not instance.order_id:
        instance.order_id = unique_order_id_generator(instance)
    qs=Order.objects.filter(cart=instance.cart).exclude(billing_profile=instance.billing_profile)
    if qs.exists():
        qs.update(active=False)

pre_save.connect(pre_save_create_order_id, sender=Order)

def post_save_cart_total(sender, instance, created, *args, **kwargs):
    cart_obj = instance
    cart_total = cart_obj.total
    cart_id = cart_obj.id
    qs = Order.objects.filter(cart__id=cart_id)
    if qs.count()==1:
        order_obj=qs.first()
        order_obj.update_total()

post_save.connect(post_save_cart_total, sender=Cart)

def post_save_order(sender, instance, created, *args, **kwargs):
    if created:
        instance.update_total()

post_save.connect(post_save_order, sender=Order)

class ProductPurchaseQuerySet(models.query.QuerySet):
    def active(self):
        return self.filter(refunded=False)

    def digital(self):
        return self.filter(product__is_digital=True)

    def by_request(self, request):
        my_profile, created = BillingProfile.objects.new_or_get(request)
        return self.filter(billing_profile=my_profile)

class ProductPurchaseManager(models.Manager):
    def get_queryset(self):
        return ProductPurchaseQuerySet(self.model, using=self._db)

    def all(self):
        return self.get_queryset().active()

    def digital(self):
        return self.get_queryset().active().digital()

    def by_request(self, request):
        return self.get_queryset().by_request(request)

    def products_by_request(self, request):
        qs = self.by_request(request).digital()
        ids_=[x.product.id for x in qs]
        products_qs=Product.objects.filter(id__in=ids_).distinct()
        return products_qs

class ProductPurchase(models.Model):
    billing_profile = models.ForeignKey(BillingProfile)
    order_id = models.CharField(max_length=120)
    product = models.ForeignKey(Product)
    refunded = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = ProductPurchaseManager()

    def __str__(self):
        return self.product.title