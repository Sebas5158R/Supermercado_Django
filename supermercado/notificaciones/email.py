from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


def _enviar(asunto, template, contexto, destinatarios):
    cuerpo = render_to_string(template, contexto)
    try:
        send_mail(
            subject=asunto,
            message='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=destinatarios if isinstance(destinatarios, list) else [destinatarios],
            html_message=cuerpo,
            fail_silently=False,
        )
        return True
    except Exception:
        return False


def enviar_confirmacion_venta(venta, detalles):
    return _enviar(
        asunto=f"Confirmación de compra #{venta.id} — Supermercado Lolitas",
        template='emails/confirmacion_venta.html',
        contexto={'venta': venta, 'detalles': detalles, 'cliente': venta.cliente},
        destinatarios=venta.cliente.email,
    )


def enviar_confirmacion_compra(compra, detalles):
    if not compra.proveedor or not compra.proveedor.email:
        return False
    return _enviar(
        asunto=f"Orden de compra #{compra.id} registrada — Supermercado Lolitas",
        template='emails/confirmacion_compra.html',
        contexto={'compra': compra, 'detalles': detalles, 'proveedor': compra.proveedor},
        destinatarios=compra.proveedor.email,
    )


def enviar_alerta_stock_critico(productos_criticos, destinatarios):
    if not productos_criticos or not destinatarios:
        return False
    return _enviar(
        asunto=f"Alerta: {len(productos_criticos)} producto(s) con stock crítico — Supermercado Lolitas",
        template='emails/alerta_stock.html',
        contexto={'productos': productos_criticos},
        destinatarios=destinatarios,
    )


def enviar_alerta_vencimiento(productos_proximos, destinatarios):
    if not productos_proximos or not destinatarios:
        return False
    return _enviar(
        asunto=f"Alerta: {len(productos_proximos)} producto(s) próximos a vencer — Supermercado Lolitas",
        template='emails/alerta_vencimiento.html',
        contexto={'productos': productos_proximos},
        destinatarios=destinatarios,
    )


def enviar_notificacion_anulacion_venta(venta):
    if not venta.cliente or not venta.cliente.email:
        return False
    return _enviar(
        asunto=f"Venta #{venta.id} anulada — Supermercado Lolitas",
        template='emails/anulacion_venta.html',
        contexto={'venta': venta, 'cliente': venta.cliente},
        destinatarios=venta.cliente.email,
    )


def enviar_resumen_diario(resumen, destinatarios):
    if not destinatarios:
        return False
    from datetime import date
    return _enviar(
        asunto=f"Resumen diario {date.today().strftime('%d/%m/%Y')} — Supermercado Lolitas",
        template='emails/resumen_diario.html',
        contexto={'resumen': resumen, 'fecha': date.today()},
        destinatarios=destinatarios,
    )
