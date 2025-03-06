from django.db import models


# Create your models here.
class Challenge(models.Model):
    id = models.AutoField(primary_key=True)

    icon = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    description = models.TextField()
    tags = models.JSONField(default=list)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]
