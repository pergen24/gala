import os
from flask import Blueprint, current_app, render_template, request, redirect, url_for, send_file, flash
from werkzeug.utils import secure_filename
from . import db
from .models import TicketPurchase
from .utils import generate_ticket_pdf, send_ticket_email
from .auth import admin_required
#from werkzeug.security import generate_password_hash, check_password_hash




bp = Blueprint('main', __name__)

ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

# RUTAS CLIENTE
@bp.route('/')
def index():
    return render_template('cliente/index.html')

@bp.route('/elegir')
def elegir_ticket():
    ticket_types = [
        {"name": "GENERAL", "image": "images/tickets/estandar.jpg"},
        {"name": "VIP", "image": "images/tickets/vip.jpg"},
        {"name": "INVITADO ESPECIAL", "image": "/images/tickets/especial.jpg"}
    ]
    return render_template('cliente/elegir_ticket.html', ticket_types=ticket_types)


@bp.route('/ticket_image/<ticket_type>')
def ticket_image(ticket_type):
    images = {
        "GENERAL": "images/tickets/estandar.jpg",
        "VIP": "images/tickets/vip.jpg",
        "INVITADO ESPECIAL": "images/tickets/especial.jpg"
    }
    img_path = images.get(ticket_type.upper())
    if not img_path:
        return "Tipo de ticket no encontrado", 404
    return render_template('cliente/ticket_image.html', ticket_type=ticket_type, img_path=img_path)



#@bp.route('/ticket_image/<ticket_type>')
#def ticket_image(ticket_type):
    # Diccionario de imágenes por tipo de ticket
#    images = {
#        "GENERAL": "images/tickets/estandar.jpg",
#        "VIP": "images/tickets/vip.jpg",
#        "INVITADO ESPECIAL": "images/tickets/especial.jpg"
#    }

#    img_path = images.get(ticket_type.upper())
#    if not img_path:
#        return "Tipo de ticket no encontrado", 404

#    return render_template('cliente/ticket_image.html', ticket_type=ticket_type, img_path=img_path)




@bp.route('/checkout/<ticket_type>', methods=['GET', 'POST'])
def checkout(ticket_type):
    if request.method == 'POST':
        # recoger datos
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        address = request.form.get('address')
        city = request.form.get('city')
        phone = request.form.get('phone')

        purchase = TicketPurchase(
            ticket_type=ticket_type,
            first_name=first_name,
            last_name=last_name,
            email=email,
            address=address,
            city=city,
            phone=phone,
            status='pending'
        )
        db.session.add(purchase)
        db.session.commit()

        # redirigir a página para que suba su recibo (transferencia externa)
        return redirect(url_for('.subir_recibo', purchase_id=purchase.id))

    return render_template('cliente/checkout.html', ticket_type=ticket_type)

@bp.route('/subir_recibo/<int:purchase_id>', methods=['GET', 'POST'])
def subir_recibo(purchase_id):
    purchase = TicketPurchase.query.get_or_404(purchase_id)
    if request.method == 'POST':
        if 'receipt' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['receipt']
        if file and allowed_file(file.filename):
            filename = secure_filename(f"{purchase.id}_{file.filename}")
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)
            purchase.receipt_filename = filename
            purchase.status = 'uploaded'
            db.session.commit()
            return redirect(url_for('.gracias'))
        else:
            flash('Archivo no permitido')
            return redirect(request.url)
    return render_template('cliente/subir_recibo.html', purchase=purchase)

@bp.route('/gracias')
def gracias():
    return render_template('cliente/gracias.html')

# RUTAS ADMIN (simple, sin auth para demo)
@bp.route('/admin')
@admin_required
def admin_index():
    purchases = TicketPurchase.query.order_by(TicketPurchase.created_at.desc()).all()
    return render_template('admin/index.html', purchases=purchases)

@bp.route('/admin/recibos')
@admin_required
def admin_recibos():
    purchases = TicketPurchase.query.filter(TicketPurchase.status.in_(['uploaded','pending'])).all()
    return render_template('admin/recibos.html', purchases=purchases)

#@bp.route('/admin/approve/<int:purchase_id>', methods=['POST'])
#def admin_approve(purchase_id):
#    purchase = TicketPurchase.query.get_or_404(purchase_id)
    # marcar aprobado
#    purchase.status = 'approved'
#    db.session.commit()

    # generar PDF con QR y devolverlo al admin (descarga)
#    pdf_bytes = generate_pdf_with_qr(purchase.to_dict())
#    filename = f"ticket_{purchase.id}.pdf"
#    return send_file(
#        io.BytesIO(pdf_bytes),
##        download_name=filename,
#        as_attachment=True,
#        mimetype='application/pdf'
#    )

@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    # servir recibos (solo demo)
    return send_file(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))




@bp.route('/admin/approve/<int:purchase_id>', methods=['POST'])
def admin_approve(purchase_id):
    purchase = TicketPurchase.query.get_or_404(purchase_id)

    # Marcar como aprobado
    purchase.status = 'approved'
    db.session.commit()

    try:
        # Generar PDF con QR
        pdf_bytes = generate_ticket_pdf(purchase)

        # Guardar PDF en el servidor
        tickets_folder = current_app.config.get('GENERATED_TICKETS_FOLDER', '/app/generated_tickets')
        os.makedirs(tickets_folder, exist_ok=True)
        pdf_filename = f"ticket_{purchase.id}.pdf"
        pdf_path = os.path.join(tickets_folder, pdf_filename)
        with open(pdf_path, 'wb') as f:
            f.write(pdf_bytes)

        # Guardar nombre del archivo en la compra (opcional)
        purchase.pdf_filename = pdf_filename
        db.session.commit()

        # Enviar email al usuario con el PDF adjunto
        send_ticket_email(purchase, pdf_bytes)

        flash(f"Ticket #{purchase.id} aprobado, enviado por email y guardado en el servidor.", "success")

    except Exception as e:
        flash(f"Error al generar/enviar/guardar el ticket: {str(e)}", "danger")

    return redirect(url_for("main.admin_index"))

