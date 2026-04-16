from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('terceros/', include('terceros.urls', namespace='terceros')),
]
