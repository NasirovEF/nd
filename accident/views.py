from django.core.mail import send_mail
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView, View)
from accident.forms import AccidentForm
from accident.models import Accident, AccidentСategory, Organization
from config.settings import EMAIL_HOST_USER
from datetime import date


class AccidentListView(ListView):
    model = Accident
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        organizations = Organization.objects.all()
        context["organizations"] = organizations
        categories = AccidentСategory.objects.all()
        context["categories"] = categories
        date_now = str(date.today())
        context["date_now"] = date_now
        context['search_params'] = {
            'order': self.request.GET.get('order', ''),
            'date_from': self.request.GET.get('date_from', ''),
            'date_to': self.request.GET.get('date_to', ''),
            'ost': self.request.GET.get('OST', ''),
            'category': self.request.GET.get('category', ''),
            'description': self.request.GET.get('description', ''),
            'is_death': self.request.GET.get('is_death'),
        }
        return context

    def get_queryset(self, *args, **kwargs):
        queryset = super().get_queryset(*args, **kwargs)
        order = self.request.GET.get("order")
        date_from = self.request.GET.get("date_from")
        date_to = self.request.GET.get("date_to")
        ost = self.request.GET.get("OST")
        category = self.request.GET.get("category")
        description = self.request.GET.get("description")
        is_death = self.request.GET.get("is_death")

        if order:
            queryset = queryset.filter(order__icontains=order)
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        if ost:
            queryset = queryset.filter(organization__name__icontains=ost)
        if category:
            queryset = queryset.filter(category__name__icontains=category)
        if is_death == '1':
            queryset = queryset.filter(is_death=True)
        elif is_death == '0':
            queryset = queryset.filter(is_death=False)
        else:
            queryset
        if description:
            queryset = queryset.filter(description__icontains=description)

        return queryset


class AccidentDetailView(DetailView):
    model = Accident


class AccidentCreateView(CreateView):
    model = Accident
    form_class = AccidentForm

    def get_success_url(self):
        return reverse("accident:accident_detail", args=[self.object.pk])

    def form_valid(self, form):
        object = form.save()
        host = self.request.get_host()
        send_mail(
            subject=f"Информация о новом несчастном случае",
            message=f"Внимание в АСУ НС добавлена информация о новом несчастном случае. "
            f"Для ознакомления перейдите по ссылке: http://{host}/accident/accident_detail/{object.pk}",
            from_email=EMAIL_HOST_USER,
            recipient_list=["i@ef-nasirov.ru",],
        )
        return super().form_valid(form)


class AccidentUpdateView(UpdateView):
    model = Accident
    form_class = AccidentForm

    def get_success_url(self):
        return reverse("accident:accident_detail", args=[self.object.pk])


class AccidentDeleteView(DeleteView):
    model = Accident
    success_url = reverse_lazy("accident:search", args=[1])

