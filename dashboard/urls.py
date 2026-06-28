from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.index_view, name='index'),
    path('admin-panel/', views.admin_view, name='admin_panel'),
    path('mi-empresa/', views.empresa_view, name='mi_empresa'),
    path('empresas/', views.empresas_lista_view, name='empresas_lista'),

    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),

    path('api/empresa/', views.api_empresa, name='api_empresa'),

    path('api/admin/resumen/', views.api_admin_resumen, name='api_admin_resumen'),
]