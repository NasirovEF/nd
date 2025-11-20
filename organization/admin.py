from django.contrib import admin

from .models import Organization, Branch, Division, District, Group, Worker, PositionGroup, Position, StaffUnit

admin.site.register(Organization)
admin.site.register(Position)
admin.site.register(Branch)
admin.site.register(Division)
admin.site.register(District)
admin.site.register(Group)
admin.site.register(Worker)
admin.site.register(PositionGroup)
admin.site.register(StaffUnit)