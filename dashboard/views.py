from django.shortcuts import render
from django.http import JsonResponse
from .models import Empresa, Merma, EtapaProductiva
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
    total_mermas = mermas.count()

    # Detalle por etapa
    etapas_detalle = []
    for etapa in EtapaProductiva.objects.all().order_by('orden'):
        m_etapa = mermas.filter(etapa=etapa)
        pct = m_etapa.aggregate(avg=Avg('porcentaje'))['avg']
        etapas_detalle.append({
            'nombre':       etapa.nombre,
            'tiene_datos':  m_etapa.exists(),
            'merma_pct':    f"{pct:.1f}%" if pct is not None else None,
            'registros':    m_etapa.count(),
        })

    # Detalle por tipo de merma
    tipos_detalle = []
    for tipo_code, tipo_label in Merma.TIPO_CHOICES:
        m_tipo = mermas.filter(tipo=tipo_code)
        count = m_tipo.count()
        tipos_detalle.append({
            'tipo':       tipo_label,
            'cantidad':   count,
            'porcentaje': round((count / total_mermas * 100), 1) if total_mermas else 0,
        })

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
        'total_mermas':    total_mermas,
        'etapas_detalle':  etapas_detalle,
        'tipos_detalle':   tipos_detalle,
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
            'id':          e.id,
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


@api_login_required
def api_etapas(request):
    etapas = EtapaProductiva.objects.all().order_by('orden')
    data = [{'id': e.id, 'nombre': e.nombre} for e in etapas]
    return JsonResponse({'etapas': data})


@api_login_required
def registrar_merma(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        empresa = request.user.perfil_empresa
    except Empresa.DoesNotExist:
        return JsonResponse({'error': 'Este usuario no tiene empresa asociada.'}, status=403)

    import json
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)

    etapa_id      = data.get('etapa_id')
    problema      = (data.get('problema') or '').strip()
    tipo          = data.get('tipo')
    porcentaje    = data.get('porcentaje')
    impacto       = data.get('impacto')
    prioridad     = data.get('prioridad', 'media')

    if not all([etapa_id, problema, tipo, porcentaje]):
        return JsonResponse({'error': 'Faltan campos obligatorios.'}, status=400)

    try:
        etapa = EtapaProductiva.objects.get(id=etapa_id)
    except EtapaProductiva.DoesNotExist:
        return JsonResponse({'error': 'Etapa inválida.'}, status=400)

    if tipo not in dict(Merma.TIPO_CHOICES):
        return JsonResponse({'error': 'Tipo de merma inválido.'}, status=400)

    if prioridad not in dict(Merma.PRIORIDAD_CHOICES):
        prioridad = 'media'

    try:
        porcentaje = float(porcentaje)
        if porcentaje < 0 or porcentaje > 100:
            return JsonResponse({'error': 'El porcentaje debe estar entre 0 y 100.'}, status=400)
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Porcentaje inválido.'}, status=400)

    impacto_val = None
    if impacto not in (None, ''):
        try:
            impacto_val = float(impacto)
        except (TypeError, ValueError):
            return JsonResponse({'error': 'Impacto económico inválido.'}, status=400)

    Merma.objects.create(
        empresa=empresa,
        etapa=etapa,
        problema_detectado=problema,
        tipo=tipo,
        porcentaje=porcentaje,
        impacto_economico=impacto_val,
        prioridad=prioridad,
    )

    return JsonResponse({'ok': True})

@api_login_required
def listar_mermas(request):
    try:
        empresa = request.user.perfil_empresa
    except Empresa.DoesNotExist:
        return JsonResponse({'error': 'Este usuario no tiene empresa asociada.'}, status=403)

    mermas = Merma.objects.filter(empresa=empresa).select_related('etapa').order_by('-fecha_registro')

    data = [{
        'id':                m.id,
        'etapa':             m.etapa.nombre,
        'etapa_id':          m.etapa.id,
        'problema':          m.problema_detectado,
        'tipo':              m.get_tipo_display(),
        'tipo_code':         m.tipo,
        'porcentaje':        f"{m.porcentaje}%",
        'porcentaje_raw':    str(m.porcentaje),
        'prioridad':         m.get_prioridad_display(),
        'prioridad_code':    m.prioridad,
        'impacto_raw':       str(m.impacto_economico) if m.impacto_economico is not None else '',
        'fecha':             m.fecha_registro.strftime('%d-%m-%Y %H:%M'),
    } for m in mermas]

    return JsonResponse({'mermas': data})

@api_login_required
def eliminar_merma(request, merma_id):
    if request.method != 'DELETE':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        empresa = request.user.perfil_empresa
    except Empresa.DoesNotExist:
        return JsonResponse({'error': 'Este usuario no tiene empresa asociada.'}, status=403)

    try:
        merma = Merma.objects.get(id=merma_id, empresa=empresa)
    except Merma.DoesNotExist:
        return JsonResponse({'error': 'Merma no encontrada.'}, status=404)

    merma.delete()
    return JsonResponse({'ok': True})


@api_login_required
def api_admin_detalle_empresa(request, empresa_id):
    if not request.user.is_staff:
        return JsonResponse({'error': 'No autorizado'}, status=403)

    try:
        empresa = Empresa.objects.get(id=empresa_id)
    except Empresa.DoesNotExist:
        return JsonResponse({'error': 'Empresa no encontrada'}, status=404)

    mermas = Merma.objects.filter(empresa=empresa).select_related('etapa').order_by('-fecha_registro')

    mermas_data = [{
        'id':         m.id,
        'etapa':      m.etapa.nombre,
        'problema':   m.problema_detectado,
        'tipo':       m.get_tipo_display(),
        'porcentaje': f"{m.porcentaje}%",
        'prioridad':  m.get_prioridad_display(),
        'fecha':      m.fecha_registro.strftime('%d-%m-%Y %H:%M'),
    } for m in mermas]

    merma_pct = mermas.aggregate(avg=Avg('porcentaje'))['avg'] or 0
    perdida   = mermas.aggregate(total=Sum('impacto_economico'))['total'] or 0

    return JsonResponse({
        'nombre':      empresa.nombre,
        'rubro':       empresa.rubro or '—',
        'tamano':      empresa.tamano or '—',
        'region':      empresa.region or '—',
        'contacto':    empresa.contacto_principal or '—',
        'merma_pct':   f"{merma_pct:.1f}%",
        'perdida_usd': f"${perdida:,.0f}".replace(',', '.'),
        'total_mermas': mermas.count(),
        'mermas':      mermas_data,
    })

@api_login_required
def api_admin_editar_empresa(request, empresa_id):
    if not request.user.is_staff:
        return JsonResponse({'error': 'No autorizado'}, status=403)

    if request.method != 'PUT':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        empresa = Empresa.objects.get(id=empresa_id)
    except Empresa.DoesNotExist:
        return JsonResponse({'error': 'Empresa no encontrada'}, status=404)

    import json
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)

    nombre = (data.get('nombre') or '').strip()
    if not nombre:
        return JsonResponse({'error': 'El nombre es obligatorio.'}, status=400)

    empresa.nombre = nombre
    empresa.rubro = (data.get('rubro') or '').strip() or None
    empresa.tamano = (data.get('tamano') or '').strip() or None
    empresa.region = (data.get('region') or '').strip() or None
    empresa.contacto_principal = (data.get('contacto') or '').strip() or None
    empresa.save()

    return JsonResponse({'ok': True})

@api_login_required
def editar_empresa(request):
    if request.method != 'PUT':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        empresa = request.user.perfil_empresa
    except Empresa.DoesNotExist:
        return JsonResponse({'error': 'Este usuario no tiene empresa asociada.'}, status=403)

    import json
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)

    rubro    = (data.get('rubro') or '').strip()
    tamano   = (data.get('tamano') or '').strip()
    region   = (data.get('region') or '').strip()
    contacto = (data.get('contacto') or '').strip()

    empresa.rubro = rubro or None
    empresa.tamano = tamano or None
    empresa.region = region or None
    empresa.contacto_principal = contacto or None
    empresa.save()

    return JsonResponse({'ok': True})


@api_login_required
def editar_merma(request, merma_id):
    if request.method != 'PUT':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        empresa = request.user.perfil_empresa
    except Empresa.DoesNotExist:
        return JsonResponse({'error': 'Este usuario no tiene empresa asociada.'}, status=403)

    try:
        merma = Merma.objects.get(id=merma_id, empresa=empresa)
    except Merma.DoesNotExist:
        return JsonResponse({'error': 'Merma no encontrada.'}, status=404)

    import json
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)

    etapa_id   = data.get('etapa_id')
    problema   = (data.get('problema') or '').strip()
    tipo       = data.get('tipo')
    porcentaje = data.get('porcentaje')
    impacto    = data.get('impacto')
    prioridad  = data.get('prioridad', 'media')

    if not all([etapa_id, problema, tipo, porcentaje]):
        return JsonResponse({'error': 'Faltan campos obligatorios.'}, status=400)

    try:
        etapa = EtapaProductiva.objects.get(id=etapa_id)
    except EtapaProductiva.DoesNotExist:
        return JsonResponse({'error': 'Etapa inválida.'}, status=400)

    if tipo not in dict(Merma.TIPO_CHOICES):
        return JsonResponse({'error': 'Tipo de merma inválido.'}, status=400)

    if prioridad not in dict(Merma.PRIORIDAD_CHOICES):
        prioridad = 'media'

    try:
        porcentaje = float(porcentaje)
        if porcentaje < 0 or porcentaje > 100:
            return JsonResponse({'error': 'El porcentaje debe estar entre 0 y 100.'}, status=400)
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Porcentaje inválido.'}, status=400)

    impacto_val = None
    if impacto not in (None, ''):
        try:
            impacto_val = float(impacto)
        except (TypeError, ValueError):
            return JsonResponse({'error': 'Impacto económico inválido.'}, status=400)

    merma.etapa = etapa
    merma.problema_detectado = problema
    merma.tipo = tipo
    merma.porcentaje = porcentaje
    merma.impacto_economico = impacto_val
    merma.prioridad = prioridad
    merma.save()

    return JsonResponse({'ok': True})