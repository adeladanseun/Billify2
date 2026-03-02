from datetime import datetime, timedelta
from random import randint

from django.db import models
from django.conf import settings
from django.core.files import File

from sales.models import *
from .product_receipt_generator import PDFInvoiceGenerator

# Create your models here.
back_path = '..'
invoices_sub_path = 'products/invoices/'
invoices_file_path = settings.MEDIA_URL + invoices_sub_path

class ProductCategoryManager(models.Manager):
    def create(self, *args, **kwargs):
        model = ProductCategory.objects.filter(**kwargs)
        if not model:
            return super().create(*args, **kwargs)
        return model[0]

class ProductCategory(models.Model):
    objects = ProductCategoryManager()

    BOOK = 0
    CONSUMABLE = 1
    ELECTRONIC = 2
    COMFORT = 3
    HEALTH = 4
    RELIGIOUS = 5
    
    CATEGORY = (
        (BOOK, 'book'),
        (CONSUMABLE, 'consumable'),
        (ELECTRONIC, 'electronic'),
        (COMFORT, 'comfort'),
        (HEALTH, 'health'),
        (RELIGIOUS, 'religious'),
    )

    category = models.IntegerField(choices=CATEGORY, default=CONSUMABLE, unique=True)

class ProductMembership(Membership):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='memberships')

class ProductImage(Image):
    #image = models.ForeignKey(Image, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)

class ProductDiscount(Discount):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='discounts')

class ProductMultiPurchase(MultiPurchase):

    def __str__(self):
        return f'Id {self.id} Total Price {self.price}'
    
    @property
    def product(self):
        return self.purchases.all()

    @property
    def owner(self):
        if self.purchases.count():
            return self.purchases.first().owner

    def invoice_format(self, id):
        string_length = 8
        id_string = str(id)
        if len(id_string) < string_length:
            return f'0'*(string_length - len(id_string)) + id_string
        return id_string

    def generate_invoice(self, new=False):
        """Generates a new invoice if no previous invoice exists and returns the invoice """
        filename = f'Invoice_{self.id}_{randint(1000, 10000)}.pdf'#{invoices_file_path}
        invoice_gen = PDFInvoiceGenerator(filename)

        company_address = self.company.address if self.company.show_address_on_receipt else None

        company_info = {
            'name': self.company.name,
            'email': self.company.email,
            'phone': self.company.phone_number,
            'zip': self.company.zip,
        }
        if company_address:
            company_info['address'] = company_address
        
        items = [
            {
                'name': purchase.membership_name, 
                'quantity': purchase.amount, 
                'unit_price': purchase.price, 
                'price': purchase.price_given_discount,
                'discount': purchase.discount,
            } for purchase in self.purchases.all()
        ]

        invoice_gen.set_invoice_data(
            invoice_number = self.invoice_format(self.id),
            issue_date = datetime.now().strftime("%B %d, %Y"),
            company_info = company_info,
            items = items,
        )

        pdf_data = invoice_gen.generate_invoice()

        try:
            invoice = self.invoice.pdf
        except:
            invoice = None

        if not (invoice and not new):
            with open(filename, 'wb') as f:
                f.write(pdf_data)
            with open(filename, 'rb') as f:
                invoice = Invoice.objects.create(pdf=File(f), multi_purchase=self)

        return (self, invoice)
        
class ProductIndividualPurchase(IndividualPurchase):
    multi_purchase_class = ProductMultiPurchase
    
    #product = models.ForeignKey('Product', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='individual_purchases')
    multi_purchase = models.ForeignKey(multi_purchase_class, on_delete=models.CASCADE, null=True, related_name='purchases')

    @property
    def owner(self):
        return self.product.owner

class ProductManager(MainObjectDefaultManager):
    pass

class Product(MainObjectDefault):
    owner = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='products')
    categories = models.ManyToManyField(ProductCategory)
    
    objects = ProductManager()
    membership_class = ProductMembership
    individual_purchase_class = ProductIndividualPurchase
    discount_class = ProductDiscount
    
    @property
    def producer(self):
        return self.owner
    
    @property
    def manufacturer(self):
        return self.owner
    
        
class Invoice(Receipt):
    pdf = models.FileField(upload_to=invoices_sub_path, max_length=100)
    multi_purchase = models.OneToOneField(ProductMultiPurchase, on_delete=models.CASCADE, related_name='invoice')

    def __str__(self):
        return f"Company {self.multi_purchase.company.name} -> P_Id: {self.multi_purchase.id} -> {self.pdf.name.split('/')[-1]}"