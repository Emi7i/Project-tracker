from django.db import models
from django.utils import timezone


class Profile(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Ensure only one profile is active
        if self.is_active:
            Profile.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)


class TypeDefinition(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='type_definitions')
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default='#BA7517')
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order']


class StatusDefinition(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='status_definitions')
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default='#1D9E75')
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order']


class PriorityDefinition(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='priority_definitions')
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default='#BA7517')
    order = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order']


class Project(models.Model):
    name = models.CharField(max_length=200)
    project_type = models.CharField(max_length=20, default='corporate')
    due_date = models.DateField(null=True, blank=True)
    next_action = models.CharField(max_length=500, blank=True)
    order = models.IntegerField(default=0)
    manual_status = models.CharField(max_length=20, null=True, blank=True)
    priority = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def status(self):
        if self.manual_status:
            return self.manual_status
        return None

    @property
    def status_label(self):
        if not self.status:
            return ''
        active_profile = Profile.objects.filter(is_active=True).first()
        if active_profile:
            status_def = active_profile.status_definitions.filter(name__iexact=self.status).first()
            if status_def:
                return status_def.name.title()
        return self.status.title()

    @property
    def status_color(self):
        if not self.status:
            return '#999999'
        active_profile = Profile.objects.filter(is_active=True).first()
        if active_profile:
            status_def = active_profile.status_definitions.filter(name__iexact=self.status).first()
            if status_def:
                return status_def.color
        return '#999999'

    @property
    def days_label(self):
        if not self.due_date:
            return ''
        
        today = timezone.now().date()
        diff = (self.due_date - today).days
        
        if diff < 0:
            return f'{abs(diff)}d overdue'
        elif diff == 0:
            return 'due today'
        elif diff == 1:
            return 'due tomorrow'
        else:
            return f'due in {diff}d'

    @property
    def formatted_date(self):
        if not self.due_date:
            return ''
        return self.due_date.strftime('%d %b %Y')

    @property
    def dot_color(self):
        active_profile = Profile.objects.filter(is_active=True).first()
        if active_profile and self.project_type:
            type_def = active_profile.type_definitions.filter(name__iexact=self.project_type).first()
            if type_def:
                return type_def.color
        return '#BA7517' if self.project_type == 'corporate' else '#1D9E75'

    @property
    def get_priority_display(self):
        if not self.priority:
            return ''
        active_profile = Profile.objects.filter(is_active=True).first()
        if active_profile:
            priority_def = active_profile.priority_definitions.filter(name__iexact=self.priority).first()
            if priority_def:
                return priority_def.name.title()
        return self.priority.title()

    @property
    def priority_color(self):
        if not self.priority:
            return '#999999'
        active_profile = Profile.objects.filter(is_active=True).first()
        if active_profile:
            priority_def = active_profile.priority_definitions.filter(name__iexact=self.priority).first()
            if priority_def:
                return priority_def.color
        return '#999999'
