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
    path('api/empresa/editar/', views.editar_empresa, name='editar_empresa'),

    path('api/admin/resumen/', views.api_admin_resumen, name='api_admin_resumen'),
    path('api/admin/empresa/<int:empresa_id>/', views.api_admin_detalle_empresa, name='api_admin_detalle_empresa'),
    path('api/admin/empresa/<int:empresa_id>/editar/', views.api_admin_editar_empresa, name='api_admin_editar_empresa'),
    path('api/etapas/', views.api_etapas, name='api_etapas'),

    path('api/merma/registrar/', views.registrar_merma, name='registrar_merma'),
    path('api/mermas/listar/', views.listar_mermas, name='listar_mermas'),
    path('api/merma/<int:merma_id>/eliminar/', views.eliminar_merma, name='eliminar_merma'),
    path('api/merma/<int:merma_id>/editar/', views.editar_merma, name='editar_merma'),

    
]