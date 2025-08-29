from app import db

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(20), unique=True)
    company = db.Column(db.String(100))
    billing_address = db.Column(db.String(200))
    invoices = db.relationship("Invoice", backref="client", cascade="all, delete", passive_deletes=True)

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_no = db.Column(db.String(20))
    client_id = db.Column(db.Integer, db.ForeignKey('client.id', ondelete='CASCADE'))
    issue_date = db.Column(db.String(20))
    due_date = db.Column(db.String(20))
    tax = db.Column(db.Float)
    discount = db.Column(db.Float)
    subtotal = db.Column(db.Float)
    total = db.Column(db.Float)
    items = db.relationship("Item", backref="invoice", cascade="all, delete", passive_deletes=True)


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'))
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    quantity = db.Column(db.Integer)
    rate = db.Column(db.Float)
    tax = db.Column(db.Float, default=0.0)        
    discount = db.Column(db.Float, default=0.0) 
