from django.contrib import admin
from django.urls import include, path, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls'))
]

schema_view = get_schema_view(
    openapi.Info(
        title="Notificaion service API",
        default_version='v1',
        description="Документация для Cервиса уведомлений",
        contact=openapi.Contact(url='https://telegram.me/katerinagryadova'),
        license=openapi.License(name="made by KaterinaSolovyeva")
    ),
    public=True,
    permission_classes=(permissions.AllowAny,)
)

urlpatterns += [
    re_path(
        r'^swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=0), name='schema-json'
    ),
    re_path(
        r'^docs/$', schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'
    )
]
