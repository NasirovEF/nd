from datetime import date, timedelta

from organization.models import Organization


def insert_line_breaks(text, max_chars=60):
    if len(text) <= max_chars:
        return text
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        if len(current_line + " " + word) <= max_chars:
            current_line += (" " + word) if current_line else word
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return "<br>".join(lines)


def calculating_probability(event):
    """Расчет вероятности возникновения события"""
    three_years_ago = date.today() - timedelta(days=3 * 365)
    ten_years_ago = date.today() - timedelta(days=10 * 365)
    main_ost = Organization.objects.filter(is_main=True).first()
    #for accident in event.accident_set.all():
    count = 0
    # уровни риска
    hight = event.accident_set.filter(
        organization__is_main=True,
        date__gte=three_years_ago
    ).count()

    medium = event.accident_set.filter(
        organization__is_transit=main_ost.is_transit,
        date__gte=three_years_ago
    ).count()

    low = event.accident_set.filter(
        date__gte=ten_years_ago
    ).count()

    if hight > 1:
        count += 5
    elif medium > 3:
        count += 4
    elif 1 <= medium <= 3:
        count += 3
    elif low > 1:
        count += 2
    elif hight == 0 and medium == 0 and low == 0:
        count += 1
    else:
        count += 2

    return count
