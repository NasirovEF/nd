from django.http import HttpResponse
from docxtpl import DocxTemplate
import io
from django.http import HttpResponseNotFound
from learning.models import Protocol, Learner
from django.conf import settings
from pathlib import Path


def generate_identity(request, pk):
    try:
        learner = Learner.objects.get(pk=pk)
    except Learner.DoesNotExist:
        return HttpResponseNotFound("Работник не найден")
    knowledge_dates = learner.knowledge_date.filter(is_active=True)
    identity_date = knowledge_dates.order_by("-kn_date").first()
    context = {
        'learner': learner,
        'knowledge_dates': knowledge_dates,
        'identity_date': identity_date,
    }

    template_path = Path(settings.BASE_DIR) / "patterns" / "identity_template.docx"

    if not template_path.exists():
        return HttpResponse("Шаблон не найден", status=500)

    try:
        doc = DocxTemplate(str(template_path))
        doc.render(context)
    except Exception as e:
        return HttpResponse(f"Ошибка при генерации документа: {e}", status=500)

    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    data = file_stream.getvalue()

    response = HttpResponse(
        data,
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
    response['Content-Disposition'] = f'attachment; filename="{learner.worker.surname}_удостоверение.docx"'
    response['Content-Length'] = str(len(data))

    return response


def return_knowledge_dates(learner):
    dates = learner.knowledge_date.filter(is_active=True)
    return dates


def generate_protocol(request, pk, template_name):
    try:
        protocol = Protocol.objects.get(pk=pk)
    except Protocol.DoesNotExist:
        return HttpResponseNotFound("Протокол не найден")
    results = protocol.protocol_result.all()
    learners_data = []
    for learner in protocol.learner.all():
        active_dates = learner.knowledge_date.filter(is_active=True)
        learners_data.append({
            'learner': learner,
            'active_dates': active_dates
        })
    context = {
        'protocol': protocol,
        'results': results,
        'learners_data': learners_data,
    }

    if template_name == 'protocol':
        template_path = Path(settings.BASE_DIR) / "patterns" / "protocol_template.docx"
    elif template_name == 'identities':
        template_path = Path(settings.BASE_DIR) / "patterns" / "identities.docx"

    if not template_path.exists():
        return HttpResponse("Шаблон не найден", status=500)

    try:
        doc = DocxTemplate(str(template_path))

        doc.render(context)
    except Exception as e:
        return HttpResponse(f"Ошибка при генерации документа: {e}", status=500)

    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    data = file_stream.getvalue()

    response = HttpResponse(
        data,
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
    response['Content-Disposition'] = 'attachment; filename="protocol.docx"'
    response['Content-Length'] = str(len(data))

    return response




