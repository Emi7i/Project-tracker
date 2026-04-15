from django.db import models
from django.utils import timezone


class Project(models.Model):
    PROJECT_TYPES = [
        ('corporate', 'Corporate'),
        ('personal', 'Personal'),
    ]
    
    STATUS_CHOICES = [
        ('ongoing', 'Ongoing'),
        ('ontrack', 'On Track'),
        ('atrisk', 'At Risk'),
        ('overdue', 'Overdue'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    name = models.CharField(max_length=200)
    project_type = models.CharField(max_length=20, choices=PROJECT_TYPES, default='corporate')
    due_date = models.DateField(null=True, blank=True)
    next_action = models.CharField(max_length=500, blank=True)
    order = models.IntegerField(default=0)
    manual_status = models.CharField(max_length=20, choices=STATUS_CHOICES, null=True, blank=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def status(self):
        if self.manual_status:
            return self.manual_status
            
        if not self.due_date:
            return 'ongoing'
        
        today = timezone.now().date()
        diff = (self.due_date - today).days
        
        if diff < 0:
            return 'overdue'
        elif diff <= 7:
            return 'atrisk'
        else:
            return 'ontrack'

    @property
    def status_label(self):
        labels = dict(Project.STATUS_CHOICES)
        return labels.get(self.status, '')

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
        return '#BA7517' if self.project_type == 'corporate' else '#1D9E75'
