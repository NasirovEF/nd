from django.contrib import admin, messages
from users.forms import AdminPasswordChangeForm
from users.models import User


@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
        # Поля, доступные для редактирования
        fieldsets = (
            (None, {
                'fields': ('service_number', 'email', 'worker', 'is_active', 'is_staff')
            }),
            ('Права', {
                'fields': ('is_superuser', 'groups', 'user_permissions'),
                'classes': ('collapse',)  # Свёрнуто по умолчанию
            }),
        )

        # Только для списка (не для редактирования)
        list_display = ('service_number', 'email', 'worker', 'is_staff', 'is_active')
        search_fields = ('service_number', 'email', 'worker__surname')
        list_filter = ('is_staff', 'is_superuser', 'is_active')

        def change_view(self, request, object_id, form_url='', extra_context=None):
            # Добавляем форму смены пароля на страницу редактирования
            extra_context = extra_context or {}
            if object_id:
                extra_context['password_form'] = AdminPasswordChangeForm()
            return super().change_view(request, object_id, form_url, extra_context)

        def response_change(self, request, obj):
            # Обрабатываем отправку формы смены пароля
            if "_change_password" in request.POST:
                form = AdminPasswordChangeForm(request.POST)
                if form.is_valid():
                    form.instance = obj
                    form.save()
                    self.message_user(request, "Пароль успешно изменён.")
                else:
                    for error in form.errors.values():
                        self.message_user(request, str(error), level=messages.ERROR)
            return super().response_change(request, obj)
