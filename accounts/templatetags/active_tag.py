from django import template

register = template.Library()


@register.simple_tag
def active(request, url_name):
    from django.urls import reverse, resolve
    try:
        url = reverse(url_name)
    except:
        url = url_name
    path = request.path
    if path == url:
        return "active"
    return ""
