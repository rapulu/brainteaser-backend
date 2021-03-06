# Generated by Django 3.0.7 on 2020-07-15 07:27

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import game.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('name', models.CharField(max_length=100, primary_key=True, serialize=False, unique=True)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('doc', models.FileField(upload_to='some/place/')),
            ],
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('game_code', models.IntegerField(default=game.models.add_one, primary_key=True, serialize=False)),
                ('user_name', models.CharField(max_length=100)),
                ('active', models.BooleanField(default=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.Category')),
            ],
        ),
        migrations.CreateModel(
            name='Options',
            fields=[
                ('option', models.CharField(max_length=100000, primary_key=True, serialize=False, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserGames',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('user_name', models.CharField(max_length=100)),
                ('score', models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(1)])),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.Category')),
                ('game_code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.Game')),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('question', models.CharField(max_length=100000)),
                ('answer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='correct', to='game.Options')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='game.Category')),
                ('options', models.ManyToManyField(to='game.Options')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
