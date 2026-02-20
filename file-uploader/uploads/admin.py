from django.contrib import admin
from hh.models import Sim

@admin.register(Sim)
class SimAdmin(admin.ModelAdmin):
    list_display = ('name','description','respo')
    search_fields = ('name',) 
 