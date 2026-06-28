from django.shortcuts import render
from django.http import JsonResponse
from .models import Empresa, Merma
from django.db.models import Avg, Sum, Count
from django.contrib.auth.decorators import login_required
from functools import wraps

from django.contrib.auth import authenticate, login
from django.http import JsonResponse

def api_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'No autenticado'}, status=401)
        return view_func(request, *args, **kwargs)
    return wrapper


from django.shortcuts import redirect

def index_view(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    if request.user.is_staff:
        return redirect('/admin-panel/')
    return redirect('/mi-empresa/')

def admin_view(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    if not request.user.is_staff:
        return redirect('/mi-empresa/')
    return render(request, 'admin.html')

def empresa_view(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    try:
        _ = request.user.perfil_empresa
    except Exception:
        return redirect('/login/')
    return render(request, 'empresa.html')

def empresas_lista_view(request):
    if not request.user.is_authenticated:
        return redirect('/login/')
    if not request.user.is_staff:
        return redirect('/mi-empresa/')
    return render(request, 'empresas.html')

def login_view(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        usuario = data.get('username')
        password = data.get('password')
        user = authenticate(request, username=usuario, password=password)
        if user is not None:
            login(request, user)
            if user.is_staff:
                redirect_url = '/admin-panel/'
            else:
                try:
                    _ = user.perfil_empresa
                    redirect_url = '/mi-empresa/'
                except Exception:
                    redirect_url = '/'
            return JsonResponse({'ok': True, 'redirect': redirect_url})
        return JsonResponse({'ok': False, 'error': 'Usuario o contraseña incorrectos.'}, status=401)
    return render(request, 'login.html')

@api_login_required
def api_empresa(request):
    print(f"[MT] api_empresa → usuario: {request.user}")
    try:
        empresa = request.user.perfil_empresa
    except Empresa.DoesNotExist:
        return JsonResponse({'error': 'Este usuario no tiene empresa asociada.'}, status=403)

    mermas = Merma.objects.filter(empresa=empresa)
    merma_pct   = mermas.aggregate(avg=Avg('porcentaje'))['avg'] or 0
    perdida     = mermas.aggregate(total=Sum('impacto_economico'))['total'] or 0
    etapas_crit = mermas.values('etapa').distinct().count()

    return JsonResponse({
        'username':        request.user.username,
        'nombre':          empresa.nombre,
        'rubro':           empresa.rubro or '',
        'tamano':          empresa.tamano or '',
        'region':          empresa.region or '',
        'contacto':        empresa.contacto_principal or '',
        'merma_pct':       f"{merma_pct:.1f}%",
        'perdida_usd':     f"${perdida:,.0f}".replace(',', '.'),
        'etapas_criticas': str(etapas_crit),
        'mejora_pct':      '0%',
    })


@api_login_required
def api_admin_resumen(request):
    if not request.user.is_staff:
        return JsonResponse({'error': 'No autorizado'}, status=403)

    from django.contrib.auth.models import User

    empresas     = Empresa.objects.filter(estado=True)
    total_users  = User.objects.count()
    merma_pct    = Merma.objects.aggregate(avg=Avg('porcentaje'))['avg'] or 0
    perdida      = Merma.objects.aggregate(total=Sum('impacto_economico'))['total'] or 0

    empresas_data = []
    for e in empresas:
        mermas_e   = Merma.objects.filter(empresa=e)
        pct        = mermas_e.aggregate(avg=Avg('porcentaje'))['avg'] or 0
        tiene_data = mermas_e.exists()
        empresas_data.append({
            'nombre':      e.nombre,
            'usuario':     e.usuario.username if e.usuario else '—',
            'rubro':       e.rubro or '—',
            'merma_pct':   f"{pct:.1f}%",
            'tiene_datos': tiene_data,
        })

    usuarios_data = []
    for u in User.objects.all():
        try:
            empresa_nombre = u.perfil_empresa.nombre
        except Exception:
            empresa_nombre = '—'
        usuarios_data.append({
            'username':      u.username,
            'nombre':        u.get_full_name() or (u.perfil_empresa.nombre if hasattr(u, 'perfil_empresa') else 'Administrador'),
            'es_admin':      u.is_staff,
            'empresa':       empresa_nombre,
            'activo':        u.is_active,
        })

    return JsonResponse({
        'kpis': {
            'total_empresas': empresas.count(),
            'total_usuarios': total_users,
            'merma_pct':      f"{merma_pct:.1f}%",
            'perdida_usd':    f"${perdida:,.0f}".replace(',', '.'),
        },
        'empresas':  empresas_data,
        'usuarios':  usuarios_data,
    })