from django.db import models
from django.contrib.auth.models import User
from smart_selects.db_fields import ChainedForeignKey
from django.core.exceptions import ValidationError


# Create your models here.

class Master(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    isactive = models.BooleanField(default=True, verbose_name='active')
    created_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)

    class Meta:
        abstract = True
        ordering = ['isactive']


class State(Master):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "States"


class District(Master):
    name = models.ForeignKey(State, on_delete=models.CASCADE, limit_choices_to={"isactive": True}, null=True)
    Dist_Name = models.CharField(max_length=255)

    def __str__(self):
        return self.Dist_Name

    class Meta:
        verbose_name_plural = "Districts"


class Branch_Name(Master):
    branch = models.CharField(max_length=200)
    branch_code = models.CharField(max_length=50, unique=True, null=True)
    address = models.CharField(max_length=500, blank=True)
    street = models.CharField(max_length=200, blank=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE, limit_choices_to={"isactive": True})
    district = ChainedForeignKey(District, chained_field="state", chained_model_field="name", show_all=False,
                                 auto_choose=True, sort=True, limit_choices_to={"isactive": True})
    pincode = models.PositiveIntegerField(blank=True, null=True)
    email = models.EmailField(max_length=200, blank=True)

    def __str__(self):
        return self.branch_code

    class Meta:
        verbose_name_plural = "Branches"
        ordering = ("state", "district")


class ComputerBrand(Master):
    Name = models.CharField(max_length=50)

    def __str__(self):
        return self.Name

    class Meta:
        verbose_name_plural = "Computer Brands"


class Course(Master):
    course = models.CharField(max_length=50)

    def __str__(self):
        return self.course

    class Meta:
        verbose_name_plural = "Courses"


class Batch(Master):
    branch = models.ForeignKey(Branch_Name, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    start_date = models.DateField()
    start_time = models.TimeField()
    end_date = models.DateField()
    end_time = models.TimeField()
    Trainer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Trainer", null=True, blank=False,
                                related_name="trainer", limit_choices_to={"is_active": True, "groups__name": 'Trainer'})
    is_closed = models.BooleanField(default=False, verbose_name="Closed")
    batch = models.CharField(max_length=255, blank=True)

    def save(self, *args, **kwargs):
        self.batch = f"{self.start_date.strftime('%Y')}{self.course}{self.start_date.strftime('%dth %B')}{self.start_time.strftime('%I:%M %p')}{self.end_time.strftime('%I:%M %p')}{self.branch}{self.Trainer}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.batch

    class Meta:
        verbose_name_plural = "Batches"


CTYPE_CHOICES = [
    ('rental', 'Rental'),
    ('own', 'Own'),
]
CATEGORY_CHOICES = [
    ('laptop', 'Laptop'),
    ('desktop', 'Desktop'),
]


class System(Master):
    branch = models.ForeignKey(Branch_Name, on_delete=models.CASCADE, null=True)
    Category = models.CharField(max_length=300, choices=CATEGORY_CHOICES)
    Code = models.CharField(max_length=50, editable=False, unique=True)
    RentalorOwn = models.CharField(max_length=300, choices=CTYPE_CHOICES)
    Brand = models.ForeignKey(ComputerBrand, on_delete=models.CASCADE)
    SerialNo = models.CharField(max_length=50, blank=True, null=True)
    ResponsibleTrainer = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Trainer", null=True,
                                           blank=False, limit_choices_to={"is_active": True},
                                           related_name='ResponsibleTrainer')
    DateofPurchase = models.DateField(blank=True, null=True)
    DateofReturn = models.DateField(blank=True, null=True)
    ActualDateofReturn = models.DateField(blank=True, null=True)
    Amount = models.FloatField(blank=True, null=True)

    def save(self, *args, **kwargs):
        # Call save method from superclass to save the object and get self.pk
        super().save(*args, **kwargs)

        # Check if Code is empty
        if not self.Code:
            # Generate code based on Category
            prefix = 'OTSL' if self.Category == 'laptop' else 'OTSD'
            self.Code = '{}{:02d}'.format(prefix, self.pk)

            # Call save method from superclass again to save the updated Code
            super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.Brand} | {self.Code}'

    class Meta:
        verbose_name_plural = "Systems"


FLOOR_CHOICES = [
    ('G', 'Ground'),
    ('I', 'First'),
    ('II', 'Second'),
]

TYPE_CHOICES = [
    ('class', 'Class Room'),
    ('conference', 'Confrence Hall'),
]


class Room(Master):
    Branch = models.ForeignKey(Branch_Name, on_delete=models.CASCADE, null=True)
    Name = models.CharField(max_length=50)
    Floor = models.CharField(max_length=300, choices=FLOOR_CHOICES)
    Type = models.CharField(max_length=300, choices=TYPE_CHOICES)
    NoofSeats = models.IntegerField()

    def __str__(self):
        return self.Name

    class Meta:
        verbose_name_plural = "Rooms"


RType_CHOICES = [
    ('class', 'Class'),
    ('meeting', 'Meeting')
]


class RoomAllocation(Master):
    Branch = models.ForeignKey(Branch_Name, on_delete=models.CASCADE, null=True)
    Reservation_Type = models.CharField(max_length=300, choices=RType_CHOICES)
    Batch = ChainedForeignKey(
        Batch,
        chained_field="Branch",
        chained_model_field="branch",  # Field in Batch model that relates to Branch model
        show_all=False,
        auto_choose=True,
        sort=True,
        null=True,
        blank=False,
        limit_choices_to={"isactive": True},
    )
    # Student = ChainedForeignKey(Student,chained_field="Batch",chained_model_field="Batch",show_all=False,auto_choose=True,sort=True,limit_choices_to={"isactive": True})
    # Person = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Trainer", null=True, blank=False,related_name="Person", limit_choices_to={"is_active": True, "groups__name":'Trainer'})
    From = models.DateField()
    starttime = models.TimeField(null=True)
    To = models.DateField()
    endtime = models.TimeField(null=True)

    Room = ChainedForeignKey(
        Room,
        chained_field="Branch",
        chained_model_field="Branch",  # Field in Room model that relates to Branch model
        show_all=False,
        auto_choose=True,
        sort=True,
        null=True,
        blank=False,
        limit_choices_to={"isactive": True},
    )

    Purpose = models.CharField(max_length=50)

    def __str__(self):
        return self.Reservation_Type

    def clean(self):
        # Check if the room is already reserved for the selected date range
        Available_Rooms = RoomAllocation.objects.filter(Room=self.Room)
        for reservation in Available_Rooms:
            if (
                    self.From <= reservation.To and self.starttime <= reservation.endtime and self.To >= reservation.From and self.endtime >= reservation.starttime):
                raise ValidationError("Room is already reserved for the selected dates.")

    class Meta:
        verbose_name_plural = "RoomAllocation"