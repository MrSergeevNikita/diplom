
from .models import *
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile

class GroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'is_student', 'is_teacher', 'is_admin', 'display_groups')
    list_filter = ('is_student', 'is_teacher', 'is_admin')
    search_fields = ('email', 'username', 'patronymic')
    filter_horizontal = ('id_group',)

    def display_groups(self, obj):
        return ', '.join([group.name for group in obj.id_group.all()])


class DisciplineAdmin(admin.ModelAdmin):
    list_display = ('name_discipline', 'id_teacher')
    list_filter = ('id_teacher',)
    search_fields = ('name_discipline', 'id_teacher__username') 

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('id_teacher')  
        return queryset


class VideoMaterialsAdmin(admin.ModelAdmin):
    list_display = ('title', 'id_teacher', 'id_discipline', 'upload_date')
    list_filter = ('id_teacher', 'id_discipline__name_discipline', 'upload_date')
    search_fields = ('title', 'id_teacher__username', 'id_discipline__name_discipline')
    readonly_fields = ('upload_date',) 
    date_hierarchy = 'upload_date'  
    

admin.site.register(VideoMaterials, VideoMaterialsAdmin)


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Discipline, DisciplineAdmin)


admin.site.register(View)
admin.site.register(Comment)
admin.site.register(StudentDiscipline)
admin.site.register(VideoLike)
admin.site.register(GroupDiscipline)