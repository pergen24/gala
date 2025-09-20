from flask import url_for
import io
import qrcode
from flask_mail import Message
from . import mail
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

def generate_ticket_pdf(purchase):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    # Datos del ticket
    text = f"""
    Ticket ID: {purchase.id}
    Nombre: {purchase.first_name} {purchase.last_name}
    Email: {purchase.email}
    Tipo de Ticket: {purchase.ticket_type}
    Estado: {purchase.status}
    """

    c.setFont("Helvetica", 12)
    y = 800
    for line in text.strip().split("\n"):
        c.drawString(100, y, line.strip())
        y -= 20

    # Generar QR con URL al ticket
    # Aquí asumimos que tu app está en localhost; usa url_for con _external=True si estás en app context
    qr_url = f"http://192.168.1.11:5000{url_for('main.ticket_image', ticket_type=purchase.ticket_type)}"
    qr_img = qrcode.make(qr_url)

    # Guardar QR en BytesIO en formato PNG
    qr_buffer = io.BytesIO()
    qr_img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)

    # Usar ImageReader con el buffer
    qr_reader = ImageReader(qr_buffer)

    # Dibujar QR en PDF
    c.drawImage(qr_reader, 100, 600, 150, 150)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue()


def send_ticket_email(purchase, pdf_bytes):
    msg = Message(
        subject="Tu Ticket - Gala Event",
        recipients=[purchase.email],
        body=f"""Hola {purchase.first_name},

Tu ticket ({purchase.ticket_type}) ha sido aprobado.
Adjunto encontrarás el PDF con tu código QR.

¡Gracias!"""
    )
    msg.attach(
        f"ticket_{purchase.id}.pdf",
        "application/pdf",
        pdf_bytes
    )
    mail.send(msg)
