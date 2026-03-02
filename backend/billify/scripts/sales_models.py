from sales.models import Company
from django.contrib.auth.models import User
def run(*args):
    company = Company.objects.all()
    company.delete()

    newCompany = Company.objects.create(
        name = "Seun Company",
    )
    adeladanseun = User.objects.get_or_create(username="adeladanseun")[0]
    newCompany.staffs.add(adeladanseun)