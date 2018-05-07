# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2018-04-04 17:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('report', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='checklistitem',
            name='category',
        ),
        migrations.RemoveField(
            model_name='checklistitem',
            name='checklist',
        ),
        migrations.RemoveField(
            model_name='pointcloudclassification',
            name='workPackage',
        ),
        migrations.RemoveField(
            model_name='review',
            name='user',
        ),
        migrations.RemoveField(
            model_name='reviewprogresschecklist',
            name='review',
        ),
        migrations.RemoveField(
            model_name='workpackage',
            name='projectSpec',
        ),
        migrations.AlterField(
            model_name='collectioninfo',
            name='qualityLevel',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='manager.QualityLevel'),
        ),
        migrations.AlterField(
            model_name='collectioninfo',
            name='sensorType',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='manager.SensorType'),
        ),
        migrations.AlterField(
            model_name='collectioninfo',
            name='sensorUsed',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='manager.SensorUsed'),
        ),
        migrations.AlterField(
            model_name='workunit',
            name='qualityLevel',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='manager.QualityLevel'),
        ),
        migrations.AlterField(
            model_name='workunit',
            name='review',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='manager.Review'),
        ),
        migrations.AlterField(
            model_name='workunit',
            name='workPackage',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='manager.WorkPackage'),
        ),
        migrations.DeleteModel(
            name='ChecklistCategory',
        ),
        migrations.DeleteModel(
            name='ChecklistItem',
        ),
        migrations.DeleteModel(
            name='PointCloudClassification',
        ),
        migrations.DeleteModel(
            name='ProjectSpecification',
        ),
        migrations.DeleteModel(
            name='QualityLevel',
        ),
        migrations.DeleteModel(
            name='Review',
        ),
        migrations.DeleteModel(
            name='ReviewProgressChecklist',
        ),
        migrations.DeleteModel(
            name='SensorType',
        ),
        migrations.DeleteModel(
            name='SensorUsed',
        ),
        migrations.DeleteModel(
            name='WorkPackage',
        ),
    ]