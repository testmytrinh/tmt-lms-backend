from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class Term(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.name
