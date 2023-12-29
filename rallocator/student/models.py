from django.db import models
from django.core.validators import RegexValidator
from smart_selects.db_fields import ChainedForeignKey
from rallocatorapp.models import Batch, Master,System
# Create your models here.

# LAPTOP_CHOICES = [
#         ('YES', 'YES'),
#         ('NO', 'NO'),
#     ]


class Student(Master) :
    Batch = models.ForeignKey(Batch,on_delete=models.CASCADE)
    Name = models.CharField(max_length=50)
    phone_regex=RegexValidator(regex=r'^\+?1?\d{9,10}$',message="phone number must be in the formate of xxxxxxxxxx , upto 10 digits allowed")
    Mobile = models.CharField(max_length=50)
    Email = models.CharField(max_length=50)
    Have_Own_System = models.BooleanField(default=False,blank=False)

    def __str__(self) :
        return self.Name
    class Meta:
        verbose_name_plural = "Students"

class SystemAllocation(models.Model) :
    Batch = models.ForeignKey(Batch,on_delete=models.CASCADE,null=True)
    # students = ChainedForeignKey(Student,chained_field='Batch',chained_model_field='Batch',show_all=False,auto_choose=True,null=True,sort=True,limit_choices_to={'Have_Own_System' : False})
    # students = models.ForeignKey(Student, on_delete=models.CASCADE,null=True,limit_choices_to={'Have_Own_System' : False})

    students = ChainedForeignKey(
        Student,
        chained_field='Batch',
        chained_model_field='Batch',
        show_all=False,
        auto_choose=True,
        null=True,
        sort=True,
        blank=False,
        limit_choices_to={'Have_Own_System': False, 'systemallocation__isnull': True}
    )
    start_date = models.DateField(null=True)
    From = models.TimeField(null=True)
    end_date = models.DateField(null=True)
    To = models.TimeField(null=True)
    # system = models.ForeignKey(System, on_delete=models.CASCADE,null=True)

    system = models.ForeignKey(
        System,
        on_delete=models.CASCADE,
        null=True,
        limit_choices_to={'systemallocation__isnull': True}
    )
    
    def clean(self):
        # Check if the system is already allocated during the specified time range
        if self.system and self.From and self.To :
            conflicting_allocations = SystemAllocation.objects.filter(
                system=self.system,
                From__lt=self.To,
                To__gt=self.From,
            ).exclude(pk=self.pk)

            if conflicting_allocations.exists():
                raise ValidationError({'From' : 'This system is already allocated during the specified time range.'})

            super().clean()