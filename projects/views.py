from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import models
from .models import Project, Profile, TypeDefinition, StatusDefinition, PriorityDefinition


def project_list(request):
    sort_by = request.session.get('sort_by', 'custom')
    group_by = request.session.get('group_by', 'none')
    type_swap = request.session.get('type_swap', False)  # False = corporate first, True = personal first
    
    # Get active profile
    active_profile = Profile.objects.filter(is_active=True).first()
    
    if sort_by == 'status':
        projects = list(Project.objects.all().order_by('manual_status', 'order'))
    elif sort_by == 'priority':
        # Sort by priority (nulls last)
        projects = list(Project.objects.all().order_by('priority', 'order'))
    else:
        projects = list(Project.objects.all().order_by('order'))
    
    overdue_count = 0
    
    # Get status and priority options from active profile or fallback to defaults
    if active_profile:
        status_definitions = active_profile.status_definitions.all()
        priority_definitions = active_profile.priority_definitions.all()
        type_definitions = active_profile.type_definitions.all()
        
        status_options = [(s.name.lower(), s.name.title(), s.color) for s in status_definitions] + [(None, 'auto', '#999999')] if status_definitions.exists() else [(None, 'auto', '#999999')]
        priority_options = [(p.name.lower(), p.name.title(), p.color) for p in priority_definitions] if priority_definitions.exists() else []
        type_options = [(t.name.lower(), t.name.title(), t.color) for t in type_definitions] if type_definitions.exists() else [('corporate', 'Corporate', '#BA7517'), ('personal', 'Personal', '#1D9E75')]
    else:
        status_options = [('ongoing', 'Ongoing', '#1D9E75'), ('ontrack', 'On Track', '#10B981'), ('atrisk', 'At Risk', '#F59E0B'), ('overdue', 'Overdue', '#EF4444'), (None, 'auto', '#999999')]
        priority_options = [('low', 'Low', '#10B981'), ('medium', 'Medium', '#F59E0B'), ('high', 'High', '#F97316'), ('urgent', 'Urgent', '#EF4444')]
        type_options = [('corporate', 'Corporate', '#BA7517'), ('personal', 'Personal', '#1D9E75')]
    
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
        status_dict = dict(status_options)
        for value, label in status_options:
            group_projects = [p for p in projects if p.manual_status == value]
            if group_projects:
                grouped_projects.append({
                    'group_label': label,
                    'group_value': value,
                    'projects': group_projects
                })
    elif group_by == 'priority':
        # Group by priority
        priority_dict = dict(priority_options)
        for value, label in priority_options:
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
        'type_options': type_options,
        'sort_options': sort_options,
        'group_options': group_options,
        'current_sort': sort_by,
        'current_sort_label': sort_label,
        'current_group': group_by,
        'current_group_label': group_label,
        'type_swap': type_swap,
        'active_profile': active_profile,
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


def settings_view(request):
    profiles = Profile.objects.all()
    return render(request, 'projects/settings.html', {'profiles': profiles})


@csrf_exempt
def create_profile(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        
        # Generate default name if not provided
        if not name:
            profile_count = Profile.objects.count()
            name = f'Profile{profile_count + 1}'
        
        # Make the first profile automatically active
        is_first = Profile.objects.count() == 0
        profile = Profile.objects.create(name=name, is_active=is_first)
        return JsonResponse({'success': True, 'profile_id': profile.id})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def activate_profile(request, profile_id):
    if request.method == 'POST':
        profile = get_object_or_404(Profile, id=profile_id)
        profile.is_active = True
        profile.save()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def delete_profile(request, profile_id):
    if request.method == 'POST':
        profile = get_object_or_404(Profile, id=profile_id)
        was_active = profile.is_active
        profile.delete()
        
        # If we deleted the active profile, activate another one if available
        if was_active:
            remaining_profile = Profile.objects.first()
            if remaining_profile:
                remaining_profile.is_active = True
                remaining_profile.save()
        
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def create_type_definition(request):
    if request.method == 'POST':
        profile_id = request.POST.get('profile_id')
        name = request.POST.get('name', '').strip()
        color = request.POST.get('color', '#BA7517')
        
        if not profile_id or not name:
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        profile = get_object_or_404(Profile, id=profile_id)
        # Get the next order value
        max_order = profile.type_definitions.aggregate(models.Max('order'))['order__max'] or 0
        TypeDefinition.objects.create(profile=profile, name=name, color=color, order=max_order + 1)
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def create_status_definition(request):
    if request.method == 'POST':
        profile_id = request.POST.get('profile_id')
        name = request.POST.get('name', '').strip()
        color = request.POST.get('color', '#1D9E75')
        
        if not profile_id or not name:
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        profile = get_object_or_404(Profile, id=profile_id)
        # Get the next order value
        max_order = profile.status_definitions.aggregate(models.Max('order'))['order__max'] or 0
        StatusDefinition.objects.create(profile=profile, name=name, color=color, order=max_order + 1)
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def create_priority_definition(request):
    if request.method == 'POST':
        profile_id = request.POST.get('profile_id')
        name = request.POST.get('name', '').strip()
        color = request.POST.get('color', '#BA7517')
        
        if not profile_id or not name:
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        profile = get_object_or_404(Profile, id=profile_id)
        # Get the next order value
        max_order = profile.priority_definitions.aggregate(models.Max('order'))['order__max'] or 0
        PriorityDefinition.objects.create(profile=profile, name=name, color=color, order=max_order + 1)
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def reorder_type_definitions(request):
    if request.method == 'POST':
        order_data = request.POST.get('order', '')
        if not order_data:
            return JsonResponse({'error': 'No order data provided'}, status=400)
        
        try:
            import json
            order_list = json.loads(order_data)
            for index, def_id in enumerate(order_list):
                TypeDefinition.objects.filter(id=def_id).update(order=index)
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def reorder_status_definitions(request):
    if request.method == 'POST':
        order_data = request.POST.get('order', '')
        if not order_data:
            return JsonResponse({'error': 'No order data provided'}, status=400)
        
        try:
            import json
            order_list = json.loads(order_data)
            for index, def_id in enumerate(order_list):
                StatusDefinition.objects.filter(id=def_id).update(order=index)
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def reorder_priority_definitions(request):
    if request.method == 'POST':
        order_data = request.POST.get('order', '')
        if not order_data:
            return JsonResponse({'error': 'No order data provided'}, status=400)
        
        try:
            import json
            order_list = json.loads(order_data)
            for index, def_id in enumerate(order_list):
                PriorityDefinition.objects.filter(id=def_id).update(order=index)
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def delete_type_definition(request, def_id):
    if request.method == 'POST':
        type_def = get_object_or_404(TypeDefinition, id=def_id)
        type_def.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def delete_status_definition(request, def_id):
    if request.method == 'POST':
        status_def = get_object_or_404(StatusDefinition, id=def_id)
        status_def.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def delete_priority_definition(request, def_id):
    if request.method == 'POST':
        priority_def = get_object_or_404(PriorityDefinition, id=def_id)
        priority_def.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def project_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        project_type = request.POST.get('type', 'corporate')
        due_date = request.POST.get('due_date', '')
        next_action = request.POST.get('next_action', '').strip()
        
        if not name:
            return JsonResponse({'error': 'Name is required'}, status=400)
        
        # Get active profile and set first status and priority
        active_profile = Profile.objects.filter(is_active=True).first()
        first_status = None
        first_priority = None
        
        if active_profile:
            first_status = active_profile.status_definitions.first()
            first_priority = active_profile.priority_definitions.first()
        
        project = Project.objects.create(
            name=name,
            project_type=project_type,
            due_date=due_date if due_date else None,
            next_action=next_action,
            manual_status=first_status.name.lower() if first_status else None,
            priority=first_priority.name.lower() if first_priority else None
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
        priority = request.POST.get('priority', '')
        project.priority = priority if priority else None
        project.save()
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
