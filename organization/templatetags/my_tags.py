from django import template
from django.utils.safestring import mark_safe
from learning.models import Protocol, KnowledgeDate, Direction, Learner
from datetime import date
register = template.Library()


@register.filter()
def media_filter(path):
    if path:
        return f"/media/{path}"
    return "/media/other/no-img.png"


@register.filter()
def get_protocol_url(direction, learner):
    try:
        protocol = Protocol.objects.filter(direction=direction, learner=learner).latest("prot_date")
        return protocol.doc_scan.url
    except Protocol.DoesNotExist:
        return mark_safe('<div class="text-danger">Отсутствует</div>')


@register.filter()
def get_protocol_date(direction, learner):
    try:
        protocol = Protocol.objects.filter(direction=direction, learner=learner).latest("prot_date")
        return protocol.prot_date.strftime("%d.%m.%Y")
    except Protocol.DoesNotExist:
        return mark_safe('<div class="text-danger">Не проводилась</div>')


@register.filter()
def get_knowledge_date(direction, learner):
    try:
        learner_direction = Learner.objects.get(pk=learner.pk).direction.all()
        if direction in learner_direction:
            knowledge_date = KnowledgeDate.objects.filter(learner=learner, direction=direction).latest("kn_date").next_date.strftime("%d.%m.%Y")
            return knowledge_date
        else:
            return mark_safe('<div class="text-muted">Не требуется</div>')
    except KnowledgeDate.DoesNotExist:
        return mark_safe(f'<div class="text-danger">{date.today().strftime("%d.%m.%Y")}</div>')


@register.filter()
def get_direction_name(directions):
    directions_name = []
    for direction in directions:
        directions_name.append(direction.name)
    return ", ".join(directions_name)


@register.filter()
def get_learner_direction(direction, learner):
    try:
        learner_direction = Learner.objects.get(pk=learner.pk).direction.all()
        if direction in learner_direction:
            return get_protocol_date(direction, learner)
        else:
            return mark_safe('<div class="text-muted">Не назначено</div>')
    except Direction.DoesNotExist:
        return mark_safe('<div class="text">Ошибка данные не найдены</div>')
