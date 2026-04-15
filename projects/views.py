from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Project


def project_list(request):
    projects = list(Project.objects.all().order_by('order'))
    
    overdue_count = sum(1 for p in projects if p.status == 'overdue')
    
    context = {
        'projects': projects,
        'overdue_count': overdue_count,
    }
    return render(request, 'projects/index.html', context)


@csrf_exempt
def project_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        project_type = request.POST.get('type', 'corporate')
        due_date = request.POST.get('due_date', '')
        next_action = request.POST.get('next_action', '').strip()
        
        if not name:
            return JsonResponse({'error': 'Name is required'}, status=400)
        
        if project_type == 'corporate' and not due_date:
            return JsonResponse({'error': 'Due date is required for corporate projects'}, status=400)
        
        project = Project.objects.create(
            name=name,
            project_type=project_type,
            due_date=due_date if due_date else None,
            next_action=next_action
        )
        
        return JsonResponse({'success': True, 'id': project.id})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def project_update(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        project_type = request.POST.get('type', 'corporate')
        due_date = request.POST.get('due_date', '')
        next_action = request.POST.get('next_action', '').strip()
        
        if not name:
            return JsonResponse({'error': 'Name is required'}, status=400)
        
        if project_type == 'corporate' and not due_date:
            return JsonResponse({'error': 'Due date is required for corporate projects'}, status=400)
        
        project.name = name
        project.project_type = project_type
        project.due_date = due_date if due_date else None
        project.next_action = next_action
        project.save()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def project_delete(request, pk):
    if request.method == 'POST':
        project = get_object_or_404(Project, pk=pk)
        project.delete()
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


def project_detail_api(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return JsonResponse({
        'id': project.id,
        'name': project.name,
        'project_type': project.project_type,
        'due_date': project.due_date.isoformat() if project.due_date else '',
        'next_action': project.next_action,
    })


@csrf_exempt
def reorder_projects(request):
    if request.method == 'POST':
        import json
        try:
            order_data = json.loads(request.POST.get('order_data', '[]'))
            for item in order_data:
                project = get_object_or_404(Project, pk=item['id'])
                project.order = item['order']
                project.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
