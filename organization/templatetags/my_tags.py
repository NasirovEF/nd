from django import template
from django.utils.safestring import mark_safe
from learning.models import Protocol, KnowledgeDate, Direction, Learner, ProtocolResult
from datetime import date

from organization.models import Position

register = template.Library()


@register.filter()
def media_filter(path):
    if path:
        return f"/media/{path}"
    return "/media/other/no-img.png"


@register.filter()
def get_protocol_url(direction, learner):
    try:
        protocol = Protocol.objects.filter(direction=direction, learner=learner).order_by("-prot_date", "-id").first()
        if protocol and protocol.doc_scan:
            return protocol.doc_scan.url
        else:
            return False
    except Protocol.DoesNotExist:
        return False


@register.filter()
def get_protocol_date(direction, learner):
    try:
        protocol = Protocol.objects.filter(direction=direction, learner=learner).order_by("-prot_date", "-id").first()
        if protocol:
            return protocol.prot_date.strftime("%d.%m.%Y")
        else:
            return mark_safe('<span class="text-danger">Не проводилась</span>')
    except Protocol.DoesNotExist:
        return mark_safe('<span class="text-danger">Не проводилась</span>')


@register.filter()
def get_protocol_result(direction, learner):
    try:
        protocol = Protocol.objects.filter(direction=direction, learner=learner).order_by("-prot_date", "-id").first()
        if protocol:
            result = protocol.protocol_result.get(learner=learner)
            return result.passed
        else:
            False
    except (Protocol.DoesNotExist, ProtocolResult.DoesNotExist):
        return False


@register.filter()
def get_knowledge_date(direction, learner):
    try:
        protocol = Protocol.objects.filter(direction=direction, learner=learner).order_by("-prot_date", "-id").first()
        learner_direction = Learner.objects.get(pk=learner.pk).direction.all()
        if direction in learner_direction:
            knowledge_date = KnowledgeDate.objects.get(learner=learner, direction=direction, protocol=protocol, is_active=True).next_date.strftime("%d.%m.%Y")
            return mark_safe(f'<strong>{knowledge_date}</strong>')
        else:
            return mark_safe('<span class="text-muted">Не требуется</span>')
    except KnowledgeDate.DoesNotExist:
        return mark_safe(f'<span class="text-danger"><strong>{date.today().strftime("%d.%m.%Y")}</strong></span>')


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
            return mark_safe('<span class="text-muted">Не назначено</span>')
    except Direction.DoesNotExist:
        return mark_safe('<span class="text">Ошибка данные не найдены</span>')


@register.filter()
def get_main_position(worker):
    main_position = Position.objects.get(worker=worker, is_main=True)
    return main_position


@register.filter()
def get_extra_position(worker):
    positions = []
    worker_extra_position = Position.objects.filter(worker=worker, is_main=False)
    for position in worker_extra_position:
        positions.append(str(position))
    if len(positions) > 0:
        return ", ".join(positions)
    else:
        return "отсутствует"
