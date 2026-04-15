from .models import Profile, TypeDefinition, StatusDefinition, PriorityDefinition


def create_default_profile(sender, **kwargs):
    # Only run for the projects app
    app_label = getattr(sender, 'label', None) or sender.name.split('.')[-1]
    if app_label != 'projects':
        return
    
    # Check if any profiles exist
    if Profile.objects.exists():
        return
    
    # Create default profile
    default_profile = Profile.objects.create(name='Default', is_active=True)
    
    # Create default type definitions
    TypeDefinition.objects.create(profile=default_profile, name='corporate', color='#BA7517', order=0)
    TypeDefinition.objects.create(profile=default_profile, name='personal', color='#1D9E75', order=1)
    
    # Create default status definitions
    StatusDefinition.objects.create(profile=default_profile, name='ongoing', order=0)
    StatusDefinition.objects.create(profile=default_profile, name='ontrack', order=1)
    StatusDefinition.objects.create(profile=default_profile, name='atrisk', order=2)
    StatusDefinition.objects.create(profile=default_profile, name='overdue', order=3)
    
    # Create default priority definitions
    PriorityDefinition.objects.create(profile=default_profile, name='low', order=0)
    PriorityDefinition.objects.create(profile=default_profile, name='medium', order=1)
    PriorityDefinition.objects.create(profile=default_profile, name='high', order=2)
    PriorityDefinition.objects.create(profile=default_profile, name='urgent', order=3)
