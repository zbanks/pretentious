from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'pretentious.views.home', name='home'),
    # url(r'^pretentious/', include('pretentious.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^signup$', 'pretentious.pos.views.signup', name='signup'),
    url(r'^buy$', 'pretentious.pos.views.buy', name='buy'),
    url(r'^credit$', 'pretentious.pos.views.credit', name='credit'),
    url(r'^finger/([a-zA-Z0-9-]+)$', 'pretentious.pos.views.finger', name='finger'),
    url(r'^$', 'pretentious.pos.views.index', name='index'),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
