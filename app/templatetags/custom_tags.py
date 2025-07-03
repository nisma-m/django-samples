from django import template
from django.contrib.auth.models import User

register = template.Library()

@register.filter
def get_username(users, user_id):
    try:
        return users.get(id=user_id).username
    except User.DoesNotExist:
        return "Unknown User"
