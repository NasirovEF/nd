import docx
from docxtpl import DocxTemplate

NULLABLE = {"null": True, "blank": True}

doc = DocxTemplate("../title.docx")


context = {"title": ""}

doc.render(context)
doc.save("123.docx")
