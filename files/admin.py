from django.contrib import admin

# Register your models here.

from .models import Directory, File, Project

class FileAdmin(admin.ModelAdmin):
    list_display = ['name', 'url']

    def add_view(self, *args, **kwargs):
        self.exclude = ('saved_file',)
        return super(FileAdmin, self).add_view(*args, **kwargs)

    def change_view(self, *args, **kwargs):
        self.exclude = ('saved_file',)
        return super(FileAdmin, self).change_view(*args, **kwargs)

    def url(self, obj):
        return '<a href="%s">%s</a>' % (obj.GetAccessPath(), obj.name)

    url.allow_tags = True

class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'user']

admin.site.register(Directory)
admin.site.register(File, FileAdmin)
admin.site.register(Project, ProjectAdmin)