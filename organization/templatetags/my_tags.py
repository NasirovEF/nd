from django import template

from learning.models import Protocol

register = template.Library()


@register.filter()
def media_filter(path):
    if path:
        return f"/media/{path}"
    return "/media/other/no-img.png"


@register.filter()
def slice_description(text):
    if len(text) >= 70:
        return f"{text[0:70]}..."
    else:
        return text


@register.filter()
def get_protocol(direction, learner):
    protocol = Protocol.objects.filter(direction=direction, learner=learner).latest("date")
    return protocol


@register.filter()
def get_direction_name(directions):
    directions_name = []
    for direction in directions:
        directions_name.append(direction.name)
    return ", ".join(directions_name)
