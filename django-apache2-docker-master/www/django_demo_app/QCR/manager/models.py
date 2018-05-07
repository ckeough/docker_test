from __future__ import unicode_literals
from django.contrib.auth.models import User

from django.db import models

# Create your models here.


class ProjectSpecification(models.Model):
    name = models.FloatField(null=False)

    def __str__(self):
        return str(self.name)


class WorkPackage(models.Model):
    workPackageId = models.IntegerField(primary_key=True);
    name = models.CharField(max_length=200, null=True);
    description = models.TextField(null=True);
    type = models.CharField(max_length=200, null=True);
    vendor = models.CharField(max_length=200, null=True);
    poc = models.CharField(max_length=200, null=True);
    # pocPhone = models.IntegerField(null = true)
    pocEmail = models.CharField(max_length=200, null=True);
    projectSpec = models.ForeignKey(ProjectSpecification, on_delete=models.CASCADE, null=True);
    restrictions = models.NullBooleanField(null=True);
    restrictionsDate = models.DateField(null=True);
    restrictionsLayer = models.NullBooleanField(null=True);
    thirdPartyQa = models.NullBooleanField(null=True);
    thirdPartyQaBy = models.CharField(max_length=200, null=True);
    receivedDate = models.DateField(null=True);
    assignedDate = models.DateField(null=True);

    def __str__(self):
        return "Work Package ID " + str(self.workPackageId) + ", " + str(self.name)


class PointCloudClassification(models.Model):
    classificationId = models.IntegerField(null=True)
    classificationType = models.CharField(max_length=200, null=True)
    workPackage = models.ForeignKey(WorkPackage, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return "Point Cloud Classification: " + str(self.classificationId) + ", Type: " + str(self.classificationType)


class Review(models.Model):
    name = models.CharField(max_length=75, null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    project_date_received = models.DateTimeField(null=True)
    project_date_assigned = models.DateTimeField(null=True)
    project_completion_date = models.DateTimeField(null=True)
    accepted = models.BooleanField(default=False)
    absVaAccept = models.BooleanField(default=False)
    relVaAccept = models.NullBooleanField(default=False)
    metadataAccept = models.NullBooleanField(default=False)
    breaklinesAccept = models.NullBooleanField(default=False)
    reportsAccept = models.NullBooleanField(default=False)
    otherAccept = models.NullBooleanField(default=False)
    demAccept = models.NullBooleanField(default=False)
    swathAccept = models.NullBooleanField(default=False)
    classifiedAccept = models.NullBooleanField(default=False)

    def __str__(self):
        return str(self.id)


class ReviewProgressChecklist(models.Model):
    master = models.BooleanField(default=False)
    review = models.OneToOneField(Review, null=True, on_delete=models.CASCADE)


class ChecklistCategory(models.Model):
    name = models.CharField(max_length=25)


class ChecklistItem(models.Model):
    checklist = models.ForeignKey(ReviewProgressChecklist, on_delete=models.CASCADE)
    category = models.ForeignKey(ChecklistCategory, on_delete=models.CASCADE)
    placement = models.IntegerField(null=False)
    name = models.CharField(max_length=300, null=False)
    complete = models.BooleanField(default=False)


class QualityLevel(models.Model):
    name = models.CharField(max_length=200, null=False)

    def __str__(self):
        return str(self.name)


class SensorUsed(models.Model):
    name = models.CharField(max_length=200, null=False)

    def __str__(self):
        return str(self.name)


class SensorType(models.Model):
    name = models.CharField(max_length=200, null=False)

    def __str__(self):
        return str(self.name)
