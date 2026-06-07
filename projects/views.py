from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Project, Section, Task, TaskStatus


def ensure_default_statuses(project):
    if not project.custom_statuses.exists():
        TaskStatus.objects.create(project=project, name='TODO', color='#bfdbfe', order=1)
        TaskStatus.objects.create(project=project, name='In review', color='#fef08a', order=2)
        TaskStatus.objects.create(project=project, name='Done', color='#bbf7d0', order=3)


def project_list(request):
    sort_by = request.session.get('sort_by', 'custom')
    group_by = request.session.get('group_by', 'none')
    type_swap = request.session.get('type_swap', False)  # False = corporate first, True = personal first
    
    # Use select_related for next_task to avoid N+1 queries
    queryset = Project.objects.all().select_related('next_task')
    
    if sort_by == 'status':
        projects = list(queryset.order_by('manual_status', 'order'))
    elif sort_by == 'priority':
        # Priority order: urgent, high, medium, low
        projects = list(queryset.extra(
            select={'priority_order': "CASE priority WHEN 'urgent' THEN 1 WHEN 'high' THEN 2 WHEN 'medium' THEN 3 WHEN 'low' THEN 4 ELSE 5 END"}
        ).order_by('priority_order', 'order'))
    else:
        projects = list(queryset.order_by('order'))
    
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
            group_projects = [p for p in projects if p.status == value]
            if group_projects:
                grouped_projects.append({
                    'group_label': label,
                    'group_value': value,
                    'projects': group_projects
                })
    elif group_by == 'priority':
        # Group by priority (in order of urgency - reverse of defined order)
        for value, label in reversed(Project.PRIORITY_CHOICES):
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
        next_action_name = request.POST.get('next_action', '').strip()
        
        if not name:
            return JsonResponse({'error': 'Name is required'}, status=400)
        
        if project_type == 'corporate' and not due_date:
            return JsonResponse({'error': 'Due date is required for corporate projects'}, status=400)
        
        project = Project.objects.create(
            name=name,
            project_type=project_type,
            due_date=due_date if due_date else None
        )
        
        # Create TODO section and initial task if next_action provided
        if next_action_name:
            ensure_default_statuses(project)
            todo_section = Section.objects.create(project=project, name='TODO', order=1)
            status = project.custom_statuses.filter(name='TODO').first() or project.custom_statuses.first()
            task = Task.objects.create(section=todo_section, name=next_action_name, status_obj=status)
            project.next_task = task
            project.save()
        
        return JsonResponse({'success': True, 'id': project.id})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def project_update(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        project_type = request.POST.get('type', 'corporate')
        due_date = request.POST.get('due_date', '')
        next_task_id = request.POST.get('next_task_id', '')
        
        if not name:
            return JsonResponse({'error': 'Name is required'}, status=400)
        
        if project_type == 'corporate' and not due_date:
            return JsonResponse({'error': 'Due date is required for corporate projects'}, status=400)
        
        project.name = name
        project.project_type = project_type
        project.due_date = due_date if due_date else None
        
        if next_task_id:
            project.next_task = get_object_or_404(Task, pk=next_task_id)
        else:
            project.next_task = None
            
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
    # Include all tasks for the next action dropdown
    all_tasks = Task.objects.filter(section__project=project)
    tasks_data = [{'id': t.id, 'name': t.name} for t in all_tasks]
    
    return JsonResponse({
        'id': project.id,
        'name': project.name,
        'project_type': project.project_type,
        'due_date': project.due_date.isoformat() if project.due_date else '',
        'next_task_id': project.next_task.id if project.next_task else '',
        'all_tasks': tasks_data
    })


@csrf_exempt
def set_next_task_api(request, project_id):
    if request.method == 'POST':
        project = get_object_or_404(Project, pk=project_id)
        task_id = request.POST.get('task_id')
        if task_id:
            task = get_object_or_404(Task, pk=task_id)
            project.next_task = task
        else:
            project.next_task = None
        project.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)


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


def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    ensure_default_statuses(project)
    sections = project.sections.all().order_by('order')
    
    # Prefetch tasks with dynamic sorting per section
    for section in sections:
        tasks = section.tasks.all().select_related('status_obj', 'waiting_on')
        if section.sort_by == 'deadline':
            tasks = tasks.order_by('due_date', 'order')
        elif section.sort_by == 'status':
            tasks = tasks.order_by('status_obj__order', 'order')
        else: # custom
            tasks = tasks.order_by('order')
        section.sorted_tasks = tasks

    all_tasks = Task.objects.filter(section__project=project)
    context = {
        'project': project,
        'sections': sections,
        'all_tasks': all_tasks,
        'statuses': project.custom_statuses.all(),
    }
    return render(request, 'projects/detail.html', context)


@csrf_exempt
def create_section(request, project_id):
    if request.method == 'POST':
        project = get_object_or_404(Project, pk=project_id)
        name = request.POST.get('name', 'New Section')
        section = Section.objects.create(project=project, name=name)
        return JsonResponse({'success': True, 'id': section.id, 'name': section.name})
    return JsonResponse({'success': False}, status=400)


@csrf_exempt
def create_task(request, section_id):
    if request.method == 'POST':
        section = get_object_or_404(Section, pk=section_id)
        name = request.POST.get('name', 'New Task')
        # Use first available status or None
        status = section.project.custom_statuses.first()
        task = Task.objects.create(section=section, name=name, status_obj=status)
        return JsonResponse({
            'success': True, 
            'id': task.id, 
            'name': task.name, 
            'status': task.status_obj.name if task.status_obj else 'None',
            'status_id': task.status_obj.id if task.status_obj else None,
            'status_color': task.status_obj.color if task.status_obj else '#9ca3af',
            'status_text_color': task.status_obj.text_color if task.status_obj else '#111827'
        })
    return JsonResponse({'success': False}, status=400)


@csrf_exempt
def update_task_api(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(Task, pk=task_id)
        field = request.POST.get('field')
        value = request.POST.get('value')
        
        if field == 'status':
            status = get_object_or_404(TaskStatus, pk=value)
            task.status_obj = status
        elif field == 'due_date':
            task.due_date = value if value else None
        elif field == 'time_tracked':
            task.time_tracked = float(value) if value else 0
        elif field == 'name':
            task.name = value
        elif field == 'waiting_on':
            if value:
                task.waiting_on = get_object_or_404(Task, pk=value)
            else:
                task.waiting_on = None
            
        task.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)


@csrf_exempt
def delete_task_api(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(Task, pk=task_id)
        task.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)


@csrf_exempt
def delete_section_api(request, section_id):
    if request.method == 'POST':
        section = get_object_or_404(Section, pk=section_id)
        section.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)


@csrf_exempt
def update_section_api(request, section_id):
    if request.method == 'POST':
        section = get_object_or_404(Section, pk=section_id)
        name = request.POST.get('name')
        if name:
            section.name = name
            section.save()
            return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)


@csrf_exempt
def update_project_name_api(request, project_id):
    if request.method == 'POST':
        project = get_object_or_404(Project, pk=project_id)
        name = request.POST.get('name')
        if name:
            project.name = name
            project.save()
            return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)


@csrf_exempt
def create_status_api(request, project_id):
    if request.method == 'POST':
        project = get_object_or_404(Project, pk=project_id)
        name = request.POST.get('name', 'New Status')
        color = request.POST.get('color', '#bfdbfe')
        status = TaskStatus.objects.create(project=project, name=name, color=color, order=project.custom_statuses.count() + 1)
        return JsonResponse({'success': True, 'id': status.id, 'name': status.name, 'color': status.color, 'text_color': status.text_color})
    return JsonResponse({'success': False}, status=400)


@csrf_exempt
def update_status_api(request, status_id):
    if request.method == 'POST':
        status = get_object_or_404(TaskStatus, pk=status_id)
        name = request.POST.get('name')
        color = request.POST.get('color')
        if name: status.name = name
        if color: status.color = color
        status.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)


@csrf_exempt
def delete_status_api(request, status_id):
    if request.method == 'POST':
        status = get_object_or_404(TaskStatus, pk=status_id)
        status.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)


@csrf_exempt
def reorder_tasks_api(request):
    if request.method == 'POST':
        import json
        try:
            order_data = json.loads(request.POST.get('order_data', '[]'))
            for item in order_data:
                task = get_object_or_404(Task, pk=item['id'])
                task.order = item['order']
                task.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False}, status=400)


@csrf_exempt
def update_section_sort_api(request, section_id):
    if request.method == 'POST':
        section = get_object_or_404(Section, pk=section_id)
        sort_by = request.POST.get('sort_by', 'custom')
        section.sort_by = sort_by
        section.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)


@csrf_exempt
def reorder_sections_api(request):
    if request.method == 'POST':
        import json
        try:
            order_data = json.loads(request.POST.get('order_data', '[]'))
            for item in order_data:
                section = get_object_or_404(Section, pk=item['id'])
                section.order = item['order']
                section.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    return JsonResponse({'success': False}, status=400)
