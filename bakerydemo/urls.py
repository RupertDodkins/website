from django.conf.urls import include, url, re_path
from django.conf import settings
from django.contrib import admin

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.core import urls as wagtail_urls

from bakerydemo.search import views as search_views
from .api import api_router

from wagtail.documents.views import serve
def view_document(request, document_id, document_filename):
    """
    Calls the normal document `serve` view, except makes it not an attachment.
    """
    # Get response from `serve` first
    response = serve.serve(request, document_id, document_filename)

    # Remove "attachment" from response's Content-Disposition
    contdisp = response['Content-Disposition']
    response['Content-Disposition'] = "; ".join(
        [x for x in contdisp.split("; ") if x != "attachment"]
    )

    # Force content-type for pdf files
    if document_filename.split('.')[-1] == 'pdf':
        response['Content-Type'] = 'application/pdf'

    # Return the response
    return response

urlpatterns = [
    url(r'^django-admin/', admin.site.urls),

    url(r'^admin/', include(wagtailadmin_urls)),
    url(r'^documents/', include(wagtaildocs_urls)),

    re_path(r'^document/view/(\d+)/(.*)$', view_document, name='view_document'),  # noqa

    url(r'^search/$', search_views.search, name='search'),

    url(r'^sitemap\.xml$', sitemap),
    url(r'^api/v2/', api_router.urls),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    from django.views.generic import TemplateView
    from django.views.generic.base import RedirectView

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        url(
            r'^favicon\.ico$', RedirectView.as_view(
                url=settings.STATIC_URL + 'img/bread-favicon.ico'
            )
        )
    ]

    # Add views for testing 404 and 500 templates
    urlpatterns += [
        url(r'^test404/$', TemplateView.as_view(template_name='404.html')),
        url(r'^test500/$', TemplateView.as_view(template_name='500.html')),
    ]

urlpatterns += [
    url(r'', include(wagtail_urls)),
]
