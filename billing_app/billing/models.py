from django.db import models
from datetime import date

class Item(models.Model):
    name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    expiry_date = models.DateField()
    
    @property
    def days_until_expiry(self):
        return (self.expiry_date - date.today()).days if self.expiry_date else None

    def __str__(self):
        return self.name
    
class Notification(models.Model):
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
