from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
import os

def attachment_upload_path(instance, filename):
    date = instance.cycle.date
    control_type = instance.cycle.control_type
    cycle_id = instance.cycle.cycle_id
    return os.path.join(
        control_type,
        str(date.year),
        str(date.month).zfill(2),
        str(date.day).zfill(2),
        cycle_id,
        filename
    )

class Cycle(models.Model):
    CONTROL_TYPES = (
        ('mutation', 'Mutation'),
        ('parc_neuf', 'Parc Neuf'),
        ('duplicata', 'Duplicata'),
    )
    control_type = models.CharField(max_length=20, choices=CONTROL_TYPES)
    date = models.DateField()
    cycle_id = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Replace spaces with hyphens in cycle_id before saving
        self.cycle_id = self.cycle_id.replace(' ', '-')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.control_type} - {self.cycle_id} ({self.date})"

class Attachment(models.Model):
    ATTACHMENT_TYPES = (
        ('photo', 'Photo'),
        ('video', 'Video'),
    )
    file = models.ImageField(upload_to=attachment_upload_path)
    file_type = models.CharField(max_length=10, choices=ATTACHMENT_TYPES, default='photo')
    cycle = models.ForeignKey(Cycle, on_delete=models.CASCADE, related_name='attachments')

    def __str__(self):
        return f"Attachment for {self.cycle.cycle_id}"

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
