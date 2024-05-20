
from .models import *
from django.contrib import admin
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
    
class ViewAdmin(admin.ModelAdmin):
    list_display = ('get_video_title', 'id_user')
    list_filter = ('id_video__title', 'id_user')
    search_fields = ('id_video__title', 'id_user__username')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('id_video', 'id_user')  # Оптимизация запросов для выборки связанных данных
        return queryset
    
    def get_video_title(self, obj):
        return obj.id_video.title
    get_video_title.short_description = 'Video Title'

class CommentAdmin(admin.ModelAdmin):
    list_display = ('get_video_title', 'get_author_email', 'content', 'creation_date')
    list_filter = ('id_video__title', 'id_author__email', 'creation_date')
    search_fields = ('content', 'id_video__title', 'id_author__email')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('id_video', 'id_author')  # Оптимизация запросов для выборки связанных данных
        return queryset

    def get_video_title(self, obj):
        return obj.id_video.title
    get_video_title.short_description = 'Video Title'

    def get_author_email(self, obj):
        return obj.id_author.email if obj.id_author else 'Anonymous'
    get_author_email.short_description = 'Author'

class VideoLikeAdmin(admin.ModelAdmin):
    list_display = ('get_video_title', 'get_user_email', 'reaction')
    list_filter = ('reaction', 'id_video__title', 'id_user__email')
    search_fields = ('id_video__title', 'id_user__email', 'reaction')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('id_video', 'id_user')  # Оптимизация запросов для выборки связанных данных
        return queryset

    def get_video_title(self, obj):
        return obj.id_video.title
    get_video_title.short_description = 'Video Title'

    def get_user_email(self, obj):
        return obj.id_user.email
    get_user_email.short_description = 'User'

class GroupDisciplineAdmin(admin.ModelAdmin):
    list_display = ('get_group_name', 'get_discipline_name')
    list_filter = ('id_group__name', 'id_discipline__name_discipline')
    search_fields = ('id_group__name', 'id_discipline__name_discipline')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('id_group', 'id_discipline')  # Оптимизация запросов для выборки связанных данных
        return queryset

    def get_group_name(self, obj):
        return obj.id_group.name
    get_group_name.short_description = 'Group'

    def get_discipline_name(self, obj):
        return obj.id_discipline.name_discipline
    get_discipline_name.short_description = 'Discipline'




admin.site.register(GroupDiscipline, GroupDisciplineAdmin)
admin.site.register(VideoLike, VideoLikeAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Discipline, DisciplineAdmin)
admin.site.register(VideoMaterials, VideoMaterialsAdmin)
admin.site.register(View, ViewAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Request)
