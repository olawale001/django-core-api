from django.db import models
from django.utils.translation import gettext as _
from authentication.models import User


CATEGORY_CHOICES =[
    ("men-clothig", "Men Clothing"),
    ("women-clothing", "Women Clothing"),
    ("kid-clothing", "Kid Clothing"),
    ("watches", "Watches"),
    ("shoes & handbags", "Shoes & Handbags"),
    ("books", "Books"),
    ("home & kitchen", "Home & Kitchen"),
    ("health & personalcares", "Health & Personalcares"),
    ("gifts", "Gifts"),
] 

class Product(models.Model):
    user = models.ForeignKey(User, verbose_name=_('User'), null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(_('name'), max_length=100, null=True, blank=True)
    price = models.DecimalField(_('price'), max_digits=10, decimal_places=2, null=True, blank=True)
    category = models.CharField(_('category'), choices=CATEGORY_CHOICES, null=True, blank=True)
    description = models.TextField(_('description'), null=True, blank=True)
    image = models.ImageField(upload_to="product-image/")
    created_at = models.DateTimeField(auto_now_add=True, null=True)
