from django.shortcuts import render, redirect, get_object_or_404
from django.forms import formset_factory
from django.http import HttpResponse
from .models import Vehicle, VehicleImage, FaultyPart, FaultyPartImage, WheelImage, VehicleDocument
from .forms import VehicleForm, VehicleImageForm, FaultyPartForm, FaultyPartImageForm, WheelImageForm, VehicleDocumentForm
import json
import zipfile
import os
from io import BytesIO
from django.conf import settings

def home(request):
    vehicles = Vehicle.objects.all()
    return render(request, 'home.html', {'vehicles': vehicles})

def add_vehicle(request):
    VehicleImageFormSet = formset_factory(VehicleImageForm, extra=1)
    WheelImageFormSet = formset_factory(WheelImageForm, extra=1)
    VehicleDocumentFormSet = formset_factory(VehicleDocumentForm, extra=1)

    if request.method == 'POST':
        vehicle_form = VehicleForm(request.POST)
        vehicle_image_formset = VehicleImageFormSet(request.POST, request.FILES, prefix='vehicle_images')
        wheel_image_formset = WheelImageFormSet(request.POST, request.FILES, prefix='wheel_images')
        document_formset = VehicleDocumentFormSet(request.POST, request.FILES, prefix='documents')

        if (vehicle_form.is_valid() and vehicle_image_formset.is_valid() and
            wheel_image_formset.is_valid() and document_formset.is_valid()):
            vehicle = vehicle_form.save()

            # Save vehicle images
            for form in vehicle_image_formset:
                if form.cleaned_data.get('image'):
                    VehicleImage.objects.create(vehicle=vehicle, image=form.cleaned_data['image'])

            # Save wheel images
            for form in wheel_image_formset:
                if form.cleaned_data.get('image'):
                    WheelImage.objects.create(vehicle=vehicle, image=form.cleaned_data['image'])

            # Save documents
            for form in document_formset:
                if form.cleaned_data.get('document'):
                    VehicleDocument.objects.create(vehicle=vehicle, document=form.cleaned_data['document'])

            return redirect('vehicle_detail', vehicle_id=vehicle.id)
    else:
        vehicle_form = VehicleForm()
        vehicle_image_formset = VehicleImageFormSet(prefix='vehicle_images')
        wheel_image_formset = WheelImageFormSet(prefix='wheel_images')
        document_formset = VehicleDocumentFormSet(prefix='documents')

    return render(request, 'add_vehicle.html', {
        'vehicle_form': vehicle_form,
        'vehicle_image_formset': vehicle_image_formset,
        'wheel_image_formset': wheel_image_formset,
        'document_formset': document_formset,
    })

def vehicle_detail(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    FaultyPartImageFormSet = formset_factory(FaultyPartImageForm, extra=1)

    if request.method == 'POST':
        faulty_part_form = FaultyPartForm(request.POST)
        faulty_part_image_formset = FaultyPartImageFormSet(request.POST, request.FILES, prefix='faulty_part_images')

        if faulty_part_form.is_valid() and faulty_part_image_formset.is_valid():
            faulty_part = faulty_part_form.save(commit=False)
            faulty_part.vehicle = vehicle
            faulty_part.save()

            # Save faulty part images
            for form in faulty_part_image_formset:
                if form.cleaned_data.get('image'):
                    FaultyPartImage.objects.create(faulty_part=faulty_part, image=form.cleaned_data['image'])

            return redirect('vehicle_detail', vehicle_id=vehicle.id)
    else:
        faulty_part_form = FaultyPartForm()
        faulty_part_image_formset = FaultyPartImageFormSet(prefix='faulty_part_images')

    return render(request, 'vehicle_detail.html', {
        'vehicle': vehicle,
        'faulty_part_form': faulty_part_form,
        'faulty_part_image_formset': faulty_part_image_formset,
    })

def backup_data(request):
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        vehicles = Vehicle.objects.all()
        vehicle_data = []
        for vehicle in vehicles:
            vehicle_dict = {
                'id': vehicle.id,
                'car_number': vehicle.car_number,
                'brand': vehicle.brand,
                'kilometers': vehicle.kilometers,
                'cylinder_count': vehicle.cylinder_count,
                'mesures': vehicle.mesures,
                'ligne': vehicle.ligne,
                'entry_date': str(vehicle.entry_date),
                'faulty_parts': [
                    {
                        'part_name': part.part_name,
                        'description': part.description,
                        'images': [image.image.name for image in part.images.all()]
                    } for part in vehicle.faulty_parts.all()
                ],
                'images': [image.image.name for image in vehicle.images.all()],
                'wheel_images': [image.image.name for image in vehicle.wheel_images.all()],
                'documents': [doc.document.name for doc in vehicle.documents.all()]
            }
            vehicle_data.append(vehicle_dict)

        zip_file.writestr('vehicles.json', json.dumps(vehicle_data, indent=2))

        for vehicle in vehicles:
            for image in vehicle.images.all():
                if os.path.exists(image.image.path):
                    zip_file.write(image.image.path, image.image.name)
            for wheel_image in vehicle.wheel_images.all():
                if os.path.exists(wheel_image.image.path):
                    zip_file.write(wheel_image.image.path, wheel_image.image.name)
            for document in vehicle.documents.all():
                if os.path.exists(document.document.path):
                    zip_file.write(document.document.path, document.document.name)
            for part in vehicle.faulty_parts.all():
                for image in part.images.all():
                    if os.path.exists(image.image.path):
                        zip_file.write(image.image.path, image.image.name)

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="vehicle_backup.zip"'
    return response
