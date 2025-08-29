from flask import render_template
from weasyprint import HTML
import io

def generate_pdf(invoice):
    html = render_template('invoice_pdf.html', invoice=invoice)
    pdf_io = io.BytesIO()
    HTML(string=html).write_pdf(pdf_io)
    pdf_io.seek(0)
    return pdf_io
