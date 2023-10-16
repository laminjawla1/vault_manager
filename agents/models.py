from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.utils import timezone



class Zone(models.Model):
    name = models.CharField(max_length=50)
    supervisor = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self) -> str:
        return self.name


class Branch(models.Model):
    class Meta:
        verbose_name_plural = "Branches"
    name = models.CharField(max_length=50)
    teller = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self) -> str:
        return self.name

    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='profile_pics/default.png', upload_to='profile_pics')
    zone = models.ForeignKey(Zone, on_delete=models.PROTECT, null=True, blank=True)
    branch = models.ForeignKey(Branch, on_delete=models.PROTECT, null=True, blank=True)
    is_cashier = models.BooleanField(default=False)
    is_supervisor = models.BooleanField(default=False)
    opening_cash = models.FloatField(null=False, default=0.0)
    additional_cash = models.FloatField(null=False, default=0.0)
    closing_balance = models.FloatField(null=False, default=0.0)
    balance = models.FloatField(null=False, default=0.0)

    def __str__(self) -> str:
        return f"{self.user.username}'s profile"
    
    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)

        image = Image.open(self.image.path)
        if image.height > 300 or image.width > 300:
            output_size = (300, 300)
            image.thumbnail(output_size)
            image.save(self.image.path)

class Ledger(models.Model):
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="agents")
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="added_by", null=True, blank=True)
    date = models.DateTimeField(null=False, default=timezone.now)
    narration = models.TextField()
    debit = models.FloatField(null=False, default=0.0)
    credit = models.FloatField(null=False, default=0.0)
    balance = models.FloatField(null=False, default=0.0)

    def __str__(self):
        return self.agent.username