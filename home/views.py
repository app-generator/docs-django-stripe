import stripe
import json
from django.shortcuts import render, get_object_or_404
from datetime import datetime
from home.models import Product
from django.conf import settings
from django.http import JsonResponse, Http404, HttpResponse
from django.views.decorators.csrf import csrf_exempt

stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.

from .models import *

def index(request):
    products = Product.objects.all()
    stripe_products = stripe.Product.list(expand=["data.default_price"])

    one_off_products = []
    recurring_products = []

    for product in stripe_products.data:
        if product.default_price.type == "one_time":
            one_off_products.append(product)
        elif product.default_price.type == "recurring":
            recurring_products.append(product)

    context = {
        'products': products,
        'one_off_products': one_off_products,
        'recurring_products': recurring_products,
        'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY
    }
    return render(request, 'index.html', context)


@csrf_exempt
def create_checkout_session(request, product_id):
    try:
        data = json.loads(request.body)
        price = data.get('price')
        if product_id.startswith("prod_"):
            stripe_product = stripe.Product.retrieve(product_id, expand=["default_price"])
            default_price = stripe_product.default_price

            mode = 'subscription' if default_price.type == "recurring" else 'payment'

            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': default_price.id,
                    'quantity': 1,
                }],
                mode=mode,
                success_url=request.build_absolute_uri('/success/'),
                cancel_url=request.build_absolute_uri('/cancel/'),
            )
        else:
            product = get_object_or_404(Product, id=product_id)
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': product.name,
                        },
                        'unit_amount': int(price * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=request.build_absolute_uri('/success/'),
                cancel_url=request.build_absolute_uri('/cancel/'),
            )

        return JsonResponse({'id': session.id})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    

def payment_success(request):
    return HttpResponse("Payment success!")

def payment_cancel(request):
    return HttpResponse("Payment cancelled!")