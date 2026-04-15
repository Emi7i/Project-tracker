from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Project


def project_list(request):
    sort_by = request.session.get('sort_by', 'custom')
    group_by = request.session.get('group_by', 'none')
    type_swap = request.session.get('type_swap', False)  # False = corporate first, True = personal first
    
    if sort_by == 'status':
        projects = list(Project.objects.all().order_by('manual_status', 'order'))
    elif sort_by == 'priority':
        # Priority order: urgent, high, medium, low
        projects = list(Project.objects.all().extra(
            select={'priority_order': "CASE priority WHEN 'urgent' THEN 1 WHEN 'high' THEN 2 WHEN 'medium' THEN 3 WHEN 'low' THEN 4 ELSE 5 END"}
        ).order_by('priority_order', 'order'))
    else:
        projects = list(Project.objects.all().order_by('order'))
    
    overdue_count = sum(1 for p in projects if p.status == 'overdue')
    
    status_options = Project.STATUS_CHOICES + [(None, 'auto')]
    priority_options = Project.PRIORITY_CHOICES
    
    sort_options = [
        ('custom', 'Custom'),
        ('status', 'Status'),
        ('priority', 'Priority'),
    ]
    
    group_options = [
        ('none', 'None'),
        ('status', 'Status'),
        ('priority', 'Priority'),
        ('type', 'Type'),
    ]
    
    # Get current sort label
    sort_label = dict(sort_options).get(sort_by, 'Custom')
    
    # Get current group label
    group_label = dict(group_options).get(group_by, 'None')
    
    # Handle grouping
    grouped_projects = []
    if group_by == 'status':
        # Group by status
        status_dict = dict(Project.STATUS_CHOICES)
        for value, label in Project.STATUS_CHOICES + [(None, 'auto')]:
            group_projects = [p for p in projects if p.manual_status == value]
            if group_projects:
                grouped_projects.append({
                    'group_label': label,
                    'group_value': value,
                    'projects': group_projects
                })
    elif group_by == 'priority':
        # Group by priority
        priority_dict = dict(Project.PRIORITY_CHOICES)
        for value, label in Project.PRIORITY_CHOICES:
            group_projects = [p for p in projects if p.priority == value]
            if group_projects:
                grouped_projects.append({
                    'group_label': label,
                    'group_value': value,
                    'projects': group_projects
                })
    elif group_by == 'type':
        # Group by project type (corporate/personal)
        type_order = [('personal', 'Personal'), ('corporate', 'Corporate')] if type_swap else [('corporate', 'Corporate'), ('personal', 'Personal')]
        for value, label in type_order:
            group_projects = [p for p in projects if p.project_type == value]
            if group_projects:
                grouped_projects.append({
                    'group_label': label,
                    'group_value': value,
                    'projects': group_projects
                })
    else:
        # No grouping
        grouped_projects = [{'group_label': None, 'group_value': None, 'projects': projects}]
    
    context = {
        'projects': projects,
        'grouped_projects': grouped_projects,
        'overdue_count': overdue_count,
        'status_options': status_options,
        'priority_options': priority_options,
        'sort_options': sort_options,
        'group_options': group_options,
        'current_sort': sort_by,
        'current_sort_label': sort_label,
        'current_group': group_by,
        'current_group_label': group_label,
        'type_swap': type_swap,
    }
    return render(request, 'projects/index.html', context)


@csrf_exempt
def set_sort(request):
    if request.method == 'POST':
        sort_by = request.POST.get('sort_by', 'custom')
        # Store sort preference in session
        request.session['sort_by'] = sort_by
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

@csrf_exempt
def set_group(request):
    if request.method == 'POST':
        group_by = request.POST.get('group_by', 'none')
        # Store group preference in session
        request.session['group_by'] = group_by
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

@csrf_exempt
def swap_type_order(request):
    if request.method == 'POST':
        # Toggle the swap preference
        current_swap = request.session.get('type_swap', False)
        request.session['type_swap'] = not current_swap
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

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


@csrf_exempt
def update_project_status(request, pk):
    if request.method == 'POST':
        project = get_object_or_404(Project, pk=pk)
        status = request.POST.get('status', '')
        project.manual_status = status if status else None
        project.save()
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def update_project_priority(request, pk):
    if request.method == 'POST':
        project = get_object_or_404(Project, pk=pk)
        priority = request.POST.get('priority', 'medium')
        project.priority = priority
        project.save()
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
