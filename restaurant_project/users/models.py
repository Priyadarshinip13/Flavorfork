from django.db import models
from django.contrib.auth.models import User
from restaurant.models import MenuItem  # ✅ Add this line!

class OrderTheItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def subtotal(self):
        return self.menu_item.price * self.quantity
