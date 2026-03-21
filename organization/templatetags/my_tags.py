from django import template
from django.utils.safestring import mark_safe
from learning.models import Protocol, KnowledgeDate, Direction, Learner, ProtocolResult, ExamAssignment, BriefingDay, \
    ExamResult
from datetime import date
from django.utils import  timezone

from learning.services import get_current_date
from organization.models import Position

register = template.Library()


@register.filter()
def media_filter(path):
    if path:
        return f"/media/{path}"
    return "/media/other/no-img.png"


@register.filter()
def poster_page(value):
    return "/media/other/poster.jpg"



@register.filter()
def get_protocol_url(direction, learner):
    try:
        protocol = Protocol.objects.filter(program__direction=direction, learner=learner).order_by("-prot_date", "-id").first()
        if protocol and protocol.doc_scan:
            return protocol.doc_scan.url
        else:
            return False
    except Protocol.DoesNotExist:
        return False


@register.filter()
def get_protocol_date(direction, learner):
    try:
        protocol = Protocol.objects.filter(program__direction=direction, learner=learner).order_by("-prot_date", "-id").first()
        if protocol:
            return protocol.prot_date.strftime("%d.%m.%Y")
        else:
            return mark_safe('<span class="text-danger">Не проводилась</span>')
    except Protocol.DoesNotExist:
        return mark_safe('<span class="text-danger">Не проводилась</span>')


@register.filter()
def get_protocol_result(direction, learner):
    try:
        protocol = Protocol.objects.filter(program__direction=direction, learner=learner).order_by("-prot_date", "-id").first()
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
        protocol = Protocol.objects.filter(program__direction=direction, learner=learner).order_by("-prot_date", "-id").first()
        learner_direction = Learner.objects.get(pk=learner.pk).direction.all()
        if direction in learner_direction:
            knowledge_date = KnowledgeDate.objects.get(learner=learner, direction=direction, protocol=protocol, is_active=True).next_date.strftime("%d.%m.%Y")
            return mark_safe(f'<strong>{knowledge_date}</strong>')
        else:
            return mark_safe('<span class="text-muted">Не требуется</span>')
    except KnowledgeDate.DoesNotExist:
        return mark_safe(f'<span class="text-danger"><strong>{date.today().strftime("%d.%m.%Y")}</strong></span>')


@register.filter()
def get_direction_name(programs):
    directions_name = set()
    for program in programs:
        for direction in program.direction.all():
            directions_name.add(direction.name)
    return ", ".join(sorted(directions_name))


@register.filter()
def get_direction_name_for_one_program(program):
    directions_name = set()
    for direction in program.direction.all():
        directions_name.add(direction.name)
    return ", ".join(sorted(directions_name))


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


@register.filter()
def get_assignments(learner):
    assignments = ExamAssignment.objects.filter(
        learner=learner,
        status__in=['assigned',]
    ).select_related('exam')
    return assignments


@register.filter()
def date_delta(date_end):
    now = get_current_date()
    delta_date = date_end - now

    return delta_date.days


@register.filter()
def get_briefing(learner, briefing_type):
    briefing_day = BriefingDay.objects.filter(
        learner=learner,
        briefing_type=briefing_type
    ).order_by("-briefing_day", "-id").first()
    return briefing_day


@register.filter()
def get_nearest_knowledge_date(worker):
    leaners = worker.learner.all()
    knowledge_date = KnowledgeDate.objects.filter(
        learner__in=leaners,
        is_active=True,
        next_date__gte=get_current_date()
    ).order_by("next_date").first()
    if knowledge_date is not None:
        return knowledge_date.next_date
    else:
        return mark_safe('<span class="text">Данные не найдены</span>')


@register.filter()
def get_nearest_briefing_date(worker):
    leaners = worker.learner.all()
    briefing_day = BriefingDay.objects.filter(
        learner__in=leaners,
        is_active=True,
        next_briefing_day__gte=get_current_date()
    ).order_by("next_briefing_day").first()
    if briefing_day is not None:
        if briefing_day.next_briefing_day is not None:
            return briefing_day.next_briefing_day
    else:
        return mark_safe('<span class="text">Данные не найдены</span>')


@register.filter()
def get_last_test_for_briefing(briefing):
    briefing_program = briefing.briefing_program
    result = ExamResult.objects.filter(
        learner=briefing.learner,
        exam__briefing_program=briefing_program,
    ).order_by("-test_date").first()
    return result


@register.filter()
def get_exam_result(assignment):
    result = assignment.exam.results.filter(
        learner=assignment.learner,
        exam=assignment.exam
    ).exists()
    return result


@register.filter
def model_name(obj):
    return obj._meta.model_name


@register.filter
def briefing_type_name(names):
    name_list = []
    for name in names:
        name_list.append(str(name))
    return ", ".join(name_list)


@register.filter()
def get_direction_result(result, direction):
    res = result.filter(direction=direction)
    return res


@register.simple_tag(takes_context=True)
def modify_page_url(context, page_number):
    request = context['request']
    get_params = request.GET.copy()
    get_params['page'] = page_number
    return f"?{get_params.urlencode()}"
