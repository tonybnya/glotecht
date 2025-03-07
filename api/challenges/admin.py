from django.contrib import admin

from .models import Challenge


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "get_tags")
    list_filter = ("tags",)
    search_fields = ("title", "description")
    ordering = ("id",)

    def get_tags(self, obj):
        return ", ".join(obj.tags)

    get_tags.short_description = "Tags - Tech Stack of the challenge"
