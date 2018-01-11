from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, JsonResponse
from django.views.generic import ListView, DetailView, View

from billing.models import BillingProfile

from .models import Order, ProductPurchase

class OrderListView(LoginRequiredMixin, ListView):

    def get_queryset(self):
        return Order.objects.by_request(self.request).not_created()

class OrderDetailView(LoginRequiredMixin, DetailView):

    def get_object(self):
        qs = Order.objects.by_request(self.request).filter(order_id=self.kwargs.get('order_id')).not_created()
        if qs.count()==1:
            return qs.first()
        raise Http404

class LibraryView(LoginRequiredMixin, ListView):
    template_name = 'orders/library.html'

    def get_queryset(self):
        return ProductPurchase.objects.products_by_request(self.request)

class VerifyOwnership(View):
    def get(self, request, *args, **kwargs):
        print(request)
        if request.is_ajax():
            data = request.GET
            product_id = data.get('product_id')
            ownership_ids = ProductPurchase.objects.products_by_id(request)
            if int(product_id) in ownership_ids:
                return JsonResponse({'owner': True})
            return JsonResponse({'owner': False})
        raise Http404