from django.db import models

class Appointment(models.Model):
    doctor = models.CharField(max_length=100)
    hospital = models.CharField(max_length=200)
    date = models.DateField()
    time = models.TimeField()
    department = models.CharField(max_length=100)
    purpose = models.TextField()

    def __str__(self):
        return self.doctor
class UserProfile(models.Model):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=100)
    emergency_contact = models.CharField(max_length=20)
    primary_doctor = models.CharField(max_length=100)
    current_medications = models.TextField()
    blood_group = models.CharField(max_length=10)
    allergies = models.TextField()

    def __str__(self):
        return self.full_name