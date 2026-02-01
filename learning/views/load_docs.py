from django.http import HttpResponse
from docxtpl import DocxTemplate
import io

def generate_word_document(request, learner):
    context = {
        'name': 'Иван Иванов',
        'amount': 1000,
        'date': '01.02.2026'
    }

    # Загрузка шаблона
    doc = DocxTemplate("templates/docs/template.docx")

    # Рендеринг документа
    doc.render(context)

    # Сохранение в байтовый поток
    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)  # Перемотка в начало потока

    # Подготовка ответа для скачивания
    response = HttpResponse(
        file_stream.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
    response['Content-Disposition'] = 'attachment; filename="document.docx"'
    response['Content-Length'] = file_stream.tell()

    return response
