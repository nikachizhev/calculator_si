from django.db import models


class Calculation(models.Model):
    client_id = models.CharField(max_length=100, db_index=True)
    expression = models.CharField(max_length=200)
    result = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.expression} = {self.result}"
