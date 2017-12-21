from django.shortcuts import render, redirect
from decouple import config
from django.http import JsonResponse,HttpResponse
from django.utils.http import is_safe_url

from .models import BillingProfile, Card

import stripe
stripe.api_key = config('STRIPE_API_KEY')


def payment_method_view(request):
    billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
    if not billing_profile:
        return redirect("/cart")
    next_url = None
    next_ = request.GET.get('next')
    if is_safe_url(next_):
        next_url = next_
    return render(request, 'billing/payment-method.html', {"publish_key": config('STRIPE_PUB_KEY'), "next_url": next_url})

def payment_method_createview(request):
    if request.method=="POST" and request.is_ajax():
        billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
        if not billing_profile:
            return HttpResponse({"message": "Cannot find user"}, status=404)
        token = request.POST.get('token')
        if token is not None:
            customer = stripe.Customer.retrieve(billing_profile.customer_id)
            card_response = customer.sources.create(source=token)
            new_card_obj=Card.objects.add_new(billing_profile=billing_profile, stripe_card_response=card_response)
        return JsonResponse({"message": "Success! Your card was added."})
    return HttpResponse('error', status=401)