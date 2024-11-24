from django.contrib import admin

from . import models


@admin.register(models.Post)
class PostAdmin(admin.ModelAdmin):
    search_fields = ('title', 'text', 'pub_date',)


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('title', 'description',)


@admin.register(models.Location)
class LocationAdmin(admin.ModelAdmin):
    search_fields = ('name',)


@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
    search_fields = ('title', 'description',)


admin.site.empty_value_display = 'Не задано'
