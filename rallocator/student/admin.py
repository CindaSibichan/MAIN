from django.contrib import admin

from.models import *

# Register your models here.

class MasterAdmin(admin.ModelAdmin) :

    list_display = ['created_user','created_date','isactive']
    def save_model(self, request, obj, form, change):
        # Set the created_user field to the currently logged-in user
        obj.created_user = request.user
        super().save_model(request, obj, form, change)


@admin.register(Student)

class studentAdmin(admin.ModelAdmin):
    list_display = ['Name','Batch']
    exclude = ['created_user']


class SystemAllocationAdmin(MasterAdmin) :
    
    list_display = ['students','From','To','system']
    exclude = ['created_user']

admin.site.register(SystemAllocation,SystemAllocationAdmin)