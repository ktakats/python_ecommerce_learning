from django.shortcuts import render
from decouple import config
from django.http import JsonResponse,HttpResponse
from django.utils.http import is_safe_url

import stripe
stripe.api_key = config('STRIPE_API_KEY')


def payment_method_view(request):
    next_url = None
    next_ = request.GET.get('next')
    if is_safe_url(next_):
        next_url = next_
    return render(request, 'billing/payment-method.html', {"publish_key": config('STRIPE_PUB_KEY'), "next_url": next_url})

def payment_method_createview(request):
    print(request)
    print(request.method)
    print(request.is_ajax())
    if request.method=="POST" and request.is_ajax():
        print("bla")
        return JsonResponse({"message": "Success! Your card was added."})
    return HttpResponse('error', status=401)