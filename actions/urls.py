from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .currency_actions import currency_actions

urlpatterns = [
    path("currency_actions", currency_actions, name="currency_actions"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)