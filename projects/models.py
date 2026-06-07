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
    next_task = models.ForeignKey('Task', on_delete=models.SET_NULL, null=True, blank=True, related_name='next_for_project')
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


class Section(models.Model):
    name = models.CharField(max_length=200)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='sections')
    order = models.IntegerField(default=0)
    sort_by = models.CharField(max_length=20, default='custom') # 'custom', 'deadline', 'status'

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name


class TaskStatus(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='custom_statuses')
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=7, default='#bfdbfe')
    text_color = models.CharField(max_length=7, default='#111827')
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def save(self, *args, **kwargs):
        # Calculate contrast color before saving
        self.text_color = self.calculate_contrast(self.color)
        super().save(*args, **kwargs)

    def calculate_contrast(self, hex_color):
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 3:
            hex_color = ''.join([c*2 for s in hex_color for c in s])
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        return '#111827' if brightness > 150 else '#ffffff'

    def __str__(self):
        return f"{self.project.name} - {self.name}"


class Task(models.Model):
    name = models.CharField(max_length=500)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='tasks')
    status_obj = models.ForeignKey(TaskStatus, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    due_date = models.DateField(null=True, blank=True)
    time_tracked = models.FloatField(default=0)
    waiting_on = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='blocked_tasks')
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name
