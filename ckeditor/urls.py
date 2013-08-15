from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from ckeditor import views

urlpatterns = patterns(
    '',
    url(r'^upload/', admin.site.admin_view(views.upload), name='ckeditor_upload'),
    url(r'^browse/', admin.site.admin_view(views.browse), name='ckeditor_browse'),
)
