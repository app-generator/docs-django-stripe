from django import template

register = template.Library()

@register.filter
def convert_stripe_price(price):
    return price / 100 if price else 0