from flask import Blueprint, render_template, request, redirect, url_for, send_file, flash,make_response
from app import db, mail
from sqlalchemy.exc import IntegrityError
from app.models import Client, Invoice, Item
from flask_mail import Message
from app.utils import generate_pdf
from xhtml2pdf import pisa
import io
from app.extensions import db, mail

main = Blueprint('main', __name__)

@main.route('/')
def index():
    clients = Client.query.all()
    return render_template('index.html', clients=clients)

@main.route("/add-client", methods=["GET", "POST"])
def add_client():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        company = request.form.get("company")
        billing_address = request.form.get("billing_address")

        client = Client(
            name=name,
            email=email,
            phone=phone,
            company=company,
            billing_address=billing_address
        )

        try:
            db.session.add(client)
            db.session.commit()
            flash("Client added successfully!", "success")
            return redirect(url_for("main.add_client"))
        except IntegrityError as e:
            db.session.rollback()
            if "Duplicate entry" in str(e):
                flash("Email or phone already exists!", "danger")
            else:
                flash("An error occurred while adding the client.", "error")

    return render_template("add_client.html")

@main.route("/client/update/<int:client_id>", methods=["POST"])
def update_client(client_id):
    client = Client.query.get_or_404(client_id)

    client.name = request.form.get("name")
    client.email = request.form.get("email")
    client.phone = request.form.get("phone")
    client.company = request.form.get("company")
    client.billing_address = request.form.get("billing_address")

    try:
        db.session.commit()
        flash("Client updated successfully!", "success")
    except IntegrityError as e:
        db.session.rollback()
        if "Duplicate entry" in str(e.orig):
            flash("Email or phone already exists!", "danger")
        else:
            flash("An error occurred while updating the client.", "danger")

    return redirect(url_for("main.index"))

@main.route("/client/delete/<int:client_id>", methods=["POST"])
def delete_client(client_id):
    client = Client.query.get_or_404(client_id)

    try:
        Invoice.query.filter_by(client_id=client.id).delete()
        db.session.delete(client)
        db.session.commit()
        flash("Client deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting the client: {str(e)}", "danger")

    return redirect(url_for("main.index"))




@main.route('/invoice/create/<int:client_id>', methods=['GET', 'POST'])
def create_invoice(client_id):
    client = Client.query.get_or_404(client_id)
    if request.method == 'POST':
        invoice = Invoice(
            invoice_no=request.form['invoice_no'],
            client_id=client_id,
            issue_date=request.form['issue_date'],
            due_date=request.form['due_date'],
            subtotal=0,
            total=0
        )
        db.session.add(invoice)
        db.session.commit()

        subtotal = 0
        total = 0

        item_names = request.form.getlist('item_name')
        descriptions = request.form.getlist('description')
        quantities = request.form.getlist('quantity')
        rates = request.form.getlist('rate')
        item_taxes = request.form.getlist('item_tax')
        item_discounts = request.form.getlist('item_discount')

        for i in range(len(item_names)):
            qty = int(quantities[i])
            rate = float(rates[i])
            item_subtotal = qty * rate

            tax = float(item_taxes[i])  # % tax
            discount = float(item_discounts[i])  # flat discount

            # apply per item
            item_total = item_subtotal + (item_subtotal * tax / 100) - discount

            subtotal += item_subtotal
            total += item_total

            item = Item(
                invoice_id=invoice.id,
                name=item_names[i],
                description=descriptions[i],
                quantity=qty,
                rate=rate,
                tax=tax,
                discount=discount
            )
            db.session.add(item)

        invoice.subtotal = subtotal
        invoice.total = total
        db.session.commit()
        return redirect(url_for('main.preview_invoice', invoice_id=invoice.id))

    return render_template('create_invoice.html', client=client)


@main.route('/invoice/preview/<int:invoice_id>')
def preview_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    return render_template('preview_invoice.html', invoice=invoice)

@main.route('/invoice/download/<int:invoice_id>')
def download_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    pdf = generate_pdf(invoice)
    return send_file(pdf, as_attachment=True, download_name=f'invoice_{invoice.invoice_no}.pdf')

@main.route('/invoice/email/<int:invoice_id>')
def email_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    client_email = invoice.client.email
    pdf = generate_pdf(invoice)

    msg = Message(
        f"Invoice #{invoice.invoice_no}",
        recipients=[client_email],
        body="Please find your invoice attached.",
        sender='your_email@gmail.com'
    )
    msg.attach(f"invoice_{invoice.invoice_no}.pdf", 'application/pdf', pdf.getvalue())
    mail.send(msg)
    flash('Invoice emailed successfully!',"success")
    return redirect(url_for('main.preview_invoice', invoice_id=invoice_id))

@main.route('/invoice/<int:invoice_id>/pdf')
def view_invoice_pdf(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    html = render_template('invoice_pdf.html', invoice=invoice)

    result = io.BytesIO()
    pisa_status = pisa.CreatePDF(io.StringIO(html), dest=result)

    if pisa_status.err:
        return "Error while creating PDF", 500

    response = make_response(result.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=invoice.pdf'
    return response

@main.route("/client/<int:client_id>/invoices")
def client_invoices(client_id):
    client = Client.query.get_or_404(client_id)
    invoices = Invoice.query.filter_by(client_id=client.id).all()
    return render_template("client_invoices.html", client=client, invoices=invoices)
@main.route("/invoice/delete/<int:invoice_id>", methods=["POST"])
def delete_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    client_id = invoice.client_id
    try:
        Item.query.filter_by(invoice_id=invoice.id).delete()
        db.session.delete(invoice)
        db.session.commit()
        flash("Invoice deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error deleting invoice: {str(e)}", "danger")

    return redirect(url_for("main.client_invoices", client_id=client_id))
