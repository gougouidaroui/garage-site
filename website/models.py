from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
import os

def vehicle_image_upload_path(instance, filename):
    # Structure: year/month/day/car-number/images/filename
    date = instance.vehicle.entry_date
    car_number = instance.vehicle.car_number
    return os.path.join(
        str(date.year),
        str(date.month).zfill(2),
        str(date.day).zfill(2),
        car_number,
        'images',
        filename
    )

def faulty_part_image_upload_path(instance, filename):
    # Structure: year/month/day/car-number/images/filename
    date = instance.faulty_part.vehicle.entry_date
    car_number = instance.faulty_part.vehicle.car_number
    return os.path.join(
        str(date.year),
        str(date.month).zfill(2),
        str(date.day).zfill(2),
        car_number,
        'images',
        filename
    )

def wheel_image_upload_path(instance, filename):
    # Structure: year/month/day/car-number/images/filename
    date = instance.vehicle.entry_date
    car_number = instance.vehicle.car_number
    return os.path.join(
        str(date.year),
        str(date.month).zfill(2),
        str(date.day).zfill(2),
        car_number,
        'images',
        filename
    )

# Vehicle model to store vehicle details
class Vehicle(models.Model):
    entry_date = models.DateField(auto_now_add=True)
    car_number = models.CharField(max_length=20, unique=True)
    brand = models.CharField(max_length=50)
    kilometers = models.PositiveIntegerField()
    cylinder_count = models.PositiveIntegerField()
    mesures = models.CharField(max_length=100, blank=True)
    ligne = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.car_number} - {self.brand}"

# Image model for vehicle images
class VehicleImage(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=vehicle_image_upload_path)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.vehicle.car_number}"

# Faulty part model
class FaultyPart(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='faulty_parts')
    part_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.part_name} for {self.vehicle.car_number}"

# Image model for faulty parts
class FaultyPartImage(models.Model):
    faulty_part = models.ForeignKey(FaultyPart, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=faulty_part_image_upload_path)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.faulty_part.part_name}"

# Image model for wheels
class WheelImage(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='wheel_images')
    image = models.ImageField(upload_to=wheel_image_upload_path)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Wheel image for {self.vehicle.car_number}"

# Document model for additional documents
class VehicleDocument(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='documents')
    document = models.FileField(upload_to=vehicle_image_upload_path)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Document for {self.vehicle.car_number}"

# File deletion signals
@receiver(post_delete)
def delete_files_when_row_deleted_from_db(sender, instance, **kwargs):
    for field in sender._meta.concrete_fields:
        if isinstance(field, models.FileField):
            instance_file_field = getattr(instance, field.name)
            delete_file_if_unused(sender, instance, field, instance_file_field)

@receiver(pre_save)
def delete_files_when_file_changed(sender, instance, **kwargs):
    if not instance.pk:
        return
    for field in sender._meta.concrete_fields:
        if isinstance(field, models.FileField):
            try:
                instance_in_db = sender.objects.get(pk=instance.pk)
            except sender.DoesNotExist:
                return
            instance_in_db_file_field = getattr(instance_in_db, field.name)
            instance_file_field = getattr(instance, field.name)
            if instance_in_db_file_field.name != instance_file_field.name:
                delete_file_if_unused(sender, instance, field, instance_in_db_file_field)

def delete_file_if_unused(model, instance, field, instance_file_field):
    dynamic_field = {field.name: instance_file_field.name}
    other_refs_exist = model.objects.filter(**dynamic_field).exclude(pk=instance.pk).exists()
    if not other_refs_exist and instance_file_field:
        instance_file_field.delete(False)
