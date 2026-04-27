from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):

    CATEGORY_CHOICES = [
        ('baby', 'Baby Care'),
        ('firstaid', 'First Aid'),
        ('personal', 'Personal Care'),
        ('medicine', 'Medicines'),
        ('device', 'Health Devices'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.FloatField()
    discount_percentage = models.FloatField(default=0.0)  # ✅ NEW
    stock_quantity = models.PositiveIntegerField(default=10)  # ✅ NEW
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='medicine')
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)

    @property
    def discounted_price(self):
        return self.price * (1 - self.discount_percentage / 100)

    def __str__(self):
        return f"{self.name} ({self.category})"
        
        
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    mobile = models.CharField(max_length=15, unique=True, null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], null=True, blank=True)
    
    def __str__(self):
        return self.user.username


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.product.discounted_price * self.quantity

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'product')

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
        ('Packed', 'Packed'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.TextField()
    mobile = models.CharField(max_length=15)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.FloatField()

    def subtotal(self):
        return self.quantity * self.price

class Invoice(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='invoice')
    serial_number = models.CharField(max_length=50, unique=True)
    pdf = models.FileField(upload_to='invoices/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice {self.serial_number} for Order #{self.order.id}"