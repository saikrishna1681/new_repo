from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

circulation_action = (("RETURN", "RETURN"),("CHECK OUT", "CHECK OUT"),("FULFILL", "FULFILL"),("RESERVE", "RESERVE"))
reservation_action = (("FULFILL", "FULFILL"),("RESERVE", "RESERVE"))


class Member(AbstractUser):
    pass


class Book(models.Model):

    name = models.CharField(max_length = 100)
    no_of_copies = models.IntegerField(default = 0)
    copies_left = models.IntegerField(default = 0)

    def __str__(self):

        return f'{self.name}__{self.id}'
    

class Circulation(models.Model):

    member = models.ForeignKey("Member", on_delete = models.CASCADE)
    book = models.ForeignKey("Book", on_delete = models.CASCADE)
    date = models.DateField(auto_now_add = True)
    eventtype = models.CharField(max_length = 15, choices = circulation_action)


class Reservation(models.Model):

    member = models.ForeignKey("Member", on_delete = models.CASCADE)
    book = models.ForeignKey("Book", on_delete = models.CASCADE)
    date = models.DateField(auto_now_add = True)
    eventtype = models.CharField(max_length = 15, choices = reservation_action)


