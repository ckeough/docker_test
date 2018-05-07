from __future__ import unicode_literals
from django.dispatch import receiver
from django.db.models.signals import post_delete
from django.db import models
from django.contrib.auth.models import User
from manager.models import QualityLevel
from manager.models import SensorType
from manager.models import SensorUsed
from manager.models import WorkPackage
from manager.models import Review



####   High-level classes   ####

## VA Requirement Classes
class VaRequirement(models.Model):
	comment = models.CharField(max_length = 200, null = True)

class VaRequirement10(VaRequirement):
	fundamentalVaChkpt = models.IntegerField(null = True)
	fundamentalVaValue = models.FloatField(null = True)
	consolidatedVaChkpt = models.IntegerField(null = True)
	consolidatedVaValue = models.FloatField(null = True)
	def __str__(self):
		return "LBS 1.0 VA Requirement ID: " + str(self.id)		
		
class VaRequirement12(VaRequirement):
	vegetatedVaChkpt = models.IntegerField(null = True)
	vegetatedVaValue = models.FloatField(null = True)
	nonvegetatedVaChkpt = models.IntegerField(null = True)
	nonvegetatedVaValue = models.FloatField(null = True)
	def __str__(self):
		return "LBS 1.2 VA Requirement ID: " + str(self.id)

class SuppVaMeasure(models.Model):
	landcover = models.CharField(max_length=200, null = True)
	reqChkpts = models.IntegerField(null = True)
	reqVal = models.FloatField(null = True)
	vaRequirement = models.ForeignKey(VaRequirement10, on_delete=models.CASCADE)
	## Dont think this field is used any more - double check
	vaReqSvaId = models.IntegerField()
	def __str__(self):
		return "VA Requirement measure type: SVA, ID: " + str(self.id)		
			
#### Collection Info (per work unit) class		
class CollectionInfo(models.Model):
	areaExtent = models.FloatField(null = True)
	## Not sure we should allow this field to be null...otherwise no way to associate VA Reqs
	qualityLevel = models.ForeignKey(QualityLevel, null = True, on_delete = models.CASCADE)
	collectionStart = models.DateTimeField(null = True)
	collectionEnd = models.DateTimeField(null = True)
	tileSize = models.CharField(max_length = 30, null = True)
	tileSizeUnits = models.CharField(max_length = 30, null = True)
	demResolution = models.FloatField(null = True)
	demResolutionUnits = models.CharField(max_length = 30, null = True)
	horizontalSpatRef = models.CharField(max_length = 100, null = True)
	horizontalEpsg = models.IntegerField(null = True)
	verticalSpatRef = models.CharField(max_length = 100, null = True)
	verticalEpsg = models.IntegerField(null = True)
	lasVersion = models.FloatField(null = True)
	configuredNps = models.FloatField(null = True) 
	configNpsUnits = models.CharField(max_length = 30, null = True)
	configuredAnps = models.FloatField(null = True) 
	configAnpsUnits = models.CharField(max_length = 30, null = True)
	configAnpsMethod = models.CharField(max_length = 200, null = True)
	hydroTreatment = models.CharField(max_length = 30, null = True)
	sensorType = models.ForeignKey(SensorType, null = True, on_delete = models.CASCADE)
	sensorUsed = models.ForeignKey(SensorUsed, null = True, on_delete = models.CASCADE)
	configScanAngle = models.FloatField(null = True) 
	def __str__(self):
		return str(self.id)

class AggregatedWuDeliverableCategory(models.Model):
	DEM = "DEM"
	SWATH = "Swath"
	CLASSIFIED = "Classified"
	CATEGORY_CHOICES = (
		(1, DEM),
		(2, SWATH),
		(3, CLASSIFIED),
	)
	name = models.CharField(max_length=200)
	category = models.IntegerField(choices = CATEGORY_CHOICES)
	def __str__(self):
		return str(self.category)

class VaData(models.Model):
	vaRequirement = models.ForeignKey(VaRequirement, on_delete = models.CASCADE, null=True)
	category = models.ForeignKey(AggregatedWuDeliverableCategory, on_delete = models.CASCADE, null=True)
	comment = models.CharField(max_length = 200, null = True)
	
class VaData10(VaData):
	reportedCvaValue = models.FloatField(null = True)
	reportedCvaChkpts = models.IntegerField(null = True)
	testedCvaValue = models.FloatField(null = True)
	testedCvaChkpts = models.IntegerField(null = True)
	reportedFvaValue = models.FloatField(null = True)
	reportedFvaChkpts = models.IntegerField(null = True)
	testedFvaValue = models.FloatField(null = True)
	testedFvaChkpts = models.IntegerField(null = True)
	def __str__(self):
		return "LBS 1.0 VA Data ID: " + str(self.id)	
		
class VaData12(VaData):
	reportedNvaValue = models.FloatField(null = True)
	reportedNvaChkpts = models.IntegerField(null = True)
	testedNvaValue = models.FloatField(null = True)
	testedNvaChkpts = models.IntegerField(null = True)
	reportedVvaValue = models.FloatField(null = True)
	reportedVvaChkpts = models.IntegerField(null = True)
	testedVvaValue = models.FloatField(null = True)
	testedVvaChkpts = models.IntegerField(null = True)
	def __str__(self):
		return "LBS 1.2 VA Data ID: " + str(self.id)		
		
class SuppVaResults(models.Model):
	vaData = models.ForeignKey(VaData, on_delete=models.CASCADE, null = True)
	sva = models.ForeignKey(SuppVaMeasure, on_delete= models.CASCADE, null = True)
	testedChkpts = models.IntegerField(null = True)
	reportedChkpts = models.IntegerField(null = True)
	testedValue = models.FloatField(null = True)
	reportedValue = models.FloatField(null = True)
	def __str__(self):
		return "SVA Results, ID: " + str(self.id)

class AggregatedWuDeliverable(models.Model):
	description = models.CharField(max_length=200, null=True)
	category = models.ForeignKey(AggregatedWuDeliverableCategory, on_delete = models.CASCADE)
	vaData = models.ForeignKey(VaData, on_delete = models.SET_NULL, null = True)
	quantity = models.IntegerField(null = True)
	spatialReference = models.CharField(max_length = 100, null = True)
	reqPerContract = models.NullBooleanField(null = True)
	reqPerSpec = models.NullBooleanField(null = True)
	delivered = models.NullBooleanField(null = True)
	accepted = models.NullBooleanField(null = True)	
	comment = models.CharField(max_length=200, null=True)
	def __str__(self):
		return str(self.id)

class AggregatedWuDeliverableTab(models.Model):
	deliverable = models.ForeignKey(AggregatedWuDeliverable, on_delete = models.CASCADE)
	vaRequirement = models.ForeignKey(VaRequirement, on_delete = models.SET_NULL, null = True)
		
class DEM(AggregatedWuDeliverable):
	resolution = models.CharField(max_length=200, null=True)
	resolutionUnits =  models.CharField(max_length=200, null=True)
	pixelType = models.CharField(max_length=200, null=True)
	interpolation = models.CharField(max_length=200, null=True)
	def __str__(self):
		return "DEM ID " + str(self.id)

class DemTab(models.Model):
	dem = models.ForeignKey(DEM, on_delete = models.CASCADE)
	vaRequirement = models.ForeignKey(VaRequirement, on_delete = models.SET_NULL, null = True)

class Swath(AggregatedWuDeliverable):
	swathPCVs = models.FloatField(null=True)
	pointRecDataFormat = models.CharField(max_length=200, null=True)
	requiredInterswath = models.FloatField(null = True)
	recordedInterswath = models.FloatField(null = True)
	testedInterswath = models.FloatField(null = True)
	def __str__(self):
		return "Swath ID " + str(self.id)

class SwathTab(models.Model):
	swath = models.ForeignKey(Swath, on_delete = models.CASCADE)
	vaRequirement = models.ForeignKey(VaRequirement, on_delete = models.SET_NULL, null = True)

class Classified(AggregatedWuDeliverable):
	classPCVs = models.FloatField(null=True)
	pointRecDataFormat = models.CharField(max_length=200, null=True)
	def __str__(self):
		return "Classified ID " + str(self.id)

class ClassifiedTab(models.Model):
	classified = models.ForeignKey(Classified, on_delete = models.CASCADE)
	vaRequirement = models.ForeignKey(VaRequirement, on_delete = models.SET_NULL, null = True)

class WorkUnit(models.Model):
	workUnitId = models.IntegerField(primary_key=True);
	workPackage = models.ForeignKey(WorkPackage, on_delete=models.CASCADE, null = True)
	qualityLevel = models.ForeignKey(QualityLevel, null = True, on_delete = models.SET_NULL)
	collectionInfo = models.ForeignKey(CollectionInfo, on_delete=models.SET_NULL, null = True)
	aggregatedWuDeliverable = models.ManyToManyField(AggregatedWuDeliverable)
	vaRequirement = models.ForeignKey(VaRequirement, on_delete=models.SET_NULL, null = True)
	name = models.CharField(max_length=200,null=True);
	status = models.CharField(max_length=200,null=True);
	review = models.ForeignKey(Review, on_delete=models.SET_NULL, null=True)
	def __str__(self):
		return str(self.workUnitId)

class DeliverableCategory(models.Model):
	META = "Metadata"
	BRKLN = "Breaklines"
	DSM = "Digital Surface Model"
	REPORTS = "Reports and Shapefiles"
	OTHER = "Other"
	CATEGORY_CHOICES = (
		(1, META),
		(2, BRKLN),
		(3, DSM),
		(6, REPORTS),
		(7, OTHER)
	)
	category = models.IntegerField(choices = CATEGORY_CHOICES)
	name = models.CharField(max_length=200)
	def __str__(self):
		return str(self.name)	
	
class Deliverable(models.Model):
	workUnit = models.ManyToManyField(WorkUnit)
	description = models.CharField(max_length=200, null=True)
	deliverableCategory = models.ForeignKey(DeliverableCategory, on_delete=models.CASCADE, null = True)
	quantity = models.IntegerField(null = True)
	spatialReference = models.CharField(max_length = 100, null = True)
	reqPerContract = models.NullBooleanField(null = True)
	reqPerSpec = models.NullBooleanField(null = True)
	delivered = models.NullBooleanField(null = True)
	comment = models.CharField(max_length=200, null=True)
	accepted = models.NullBooleanField(null = True)	
	def __str__(self):
		return str(self.description)
		
class ErrorType(models.Model):
	name = models.CharField(max_length = 200)
	deliverableCategory = models.ForeignKey(DeliverableCategory, on_delete=models.CASCADE, null=True)
	aggDeliverableCategory = models.ForeignKey(AggregatedWuDeliverableCategory, on_delete=models.CASCADE, null=True)
	def __str__(self):
		return str(self.name)

class ErrorSubtype(models.Model):
	name = models.CharField(max_length= 200)
	errorType = models.ForeignKey(ErrorType, on_delete=models.CASCADE)
	def __str__(self):
		return str(self.name)

class Error(models.Model):
	deliverable = models.ForeignKey(Deliverable, on_delete=models.CASCADE, null=True)
	aggregatedWuDeliverable = models.ForeignKey(AggregatedWuDeliverable, on_delete = models.CASCADE, null = True)
	errorType = models.ForeignKey(ErrorType, on_delete=models.SET_NULL, null = True)
	errorSubtype = models.ForeignKey(ErrorSubtype, on_delete=models.SET_NULL, null = True)
	description= models.CharField(null=True, max_length = 200)
	location = models.CharField(null = True, max_length = 200)
	resolved = models.BooleanField()
	def __str__(self):
		return str(self.id)
		
class FileModelErrorImage(models.Model):
    bytes = models.TextField()
    filename = models.CharField(max_length=255)
    mimetype = models.CharField(max_length=50)

class ErrorImage(models.Model):
	name = models.CharField(max_length=100)
	picture = models.ImageField(upload_to='report.FileModelErrorImage/bytes/filename/mimetype', blank=True, null=True)
	error = models.ForeignKey(Error, on_delete=models.CASCADE, null = True)

class SavedReport(models.Model):
	name = models.CharField(max_length = 50)
	createdDate = models.CharField(max_length = 50)
	createdUser = models.CharField(max_length = 50)
	
class ReportData(models.Model):
	report = models.ForeignKey(SavedReport, on_delete=models.CASCADE, null = True)
	wpName = models.CharField(max_length = 50)
	type = models.CharField(max_length = 50)
	poc = models.CharField(max_length = 50)
	pocEmail = models.CharField(max_length = 50)
	
class ReportErrorGroup(models.Model):
	report = models.ForeignKey(SavedReport, on_delete=models.CASCADE, null = True)
	category = models.CharField(max_length = 50)
	numErrors = models.CharField(max_length = 50)
	errorType = models.CharField(max_length = 50)
	errorSubtype = models.CharField(max_length = 50)
	
class ReportWorkUnitId(models.Model):
	reportData = models.ForeignKey(ReportData, on_delete = models.CASCADE, null = True)
	workUnitId = models.CharField(max_length = 50)
	
class ReportDeliverableData(models.Model):
	reportData = models.ForeignKey(ReportData, on_delete = models.CASCADE, null = True)
	category = models.CharField(max_length = 50)
	description = models.CharField(max_length = 50)
	accepted = models.CharField(max_length = 5)
	summary = models.CharField(max_length = 1000)

class FileModelReportAoiImage(models.Model):
    bytes = models.TextField()
    filename = models.CharField(max_length=255)
    mimetype = models.CharField(max_length=50)

class ReportAoiImage(models.Model):
	name = models.CharField(max_length=100)
	picture = models.ImageField(upload_to='report.FileModelReportAoiImage/bytes/filename/mimetype', blank=True, null=True)	
	reportData = models.ForeignKey(ReportData, on_delete = models.CASCADE, null = True)
	
class FileModelReportErrorImage(models.Model):
    bytes = models.TextField()
    filename = models.CharField(max_length=255)
    mimetype = models.CharField(max_length=50)

class ReportErrorImage(models.Model):
	name = models.CharField(max_length=100)
	picture = models.ImageField(upload_to='report.FileModelReportImage/bytes/filename/mimetype', blank=True, null=True)	
	errorGroup = models.ForeignKey(ReportErrorGroup, on_delete=models.CASCADE, null = True)	
	
class ReportPassFailData(models.Model):
	report = models.ForeignKey(SavedReport, on_delete = models.CASCADE, null = True)
	review = models.BooleanField(default = False)
	relVa = models.NullBooleanField(null = True)
	absVa = models.NullBooleanField(null = True)
	metadata = models.NullBooleanField(null = True)
	breaklines = models.NullBooleanField(null = True)
	reports = models.NullBooleanField(null = True)
	other = models.NullBooleanField(null = True)
	dem = models.NullBooleanField(null = True)
	swath = models.NullBooleanField(null = True)
	classified = models.NullBooleanField(null = True)

class ReportVaDataCollectionWorkUnit(models.Model):
	report = models.ForeignKey(SavedReport, on_delete = models.CASCADE)
	wu = models.CharField(max_length = 100)

class ReportVaDataCollectionCategory(models.Model):
	category = models.CharField(max_length = 100)
	wu = models.ForeignKey(ReportVaDataCollectionWorkUnit, on_delete = models.CASCADE)

class ReportVaData(models.Model):
	cat = models.ForeignKey(ReportVaDataCollectionCategory, on_delete = models.CASCADE)

class ReportVaData10(ReportVaData):
	cvaReqChkpts = models.FloatField(null = True)
	cvaRepChkpts = models.FloatField(null = True)
	cvaTestChkpts = models.FloatField(null = True)
	cvaReqValue = models.FloatField(null = True)
	cvaRepValue = models.FloatField(null = True)
	cvaTestValue = models.FloatField(null = True)
	fvaReqChkpts = models.FloatField(null = True)
	fvaRepChkpts = models.FloatField(null = True)
	fvaTestChkpts = models.FloatField(null = True)
	fvaReqValue = models.FloatField(null = True)
	fvaRepValue = models.FloatField(null = True)
	fvaTestValue = models.FloatField(null = True)
	
class ReportVaData12(ReportVaData):
	nvaReqChkpts = models.FloatField(null = True)
	nvaRepChkpts = models.FloatField(null = True)
	nvaTestChkpts = models.FloatField(null = True)
	nvaReqValue = models.FloatField(null = True)
	nvaRepValue = models.FloatField(null = True)
	nvaTestValue = models.FloatField(null = True)
	vvaReqChkpts = models.FloatField(null = True)
	vvaRepChkpts = models.FloatField(null = True)
	vvaTestChkpts = models.FloatField(null = True)
	vvaReqValue = models.FloatField(null = True)
	vvaRepValue = models.FloatField(null = True)
	vvaTestValue = models.FloatField(null = True)
	
class ReportSva(models.Model):
	reportVaData = models.ForeignKey(ReportVaData10, on_delete = models.CASCADE)
	svaReqChkpts = models.FloatField(null = True)
	svaRepChkpts = models.FloatField(null = True)
	svaTestChkpts = models.FloatField(null = True)
	svaReqValue = models.FloatField(null = True)
	svaRepValue = models.FloatField(null = True)
	svaTestValue = models.FloatField(null = True)


	
	
	
	
	

