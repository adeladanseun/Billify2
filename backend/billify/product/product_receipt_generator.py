from reportlab.lib.pagesizes import letter#, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer#, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from io import BytesIO
#from reportlab.pdfgen import canvas
from datetime import datetime, timedelta

class PDFInvoiceGenerator:
    def __init__(self, filename):
        self.filename = filename
        self.buffer = BytesIO()

        self.doc = SimpleDocTemplate(
            self.buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=50,#72,
            bottomMargin=72
        )
        self.styles = getSampleStyleSheet()
        self.elements = []
        self.invoice_data = {}
        
    def set_invoice_data(self, invoice_number, issue_date, 
                         company_info, items): #  due_date, client_info, tax_rate=0.0, notes=None, terms=None):
        self.invoice_data = {
            'invoice_number': invoice_number,
            'issue_date': issue_date,
            'company_info': company_info,
            'items': items,
            #'due_date': due_date,
            #'client_info': client_info,
            #'tax_rate': tax_rate,
            #'notes': notes,
            #'terms': terms
        }
    
    def create_title(self):
        # Title style
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Center aligned
        )
        
        # Create title
        title = Paragraph(f"{self.invoice_data['company_info']['name']} Invoice", title_style)
        self.elements.append(title)
        
        # Invoice number and dates
        invoice_info_style = ParagraphStyle(
            'InvoiceInfo',
            parent=self.styles['Normal'],
            spaceAfter=12
        )
        
        invoice_num = Paragraph(f"<b>Invoice #:</b> {self.invoice_data['invoice_number']}", invoice_info_style)
        issue_date = Paragraph(f"<b>Issue Date:</b> {self.invoice_data['issue_date']}", invoice_info_style)
        #due_date = Paragraph(f"<b>Due Date:</b> {self.invoice_data['due_date']}", invoice_info_style)
        
        info_table = Table([
            [invoice_num, issue_date]#, due_date]
        ], colWidths=[2.5*inch, 2.5*inch])#, 2.5*inch])
        
        info_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        self.elements.append(info_table)
        self.elements.append(Spacer(1, 0.25*inch))
    def get_company_text(self):
        company_data = self.invoice_data['company_info']
    
        company_text = f"<b>{company_data['name']}</b><br />"
        rest_company_info = [('Address', company_data.get('address', None)),
                             ('Zip', company_data.get('zip', None)),
                             ('Phone', company_data.get('phone', None)),
                             ('Email', company_data.get('email', None)),]
        for item in rest_company_info:
            if isinstance(item, tuple) and item[1]:
                company_text += f"{item[0]}: {item[1]}<br />"
            elif item and not isinstance(item, tuple):
                company_text += f"{item}<br/>"
        return company_text

    def create_addresses(self):
        # Company and client info
        address_style = ParagraphStyle(
            'AddressStyle',
            parent=self.styles['Normal'],
            spaceAfter=6
        )
        
        # Company info
        #company_data = self.invoice_data['company_info']
        company_text = self.get_company_text()
        
        # Client info
        #client_data = self.invoice_data['client_info']
        #client_text = f"<b>Bill To:</b><br/>" + \
        #              f"{client_data['name']}<br/>" + \
        #              f"{client_data['address']}<br/>" + \
        #              f"{client_data['city']}, {client_data['state']} {client_data['zip']}<br/>" + \
        #              f"Phone: {client_data['phone']}"
        
        #addresses_table = Table([
        #    [Paragraph(company_text, address_style), Paragraph(client_text, address_style)]
        #], colWidths=[3.5*inch, 3.5*inch])
        addresses_table = Table([
            [Paragraph(company_text, address_style)]
        ], colWidths=[3.5*inch])
        
        addresses_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        self.elements.append(addresses_table)
        self.elements.append(Spacer(1, 0.3*inch))
    
    def create_items_table(self):
        # Create items table
        items = self.invoice_data['items']
        #tax_rate = self.invoice_data['tax_rate']
        
        # Calculate totals
        subtotal = sum(item['price'] for item in items)
        total_amount = sum(item['quantity'] for item in items)
        #tax_amount = subtotal * tax_rate
        #total = subtotal + tax_amount
        
        # Table header
        data = [['Name', 'Quantity', 'Discount', 'Unit Price', 'Total']]
        
        # Add items
        for item in items:
            total_price = item['price']
            data.append([
                item['name'],
                str(item['quantity']),
                str(item['discount']),
                f"${item['unit_price']:.2f}",
                f"${total_price:.2f}"
            ])
        
        # Add summary rows
        data.append(['Quantity', f"{total_amount}", '', 'Total:', f"${subtotal:.2f}"])
        #data.append(['', '', f'Tax ({tax_rate*100:.1f}%):', f"${tax_amount:.2f}"])
        #data.append(['', '', 'Total:', f"${total:.2f}"])
        
        items_table = Table(data, colWidths=[2.5*inch, 1*inch, 1*inch, 1*inch, 2*inch])#, colWidths=[3.5*inch, 1*inch, 1.5*inch, 1.5*inch])
        
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('BOTTOMPADDING', (0, 1), (-1, -2), 8),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('FONTSIZE', (0, 0), (-1, -2), 11),

            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('LINEABOVE', (0, -1), (-1, -1), 1, colors.green),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
        ]))
            #('LINEABOVE', (0, -3), (-1, -3), 1, colors.black),
        
        self.elements.append(items_table)
        self.elements.append(Spacer(1, 0.3*inch))
    
    def create_notes_terms(self):
        pass
        #    # Add notes and terms if provided
        #    #notes = self.invoice_data.get('notes')
        #    #terms = self.invoice_data.get('terms')
        #    
        #    if notes or terms:
        #        notes_style = ParagraphStyle(
        #            'NotesStyle',
        #            parent=self.styles['Normal'],
        #            spaceAfter=6
        #        )
        #        
        #        notes_text = ""
        #        if notes:
        #            notes_text += f"<b>Notes:</b><br/>{notes}<br/><br/>"
        #        if terms:
        #            notes_text += f"<b>Terms:</b><br/>{terms}"
        #        
        #        notes_para = Paragraph(notes_text, notes_style)
        #        self.elements.append(notes_para)
    
    def generate_invoice(self):
        self.create_title()
        self.create_addresses()
        self.create_items_table()
        #self.create_notes_terms()
        
        # Build PDF
        self.doc.build(self.elements)
        
        pdf_data = self.buffer.getvalue()
        self.buffer.close()

        return pdf_data
        #print(f"Invoice generated: {self.filename}")


# Example usage
if __name__ == "__main__":
    # Create invoice generator
    invoice_gen = PDFInvoiceGenerator("../media/products/invoices/example_invoice.pdf")
    
    # Set invoice data
    company_info = {
        'name': 'Billify Solutions Inc.',
        'address': '123 Business Ave',
        'zip': '94105',
        'phone': '(555) 123-4567',
        'email': 'billing@billify.com',
        #'city': 'San Francisco',
        #'state': 'CA',
    }
    
    #client_info = {
    #    'name': 'Acme Corporation',
    #    'address': '456 Client Street',
    #    'city': 'New York',
    #    'state': 'NY',
    #    'zip': '10001',
    #    'phone': '(555) 987-6543'
    #}
    
    items = [
        {'name': 'Web Development Services', 'quantity': 10, 'unit_price': 85.00, 'price': 85 * 10, 'discount': 0},
        {'name': 'UI/UX Design', 'quantity': 5, 'unit_price': 120.00, 'price': 120 * 5, 'discount': 0},
        {'name': 'Consultation Hours', 'quantity': 3, 'unit_price': 150.00, 'price': 3 * 150, 'discount': 0},
        {'name': 'Consultation Hours', 'quantity': 3, 'unit_price': 150.00, 'price': 3 * 150, 'discount': 0},
        {'name': 'Consultation Hours', 'quantity': 3, 'unit_price': 150.00, 'price': 3 * 150, 'discount': 0},
        {'name': 'Consultation Hours', 'quantity': 3, 'unit_price': 150.00, 'price': 3 * 150, 'discount': 0},
        {'name': 'Consultation Hours', 'quantity': 3, 'unit_price': 150.00, 'price': 3 * 150, 'discount': 0},
        {'name': 'Consultation Hours', 'quantity': 3, 'unit_price': 150.00, 'price': 3 * 150, 'discount': 0},
        {'name': 'Consultation Hours', 'quantity': 3, 'unit_price': 150.00, 'price': 3 * 150, 'discount': 0},
    ]
    
    invoice_gen.set_invoice_data(
        invoice_number="INV-2023-001",
        issue_date=datetime.now().strftime("%B %d, %Y"),
        company_info=company_info,
        items=items,
        #due_date=(datetime.now() + timedelta(days=30)).strftime("%B %d, %Y"),
        #client_info=client_info,
        #tax_rate=0.08,  # 8% tax
        #notes="Thank you for your business!",
        #terms="Payment due within 30 days. Late payments subject to fee."
    )
    
    # Generate the invoice
    invoice_gen.generate_invoice()
