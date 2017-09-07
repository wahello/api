from django.contrib import admin
from .models import Lesson, Course, CourseLead
# from django.utils.translation import ugettext_lazy as _
from core.models import User
# from adminfilters.models import Species, Breed


class UserAdminInline(admin.TabularInline):
    model = User


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    ordering = ['-start']
    list_filter = ('student', )
    list_display = ('start', 'student')
    save_as = True
    # raw_id_fields = ("student",)
    # inlines = [UserAdminInline]


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    ordering = ['id']


@admin.register(CourseLead)
class CourseLeadAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'contact',
        'course',
        'status',
        'student',
    )
    list_filter = ('status', )
    ordering = ['status']
    # ordering = ['id']
