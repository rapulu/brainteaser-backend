import uuid

from django.core.validators import MinValueValidator
from django.db import models


# Create your models here.
def add_one():
    largest = Game.objects.all().order_by('game_code').last()
    if not largest:
        return 1000
    return largest.game_code + 1


class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, null=False)
    email_address = models.CharField(unique=True, max_length=50, null=True)
    password = models.CharField(max_length=1000, null=True)
    score = models.PositiveIntegerField(
        null=False, validators=[MinValueValidator(1)], default=0
    )


class Category(models.Model):
    name = models.CharField(primary_key=True,max_length=100, unique=True, null=False)


class Options(models.Model):
    option = models.CharField(primary_key=True,max_length=100000, unique=True, null=False)


class Question(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    question = models.CharField(max_length=100000, unique=False, null=False)
    options = models.ManyToManyField("Options")
    answer = models.ForeignKey(Options,related_name="correct", on_delete=models.CASCADE)


class Game(models.Model):
    game_code = models.IntegerField(primary_key=True,
                                    default=add_one)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)


class UserGames(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    game_code = models.ForeignKey(Game,
                                  on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.PositiveIntegerField(
        null=False, validators=[MinValueValidator(1)], default=0
    )
