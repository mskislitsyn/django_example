from django.contrib import admin

from .models import UserProfile, Event, EventFile, Category, Tag

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'phone_number')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'name')


class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


class EventFileAdminInline(admin.StackedInline):
    extra = 0
    model = EventFile
    verbose_name_plural = "Attached event's files"


class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'description', 'host')
    inlines = [EventFileAdminInline]
    raw_id_fields = ('tags',)
    list_display_links = ('id', 'name')
    fieldsets=(
            (None, {'fields': ('name', 'category', 'description', 'host', 'created', 'tags')}),
            ('Location', {'fields': ('latitude', 'longitude', 'address')}),
            ('Period', {'fields': ('date_start', 'date_end')})
        )
 
 
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Event, EventAdmin)