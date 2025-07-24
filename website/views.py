from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.utils.dateparse import parse_date
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
    cycles = Cycle.objects.all()
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        # Validate and convert dates
        start_date_obj = parse_date(start_date) if start_date else None
        end_date_obj = parse_date(end_date) if end_date else None
        if start_date_obj and end_date_obj:
            if start_date_obj <= end_date_obj:
                cycles = Cycle.objects.filter(date__range=[start_date_obj, end_date_obj])
            else:
                cycles = Cycle.objects.filter(date__range=[end_date_obj, start_date_obj])
        elif not start_date and not end_date:
            # No filtering if both are empty
            pass
        else:
            cycles = Cycle.objects.none()

    paginator = Paginator(cycles, 5)  # Show 5 cycles per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == 'POST' and 'backup' in request.POST:
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        start_date_obj = parse_date(start_date) if start_date else None
        end_date_obj = parse_date(end_date) if end_date else None
        if start_date_obj and end_date_obj:
            if start_date_obj <= end_date_obj:
                cycles = Cycle.objects.filter(date__range=[start_date_obj, end_date_obj])
            else:
                cycles = Cycle.objects.filter(date__range=[end_date_obj, start_date_obj])
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

    return render(request, 'backup.html', {'page_obj': page_obj})

def search_cycles(request):
    cycles = Cycle.objects.all()
    sort_order = request.GET.get('sort', 'asc')
    if sort_order == 'desc':
        cycles = cycles.order_by('-date')
    else:
        cycles = cycles.order_by('date')

    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        cycle_id = request.POST.get('cycle_id', '').replace(' ', '-')
        # Validate and convert dates
        start_date_obj = parse_date(start_date) if start_date else None
        end_date_obj = parse_date(end_date) if end_date else None
        if start_date_obj and end_date_obj:
            if start_date_obj <= end_date_obj:
                cycles = cycles.filter(date__range=[start_date_obj, end_date_obj])
            else:
                cycles = cycles.filter(date__range=[end_date_obj, start_date_obj])
        if cycle_id:
            cycles = cycles.filter(cycle_id__icontains=cycle_id)  # Case-insensitive contains
        elif not start_date and not end_date:
            # No filtering if both date fields are empty and no cycle_id
            pass
        else:
            cycles = Cycle.objects.none()

    paginator = Paginator(cycles, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'search_cycles.html', {'page_obj': page_obj, 'sort_order': sort_order})

def cycle_images(request, cycle_id):
    cycle_id = cycle_id.replace(' ', '-')
    cycle = get_object_or_404(Cycle, cycle_id=cycle_id)
    images = [{'id': a.id, 'url': a.file.url} for a in cycle.attachments.all()]
    return JsonResponse({'images': images})
