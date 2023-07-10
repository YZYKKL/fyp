from django.urls import path, re_path, include
from rolemanagement import views

urlpatterns = [
    # path('admin/', admin.site.urls),
    re_path('^role/$', views.role, name="role"),
    re_path('^role_api/$', views.role_api, name="role_api"),
    re_path('^role_bind/$', views.role_bind, name="role_bind"),
    re_path('^role_bind_api/$', views.role_bind_api, name="role_bind_api"),
]
