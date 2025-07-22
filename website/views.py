from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
import zipfile
import os
from io import BytesIO
from .models import Cycle, Attachment
from .forms import CycleForm
import logging

# Set up logging
logger = logging.getLogger(__name__)

def home(request):
    cycles = Cycle.objects.all()
    return render(request, 'home.html', {'cycles': cycles})

def add_cycle(request):
    if request.method == 'POST':
        cycle_form = CycleForm(request.POST)
        if cycle_form.is_valid():
            cycle = cycle_form.save()
            if 'bulk_images' in request.FILES:
                for image in request.FILES.getlist('bulk_images'):
                    logger.info(f"Processing image: {image.name} for cycle {cycle.cycle_id}")
                    try:
                        attachment = Attachment.objects.create(cycle=cycle, file=image, file_type='photo')
                        logger.info(f"Saved image to: {attachment.file.path}")
                    except Exception as e:
                        logger.error(f"Failed to save image {image.name}: {e}")
            return redirect('home')
    else:
        cycle_form = CycleForm()
    return render(request, 'add_cycle.html', {'cycle_form': cycle_form})

def modify_cycle(request, cycle_id):
    cycle_id = cycle_id.replace(' ', '-')
    cycle = get_object_or_404(Cycle, cycle_id=cycle_id)
    if request.method == 'POST':
        cycle_form = CycleForm(request.POST, instance=cycle)
        if cycle_form.is_valid():
            cycle = cycle_form.save()
            if 'delete_attachments' in request.POST:
                delete_ids = request.POST.getlist('delete_attachments')
                cycle.attachments.filter(id__in=delete_ids).delete()
            if 'bulk_images' in request.FILES:
                for image in request.FILES.getlist('bulk_images'):
                    logger.info(f"Processing image: {image.name} for cycle {cycle.cycle_id}")
                    try:
                        attachment = Attachment.objects.create(cycle=cycle, file=image, file_type='photo')
                        logger.info(f"Saved image to: {attachment.file.path}")
                    except Exception as e:
                        logger.error(f"Failed to save image {image.name}: {e}")
            return redirect('home')
    else:
        cycle_form = CycleForm(instance=cycle)
    return render(request, 'modify_cycle.html', {'cycle_form': cycle_form, 'cycle': cycle})

def backup_data(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        cycles = Cycle.objects.filter(date__range=[start_date, end_date])

        buffer = BytesIO()
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for cycle in cycles:
                folder_path = f"{cycle.control_type}/{cycle.date.strftime('%Y')}/{cycle.date.strftime('%m')}/{cycle.date.strftime('%d')}/{cycle.cycle_id}"
                info_content = f"Type: {cycle.control_type}\nDate: {cycle.date}\nID: {cycle.cycle_id}"
                zip_file.writestr(f"{folder_path}/info.txt", info_content)
                for attachment in cycle.attachments.all():
                    if os.path.exists(attachment.file.path):
                        zip_file.write(attachment.file.path, f"{folder_path}/{os.path.basename(attachment.file.path)}")

        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="cycle_backup_{start_date}_to_{end_date}.zip"'
        return response
    return render(request, 'backup.html')

def search_cycles(request):
    cycles = []
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        if start_date and end_date:
            cycles = Cycle.objects.filter(date__range=[start_date, end_date])
    return render(request, 'search_cycles.html', {'cycles': cycles})

def cycle_images(request, cycle_id):
    cycle_id = cycle_id.replace(' ', '-')
    cycle = get_object_or_404(Cycle, cycle_id=cycle_id)
    images = [{'id': a.id, 'url': a.file.url} for a in cycle.attachments.all()]
    return JsonResponse({'images': images})
