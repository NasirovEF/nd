from django import template
from django.utils.safestring import mark_safe
from learning.models import Protocol, KnowledgeDate
from datetime import date
register = template.Library()


@register.filter()
def media_filter(path):
    if path:
        return f"/media/{path}"
    return "/media/other/no-img.png"


@register.filter()
def get_protocol(direction, learner):
    try:
        protocol = Protocol.objects.filter(direction=direction, learner=learner).latest("date")
        return protocol
    except Protocol.DoesNotExist:
        return mark_safe('<div class="text-danger">Не проводилась</div>')


@register.filter()
def get_knowledge_date(direction, learner):
    try:
        knowledge_date = KnowledgeDate.objects.filter(learner=learner, direction=direction).latest("date").next_date()
        return knowledge_date
    except KnowledgeDate.DoesNotExist:
        return mark_safe(f'<div class="text-danger">{date.today().strftime("%d.%m.%Y")}</div>')


@register.filter()
def get_direction_name(directions):
    directions_name = []
    for direction in directions:
        directions_name.append(direction.name)
    return ", ".join(directions_name)
