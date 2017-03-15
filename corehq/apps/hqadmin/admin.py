from django.contrib import admin
from .models import *


class ESRestorePillowCheckpointsAdmin(admin.ModelAdmin):

    model = ESRestorePillowCheckpoints
    list_display = [
        'checkpoint_id',
        'date_updated',
        'seq',
        'seq_int',
    ]


admin.site.register(ESRestorePillowCheckpoints, ESRestorePillowCheckpointsAdmin)
