from django.contrib import admin
from .models import Professor, Module, ModuleInstance, TeachingAssignment, Rating

admin.site.register(Professor)
admin.site.register(Module)
admin.site.register(ModuleInstance)
admin.site.register(TeachingAssignment)
admin.site.register(Rating)
