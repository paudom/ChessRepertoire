# Generated by Django 3.2.6 on 2022-05-26 16:58

import autoslug.fields
import chess_repertoire.apps.repertoire.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Opening',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('slug', autoslug.fields.AutoSlugField(editable=False, populate_from='name')),
                ('description', models.TextField(default='', max_length=400)),
                ('color', models.IntegerField(choices=[(0, 'WHITE'), (1, 'BLACK')])),
                ('difficulty', models.CharField(choices=[('B', 'BEGINNER'), ('I', 'INTERMEDIATE'), ('A', 'ADVANCED'), ('E', 'EXPERT')], max_length=50)),
                ('category', models.CharField(choices=[('CL', 'CLASSIC'), ('SY', 'SYSTEM'), ('GB', 'GAMBIT')], max_length=50)),
                ('image', models.ImageField(max_length=500, upload_to=chess_repertoire.apps.repertoire.models.opening_upload_attribute)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Variation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('slug', autoslug.fields.AutoSlugField(editable=False, populate_from='name')),
                ('description', models.TextField(default='', max_length=200)),
                ('on_turn', models.PositiveIntegerField()),
                ('nature', models.CharField(choices=[('THC', 'THEORIC'), ('PST', 'POSITIONAL'), ('TRC', 'TRICKY'), ('SHP', 'SHARP'), ('ADV', 'ADVANTAGEOUS'), ('UNF', 'UNFAVORABLE')], max_length=50)),
                ('pgn_file', models.FileField(upload_to=chess_repertoire.apps.repertoire.models.variation_upload_attribute)),
                ('image_file', models.ImageField(max_length=500, upload_to=chess_repertoire.apps.repertoire.models.variation_upload_attribute)),
                ('opening', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='repertoire.opening')),
            ],
            options={
                'ordering': ['on_turn', 'name'],
                'unique_together': {('name', 'on_turn')},
            },
        ),
    ]
