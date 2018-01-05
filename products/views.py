from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.shortcuts import render, get_object_or_404
from django.http import Http404
from .models import Product
from analytics.mixins import ObjectViewedMixin
from carts.models import Cart
# Create your views here.


class UserProductHistoryView(LoginRequiredMixin, ListView):
    template_name = "products/user-history.html"

    def get_context_data(self, *args, **kwargs):
        context = super(UserProductHistoryView, self).get_context_data(*args, **kwargs)
        cart_obj, new_obj = Cart.objects.new_or_get(self.request)
        context['cart'] = cart_obj
        return context

    def get_queryset(self, *args, **kwargs):
        request = self.request
        views = request.user.objectviewed_set.by_model(Product)
        return views

class ProductListView(ListView):
    queryset = Product.objects.all()
    template_name = "products/list.html"

    def get_context_data(self, *args, **kwargs):
        context = super(ProductListView,self).get_context_data(*args, **kwargs)
        cart_obj, new_obj = Cart.objects.new_or_get(self.request)
        context['cart'] = cart_obj
        return context

def product_list_view(request):
    queryset = Product.objects.all()
    context = {
        'object_list': queryset
    }
    return render(request, "products/list.html", context)

class ProductFeaturedListView(ListView):
    template_name = "products/list.html"

    def get_queryset(self, *args, **kwargs):
        request=self.request
        return Product.objects.featured()


class ProductDetailSlugView(ObjectViewedMixin, DetailView):
    queryset = Product.objects.all()
    template_name = "products/detail.html"

    def get_context_data(self, *args, **kwargs):
        context = super(ProductDetailSlugView, self).get_context_data(*args, **kwargs)
        request=self.request
        cart_obj, new_obj = Cart.objects.new_or_get(request)
        context['cart'] = cart_obj
        return context

    def get_object(self, *args, **kwargs):
        request=self.request
        slug=self.kwargs.get('slug')
        try:
            instance = Product.objects.get(slug=slug)
        except Product.DoesNotExist:
            raise Http404("Not found...")
        except Product.MultipleObjectsReturned:
            qs=Product.objects.filter(slug=slug)
            instance=qs.first()
        except:
            raise Http404("Hmmm.")
        #object_viewed_signal.send(instance.__class__, instance=instance, request=request)
        return instance

class ProductDetailView(ObjectViewedMixin, DetailView):
    #queryset = Product.objects.all()
    template_name = "products/detail.html"

    def get_context_data(self, *args, **kwargs):
        context = super(ProductDetailView, self).get_context_data(*args, **kwargs)
        print(context)
        return context

    def get_object(self, *args, **kwargs):
        request=self.request
        pk =self.kwargs.get('pk')
        instance = Product.objects.get_by_id(pk)
        if instance is None:
            raise Http404("Product does not exist")
        return instance

def product_detail_view(request, pk):

    instance = Product.objects.get_by_id(pk)
    if instance is None:
        raise Http404("Product does not exist")


    context = {
        'object': instance
    }
    return render(request, "products/detail.html", context)

class ProductFeaturedDetailView(ObjectViewedMixin, DetailView):
    template_name = "products/featured-detail.html"

    def get_queryset(self, *args, **kwargs):
        request = self.request
        return Product.objects.featured()