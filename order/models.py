from django.db import models
from authentication.models import User
from django.utils.translation import gettext as _
from products.models import Product


class Order(models.Model):
    user = models.ForeignKey(User, verbose_name=_("user"), on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name=_("product"), on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(_("quantity"), null=True, blank=True)
    total_price = models.DecimalField(_("Total Price"), max_digits=10,  decimal_places=2, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.total_price = self.product.price * self.quantity
        return super(Order, self).save(*args,  **kwargs)
    
    def  __str__(self):
        return f"{self.user.username} by {self.product.name}"