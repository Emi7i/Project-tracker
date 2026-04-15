from .models import Profile


def create_default_profile(sender, **kwargs):
    # Only run for the projects app
    app_label = getattr(sender, 'label', None) or sender.name.split('.')[-1]
    if app_label != 'projects':
        return
    
    # Check if any profiles exist
    if Profile.objects.exists():
        return
    
    # Create default profile (empty - user will add their own definitions)
    Profile.objects.create(name='Default', is_active=True)
