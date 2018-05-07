## Python imports
import json
import random
import ast
import os
import sys
import platform
import zipfile
import tempfile
from io import BytesIO
from datetime import datetime
from collections import defaultdict
import urllib, io
from .report_generator import ReportGenerator
from .error_shapefile_generator import ErrorShapefileGenerator
from .error_geopackage_generator import ErrorGeopackageGenerator
from PIL import Image
## Django imports
from django.http import JsonResponse
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.forms.models import model_to_dict
from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404, get_list_or_404
from django.template import loader
from django.template import RequestContext
from django.template.loader import render_to_string
from django.views import generic
from django.db import connections
from django.db import models
from django.contrib import messages
from django.conf import settings
from django.contrib.staticfiles.templatetags.staticfiles import static
##	Import models here
from .models import Deliverable
from manager.models import WorkPackage
from manager.models import Review
from manager.models import ReviewProgressChecklist
from manager.models import ChecklistItem
from manager.models import ChecklistCategory
from .models import CollectionInfo
from .models import WorkUnit
from .models import VaRequirement
from .models import VaRequirement10
from .models import VaRequirement12
from .models import SuppVaMeasure
from .models import Error
from .models import ErrorImage
from .models import ErrorType
from .models import ErrorSubtype
from .models import DEM
from .models import DemTab
from .models import DeliverableCategory
from manager.models import ProjectSpecification
from manager.models import QualityLevel
from manager.models import SensorUsed
from manager.models import SensorType
from .models import SuppVaResults
from .models import VaData
from .models import VaData10
from .models import VaData12
from .models import SwathTab
from .models import Swath
from .models import Classified
from .models import ClassifiedTab
from manager.models import PointCloudClassification
from .models import AggregatedWuDeliverableCategory
from .models import AggregatedWuDeliverable
from .models import AggregatedWuDeliverableTab
from .models import SavedReport
from .models import ReportData
from .models import ReportErrorGroup
from .models import ReportWorkUnitId
from .models import ReportDeliverableData
from .models import ReportAoiImage
from .models import ReportErrorImage
from .models import ReportPassFailData
from .models import ReportVaData
from .models import ReportVaData10
from .models import ReportVaData12
from .models import ReportSva
from .models import ReportVaDataCollectionCategory
from .models import ReportVaDataCollectionWorkUnit
from .models import FileModelErrorImage
from .models import FileModelReportAoiImage
from .models import FileModelReportErrorImage
	
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse

from .decorators import qcr_user_authenticated


## View for redirecting non-users
def notAUser(request):
	return render(request, 'notAUser.html')

## View that handles the displaying of the correct home page based on whether or not the user is authorized. If the user is
## an admin, the staff page will be displayed which allows for review creation, loading WP and WU from PTS, and managing of
## several object models, including QL, Sensor Types, Sensors Used, as well as adding authorized users. Non admin users are
## displayed a list of all their currently assigned reviews.
@qcr_user_authenticated
def home(request):
	init()
	user = request.user
	if user.is_staff:
		reviews = Review.objects.all()
		packageList = WorkPackage.objects.all()
		qualityLevels = QualityLevel.objects.all()
		sensorTypes = SensorType.objects.all()
		sensorsUsed = SensorUsed.objects.all()
		qcrUsers = []
		usgsUsers = []
		users = User.objects.all()
		for u in users:
			groups = u.groups.all()
			for g in groups:
				if g.name == 'qcr_user':
					qcrUsers.append(u.username)
			if u.username not in qcrUsers and not u.is_staff:
				usgsUsers.append(u.username)
		checklists = list(ReviewProgressChecklist.objects.all())
		catItemsDict = defaultdict(list)
		catPositionDict = defaultdict(list)
		if checklists != []:
			categories = ChecklistCategory.objects.all()
			for cat in categories:
				catItemsDict[cat.name] = []
				catPositionDict[cat.name].append(1)
			for cl in checklists:
				if cl.master == True:
					cl.review = None
					clItems = ChecklistItem.objects.filter(checklist = cl).order_by('placement')
					i = 2
					if clItems != []:
						for item in clItems:
							cat = item.category.name
							catItemsDict[cat].append(item)
							catPositionDict[cat].append(i)
							i += 1
		else:
			ReviewProgressChecklist.objects.create(master = True)
		
		if settings.DEV_TOOLS:
			if catItemsDict == {} and catPositionDict == {}:
				
				return render(request, 'admin_home.html', {'devMode': 'True',
															'user':user.username,
															'qcrUsers':qcrUsers, 
															'usgsUsers':usgsUsers, 
															'reviews':reviews, 
															'packageList':packageList, 
															'qualityLevels':qualityLevels, 
															'sensorTypes':sensorTypes, 
															'sensorsUsed':sensorsUsed})
			else:
				templateDict = dict(catItemsDict)
				posDict = dict(catPositionDict)
				return render(request, 'admin_home.html', {'devMode': 'True',
															'user':user.username,
															'qcrUsers':qcrUsers, 
															'usgsUsers':usgsUsers, 
															'reviews':reviews, 
															'packageList':packageList, 
															'qualityLevels':qualityLevels, 
															'sensorTypes':sensorTypes, 
															'sensorsUsed':sensorsUsed,
															'checklistItems':templateDict,
															'checklistPositions':posDict})
		else:
			if catItemsDict == {} and catPositionDict == {}:
				return render(request, 'admin_home.html', {'user':user.username,
															'qcrUsers':qcrUsers,
															'usgsUsers':usgsUsers,
															'reviews':reviews,
															'packageList':packageList,
															'qualityLevels':qualityLevels,
															'sensorTypes':sensorTypes, 
															'sensorsUsed':sensorsUsed})
			else:
				templateDict = dict(catItemsDict)
				posDict = dict(catPositionDict)
				return render(request, 'admin_home.html', {'user':user.username,
															'qcrUsers':qcrUsers,
															'usgsUsers':usgsUsers,
															'reviews':reviews,
															'packageList':packageList,
															'qualityLevels':qualityLevels,
															'sensorTypes':sensorTypes, 
															'sensorsUsed':sensorsUsed,
															'checklistItems':templateDict,
															'checklistPositions':posDict})
															
	else:
		review_list = Review.objects.filter(user = user)
		return render(request, 'user_home.html', {'review_list':review_list, 'user':user.username})

## View that returns project spec of the WP associated with a WU, or an aggregated deliverable tab
@qcr_user_authenticated	
def getProjectSpec(request, workUnit_id = None, tab_id = None):
	if request.is_ajax():
		if request.method == 'GET':
			projectSpec = None
			if workUnit_id:
				wu = WorkUnit.objects.get(pk = workUnit_id)
				wp = wu.workPackage
				projectSpec = wp.projectSpec
			if tab_id:
				tab = get_object_or_404(AggregatedWuDeliverableTab, pk = tab_id)
				vaReq = tab.vaRequirement
				projectSpec = vaReq.projectSpec
			spec = str(projectSpec.name).replace('.','')
			responseData = {}
			responseData['spec'] = spec
			return JsonResponse(responseData)

#################################
## Review Tab Controller Views ##
#################################

## View returning html template of a specific review
@qcr_user_authenticated
def review(request, review_id):
	review = Review.objects.get(pk = review_id)
	return render(request, 'review.html', {'review':review})

## View returning workunit tabcontroller for a specific review
@qcr_user_authenticated
def workUnits(request, review_id):
	if request.is_ajax():
		if request.method == "GET":
			responseData = {}
			review = Review.objects.get(pk=review_id)
			try:
				workUnits = WorkUnit.objects.filter(review=review).order_by('workUnitId')
				wuNames = []
				wuNamesIds = {}
				for wu in workUnits:
					workUnit = WorkUnit.objects.get(workUnitId=wu.workUnitId)
					wuNames.append(wu.name)
					wuNamesIds[wu.name] = wu.workUnitId
				if wuNames == []:
					raise Exception()
				minVal = min(sorted(wuNames))
				minVal = wuNamesIds[minVal]
				responseData['minVal'] = minVal
				sortedWorkUnits = []
				for name in sorted(wuNames):
					id = wuNamesIds[name]
					wu = WorkUnit.objects.get(pk=id)
					sortedWorkUnits.append(wu)
				tabsHtml = render_to_string('workunit_tabs.html', {'workUnits': sortedWorkUnits})
				responseData['html'] = tabsHtml
			except Exception as e:
				##ADD A 'NO WORK UNITS' TEMPLATE OR SOMETHING
				responseData["nodata"] = 'no work units'

			finally:
				return JsonResponse(responseData)

## View that displays project information for the work package associated with a specific review
@qcr_user_authenticated
def workPackage(request, review_id):
	review = get_object_or_404(Review, pk = review_id)
	wus = WorkUnit.objects.filter(review = review)
	rvwWorkPkg = None
	for wu in wus:
		rvwWorkPkg = wu.workPackage
		break
	projectSpecs = ProjectSpecification.objects.all()
	projectSpec = rvwWorkPkg.projectSpec
	projectSpecName = projectSpec.name
	if request.is_ajax():
		method = request.method
		if method == "POST":
			jsonData = json.loads(request.body.decode('utf-8'))
			rvwWorkPkg = buildWorkPackage(jsonData, rvwWorkPkg)
		workPackage = buildWorkPackageContext(rvwWorkPkg, method)
	workPkgHtml = render_to_string('workpackage_form.html', {'workPackage':workPackage, 'updateWorkPackage':'True', 'projectSpecs':projectSpecs, 'projectSpec':projectSpecName})
	return HttpResponse(workPkgHtml)

## View that returns summary list of all deliverables
@qcr_user_authenticated			
def deliverables(request, workUnit_id):
	if request.is_ajax():
		wu = get_object_or_404(WorkUnit, pk = workUnit_id)
		if request.method == 'GET':
			deliverables = list(wu.deliverable_set.all())
			aggWuDeliverables = list(wu.aggregatedWuDeliverable.all())
			wuHtml = ''
			if deliverables != [] or aggWuDeliverables != []:
			
				categories = []
				genCats = DeliverableCategory.objects.all()
				for cat in genCats:
					categories.append(cat.name)
				aggWuCats = AggregatedWuDeliverableCategory.objects.all()
				for cat in aggWuCats:
					categories.append(cat.name)
				wuHtml = render_to_string('deliverablesList.html', {'deliverables':deliverables, 'aggWuDelivs':aggWuDeliverables, 'categories':categories})
			else:
				categories = []
				genCats = DeliverableCategory.objects.all()
				for cat in genCats:
					categories.append(cat.name)
				aggWuCats = AggregatedWuDeliverableCategory.objects.all()
				for cat in aggWuCats:
					categories.append(cat.name)
				wuHtml = render_to_string('deliverablesList.html', {'categories':categories})
			return HttpResponse(wuHtml)
			
			
@qcr_user_authenticated	
def delivTabUpdate(request):
	if request.is_ajax():
		if request.method == 'POST':
			responseData = {}
			jsonData = json.loads(request.body.decode('utf-8'))
			type = jsonData['type']
			id = int(jsonData['id'])
			deliv = None
			if type == 'Gen':
				deliv = Deliverable.objects.get(pk = id)
			else:
				deliv = AggregatedWuDeliverable.objects.get(pk = id)
			deliv.description = jsonData['description']
			deliv.category = jsonData['category']
			deliv.quantity = int(jsonData['quantity'])
			deliv.spatialReference = jsonData['spatRef']
			if jsonData['reqPerContract'] == 'True':
				deliv.reqPerContract = True
			else:
				deliv.reqPerContract = False 
			if jsonData['reqPerSpec'] == 'True':
				deliv.reqPerSpec = True
			else:
				deliv.reqPerSpec = False
			if jsonData['delivered'] == 'True':
				deliv.delivered = True
			else:
				deliv.delivered = False
			if jsonData['accepted'] == 'True':
				deliv.accepted = True
			else:
				deliv.accepted = False
			
			deliv.save()
			
			categories = []
			genCats = DeliverableCategory.objects.all()
			for cat in genCats:
				categories.append(cat.name)
			aggWuCats = AggregatedWuDeliverableCategory.objects.all()
			for cat in aggWuCats:
				categories.append(cat.name)
			
			if type == 'Gen':
				html = render_to_string('deliverable_row.html', {'d':deliv, 'categories':categories})
			else:
				html = render_to_string('deliverable_row.html', {'awd':deliv, 'categories':categories})
			responseData['html'] = html			
			return JsonResponse(responseData)
			
			
## View that displays DEM tab
@qcr_user_authenticated
def demSubtabs(request):
	if request.is_ajax():
		if request.method == 'GET':
			responseData = {}
			html = render_to_string('dem_subtabs.html')
			responseData['html'] = html
			return JsonResponse(responseData)

## View that displays Metadata Tab
@qcr_user_authenticated
def metadataTab(request):
	responseData = {}
	html = render_to_string('metadataTab.html', {})
	responseData['html'] = html
	return JsonResponse(responseData)

## View that displays Pointcloud Tab
@qcr_user_authenticated
def pointcloudTab(request, review_id):
	responseData = {}
	review = get_object_or_404(Review, pk=review_id)
	html = render_to_string('pointcloudTab.html', {})
	responseData['html'] = html
	return JsonResponse(responseData)

###############################
## Generic Deliverable Views ##
###############################

## View for displaying generic deliverable form
@qcr_user_authenticated			
def delivForm(request, review_id = None, category_id = None, workunit_id = None):
	if request.is_ajax():
		if request.method == 'GET':
			categories = []
			genericCategories = DeliverableCategory.objects.all()
			aggWuCategories = AggregatedWuDeliverableCategory.objects.all()
			for cat in genericCategories:
				categories.append(cat.name)
			for cat in aggWuCategories:
				if cat.category == 1:
					name = 'DEM'
				elif cat.category == 2:
					name = 'Unclassified Swath'
				else:
					name = 'Classified Pointcloud'
				categories.append(name)
			responseData = {}
			responseData['categories'] = categories
			return JsonResponse(responseData)

## View for creating new generic deliverable from form data
@qcr_user_authenticated			
def delivCreate(request, workunit_id = None):
	if request.is_ajax():
		if request.method == 'POST':
			jsonData = json.loads(request.body.decode('utf-8'))
			delivDict = {}
			for key, value in jsonData.items():
				if key != "workUnits":
					delivDict[key] = value	
			if workunit_id:
				deliverable = buildDeliverableObject(delivDict, workunit_id)
			else:
				deliverable = buildDeliverableObject(delivDict)
				
			responseData = {}
			try:
				reqWus = jsonData["workUnits"]
				workUnits = []
				if reqWus != '':
					reqWuNames = []
					workUnits = reqWus.split(',')
					if workUnits != []:
						for id in workUnits:
							wu = WorkUnit.objects.get(pk = id)
							wu.deliverable_set.add(deliverable)
							wu.save()
							reqWuNames.append(wu.name)
				if workunit_id:
					wu = WorkUnit.objects.get(pk = workunit_id)
					responseData['updatedWu'] = str(wu.name) + ',' + str(reqWuNames).strip('[]').strip("'");
				else:
					responseData['updatedWu'] = str(reqWus)
				responseData['createdDeliv'] = str(deliverable.id)
				wu = WorkUnit.objects.get(pk = workUnits[0])
				responseData['workUnit'] = wu.name
			except:
				if workunit_id:
					wu = WorkUnit.objects.get(pk = workunit_id)
					responseData['updatedWu'] = str(wu.name)
					responseData['workUnit'] = str(wu.name)
				responseData['createdDeliv'] = str(deliverable.id)
				
			return JsonResponse(responseData)

## View for displaying all generic deliverables of a specificed category associated with a specified workunit
@qcr_user_authenticated
def deliverablesByCategory(request, category_id, workUnit_id = None):
	bootstrapHeader = '<br><div id = "container" class="container">'
	panelFooter = '</div></div>'
	bootstrapRowFooter = '</div></div></div>'
	errorTypes = ErrorType.objects.filter(deliverableCategory__category = category_id)
	deliverablesQuery = None
	try:
		html = '<br>'
		workUnit = WorkUnit.objects.get(pk = workUnit_id)
		cats = DeliverableCategory.objects.filter(category=int(category_id))
		currentReview = get_object_or_404(Review, pk=workUnit.review.pk)
		wuList = WorkUnit.objects.filter(review=currentReview).exclude(workUnitId = workUnit.workUnitId)
		deliverablesQuery = workUnit.deliverable_set.filter(deliverableCategory__category = int(category_id))
		if deliverablesQuery == []:
			if category_id == '1':
				type = 'XML Metadata'
			if category_id == '2':
				type = 'Breaklines'
			if category_id == '6':
				type = 'Reports and Shapefiles'
			if category_id == '7':
				type = 'Other'
			html += '<p>No ' + type + ' deliverables have been added to this work unit.</p><br>'
		if wuList != []:
			html += render_to_string('addDeliverablePanel.html', {'categories': cats, 'wuList': wuList})
		else:
			html += render_to_string('addDeliverablePanel.html', {'categories': cats})
			
		for deliverable in deliverablesQuery:
			delivPanelHtml = ''
			deliverableType = str(deliverable.deliverableCategory.name)
			# generate error html tables (if errors exist)
			errors = Error.objects.filter(deliverable = deliverable)
			delivWu = deliverable.workUnit.all()
			wuList = WorkUnit.objects.filter(review=currentReview).exclude(workUnitId__in = delivWu)
			if errors != []:
				delivPanelHtml = render_to_string('genericDeliverablePanel.html', {'type':deliverableType,'deliverable': deliverable, 'id':deliverable.id, 'errors': errors, 'errorTypes': errorTypes, 'categories': cats, 'wuList': wuList})
			else:
				delivPanelHtml = render_to_string('genericDeliverablePanel.html', {'type':deliverableType,'deliverable': deliverable, 'id':deliverable.id, 'errorTypes': errorTypes, 'categories': cats, 'wuList': wuList})
			html += delivPanelHtml
		if html == '':
			raise Exception()
		return HttpResponse(html)
	except:
		deliverableCategory = ''
		if category_id == '1':
			deliverableCategory = 'metadata'
		if category_id == '2':
			deliverableCategory = 'breaklines'
		if category_id == '6':
			deliverableCategory = 'reports and shapefiles'
		if category_id == '7':
			deliverableCategory = '"other"'	
		
		return HttpResponse('<br><p>There are no '+deliverableCategory+' deliverables in this review.</p>')

## View for handling the deletion of a generic deliverable
@qcr_user_authenticated		
def deleteDeliv(request, deliv_id):
	if request.is_ajax():
		if request.method == 'POST':
			deliv = Deliverable.objects.get(pk=deliv_id)
			deliv.delete()
			responseData = {}
			responseData['success'] = 'True'
			return JsonResponse(responseData)

## View for handling making modifications to a generic deliverables data
@qcr_user_authenticated			
def updateDeliv(request, deliv_id):
	if request.is_ajax():
		if request.method == 'POST':
			responseData = {}
			try:
				deliverable = Deliverable.objects.get(pk=deliv_id)
				jsonData = json.loads(request.body.decode('utf-8'))
				deliverable.deliverableCategory = DeliverableCategory.objects.get(name=jsonData["deliverableCategory"])
				if jsonData["description"] == '':
					deliverable.description = None
				else:
					deliverable.description = jsonData["description"]
				if jsonData["quantity"] == '':
					deliverable.quantity = None
				else:
					deliverable.quantity = jsonData["quantity"]
				if jsonData["spatRef"] == '':
					deliverable.spatialReference = None
				else:
					deliverable.spatialReference = jsonData["spatRef"]
				if jsonData["reqPerContract"] == '':
					deliverable.reqPerContract = None
				elif jsonData["reqPerContract"] == 'false':
					deliverable.reqPerContract = False
				elif jsonData["reqPerContract"] == 'true':
					deliverable.reqPerContract = True
				if jsonData["reqPerSpec"] == '':
					deliverable.reqPerSpec = None
				elif jsonData["reqPerSpec"] == 'false':
					deliverable.reqPerSpec = False
				elif jsonData["reqPerSpec"] == 'true':
					deliverable.reqPerSpec = True
				if jsonData["delivered"] == '':
					deliverable.delivered = None
				elif jsonData["delivered"] == 'false':
					deliverable.delivered = False
				elif jsonData["delivered"] == 'true':
					deliverable.delivered = True
				if jsonData["comment"] == '':
					deliverable.comment = None
				else:
					deliverable.comment = jsonData["comment"]
				if jsonData["accepted"] == '':
					deliverable.accepted = None
				elif jsonData["accepted"] == 'false':
					deliverable.accepted = False
				elif jsonData["accepted"] == 'true':
					deliverable.accepted = True
				deliverable.save()
				if jsonData['workUnits']:
					workUnits = jsonData['workUnits'].split(',')
					for wu in workUnits:
						workUnit = get_object_or_404(WorkUnit, name = wu)
						deliverable.workUnit.add(workUnit)
						deliverable.save()
					responseData['applied']=jsonData['workUnits']
				responseData['success'] = 'True'
				responseData['delivId'] = str(deliv_id)
			except:
				responseData['success'] = 'False'

			return JsonResponse(responseData)

## View for handling the removal of a Work Unit link from a specified deliverable
@qcr_user_authenticated			
def removeGenericDelivFromWu(request, deliv_id, workunit_id):
	if request.is_ajax():
		if request.method == 'POST':
			deliverable = get_object_or_404(Deliverable, pk = deliv_id)
			workUnit = get_object_or_404(WorkUnit, pk = workunit_id)
			deliverable.workUnit.remove(workUnit)
			deliverable.save()
			relWus = list(deliverable.workUnit.all())
			if relWus == []:
				deliverable.delete()
			responseData = {}
			responseData['success'] = 'True';
			return JsonResponse(responseData)

## View that returns a warning upon attempted wu link removal if there is only one wu link remaining
@qcr_user_authenticated			
def checkRemainingWu(request, deliv_id):
	if request.is_ajax():
		if request.method == "GET":
			responseData = {}
			deliverable = get_object_or_404(Deliverable, pk=deliv_id)
			wus = list(deliverable.workUnit.all())
			if len(wus) == 1:
				responseData['warn'] = 'True'
			else:
				responseData['warn'] = 'False'
			return JsonResponse(responseData)

## View for handling the creation of a new error
@qcr_user_authenticated
def addError(request, deliverable_id):
	deliverable = get_object_or_404(Deliverable, pk=deliverable_id)
	if request.method == 'POST':
		responseData = {}
		error = None
		try:
			type = ErrorType.objects.get(name=request.POST.get("type"), deliverableCategory__category=deliverable.deliverableCategory.category)
			if request.POST.get("resolved") == 'true':
				error = Error.objects.create(deliverable=deliverable, errorType=type, resolved=True)
			else:
				error = Error.objects.create(deliverable=deliverable, errorType=type, resolved=False)
			error = buildError(request, error)
			error.save()
			responseData['success'] = 'True'
			responseData['delivId'] = str(deliverable_id)
		except:
			responseData['success'] = 'False'
		finally:
			return JsonResponse(responseData)

## View handling the deletion of a specific error
@qcr_user_authenticated
def deleteError(request, error_id, category_id=None):
	if request.is_ajax():
		if request.method == 'POST':
			error = Error.objects.get(pk=error_id)
			imgs = ErrorImage.objects.filter(error = error)
			for i in imgs:
				try:
					fmei = FileModelErrorImage.objects.get(filename = str(i.picture))
					if fmei:
						fmei.delete()
				except:
					continue
			deliverable = None
			delivId = None
			if not category_id:
				deliverable = error.deliverable
				delivId = deliverable.id
			else:
				aggregatedWuDeliv = error.aggregatedWuDeliverable
				delivId = aggregatedWuDeliv.id
			error.delete()
			responseData = {}
			responseData['success'] = 'True'
			responseData['delivId'] = str(delivId)
			return JsonResponse(responseData)

## View for retrieving a specific error
@qcr_user_authenticated
def getError(request, error_id):
	error = get_object_or_404(Error, pk=error_id)
	if error.deliverable != None:
		category = error.deliverable.deliverableCategory
		errorTypes = ErrorType.objects.filter(deliverableCategory__category = category.category)
	if error.aggregatedWuDeliverable != None:
		category = error.aggregatedWuDeliverable.category
		errorTypes = ErrorType.objects.filter(aggDeliverableCategory__category = category.category)
	responseData = {}
	responseData['html'] = render_to_string('error_form.html', {'error': error, 'errorTypes': errorTypes})
	return JsonResponse(responseData)

## View for handling the editing of a specific error
@qcr_user_authenticated
def updateError(request, error_id):
	if request.is_ajax():
		if request.method == 'POST':
			responseData = {}
			error = get_object_or_404(Error, pk=error_id)
			try:
				try:
					errorType = ErrorType.objects.get(name=request.POST.get('type'), deliverableCategory__category=error.deliverable.deliverableCategory.category)
				except:
					errorType = ErrorType.objects.get(name=request.POST.get('type'), aggDeliverableCategory__category=error.aggregatedWuDeliverable.category.category)
				error.errorType = errorType
				if request.POST.get('subtype') != '':
					error.errorSubtype = ErrorSubtype.objects.get(name=request.POST.get('subtype'), errorType = errorType)
				error.description = request.POST.get('description')
				error.location = request.POST.get('loc')
				error.resolved = request.POST.get('resolved')
				if request.FILES:
					if request.FILES["image"]:
						file = request.FILES["image"]
						newErrImg = ErrorImage.objects.create(picture=file, error=error)
						newErrImg.save()
				error.save()
			except:
				responseData['success'] = 'Failure'
			responseData = {}
			responseData['success'] = 'True'
			return JsonResponse(responseData)

## View for retrieving Errors Table
@qcr_user_authenticated
def getErrorsTable(request, deliverable_id, category_id=None):
	responseData = {}
	if not category_id:
		deliverable = get_object_or_404(Deliverable, pk=deliverable_id)
		errors = Error.objects.filter(deliverable=deliverable).order_by('-pk')
		responseData['html'] = render_to_string('error_table.html', {'id': deliverable_id, 'errors': errors})
	else:
		tab = get_object_or_404(AggregatedWuDeliverableTab, pk=deliverable_id)
		deliverable = tab.deliverable
		errors = Error.objects.filter(aggregatedWuDeliverable=deliverable).order_by('-pk')
		responseData['html'] = render_to_string('error_table.html', {'id': deliverable_id, 'errors': errors})
	return JsonResponse(responseData)

## View for updating resolved status in Errors Table
@qcr_user_authenticated
def updateErrorsTable(request, deliverable_id, category_id=None):
	if request.is_ajax():
		if request.method == "POST":
			responseData = {}
			jsonData = json.loads(request.body.decode('utf-8'))
			if not category_id:
				deliverable = get_object_or_404(Deliverable, pk=deliverable_id)
				errors = Error.objects.filter(deliverable=deliverable)
			else:
				tab = get_object_or_404(AggregatedWuDeliverableTab, pk=deliverable_id)
				deliverable = tab.deliverable
				errors = Error.objects.filter(aggregatedWuDeliverable=deliverable)
			for e in errors:
				e.resolved = jsonData[str(e.pk)]
				e.save()
			responseData['result'] = 'success'
			return JsonResponse(responseData)

## View for getting error subtypes of a given error type
@qcr_user_authenticated
def populateErrorSubtype(request):
	if request.is_ajax():
		if request.method == "POST":
			try:
				responseData = {}
				jsonData = json.loads(request.body.decode('utf-8'))
				category = AggregatedWuDeliverableCategory.objects.filter(category = jsonData['category'])
				errorType = ErrorType.objects.filter(aggDeliverableCategory__category = category, name = jsonData['errorType'])
				subtypes = ErrorSubtype.objects.filter(errorType = errorType)
				sublist = ''
				for subtype in subtypes:
					sublist += subtype.name + ','
				sublist = sublist[:-1]
			except:
				responseData = {}
				jsonData = json.loads(request.body.decode('utf-8'))
				error = get_object_or_404(Error, pk=jsonData['errorID'])
				try:
					errorType = ErrorType.objects.filter(
						aggDeliverableCategory__category=error.aggregatedWuDeliverable.category.category,
						name=jsonData['errorType'])
				except:
					errorType = ErrorType.objects.filter(
						deliverableCategory__category=error.deliverable.deliverableCategory.category,
						name=jsonData['errorType'])
				subtypes = ErrorSubtype.objects.filter(errorType=errorType)
				sublist = ''
				for subtype in subtypes:
					sublist += subtype.name + ','
				sublist = sublist[:-1]
				if error.errorSubtype:
					responseData['selected'] = str(error.errorSubtype)
			responseData['subTypes'] = sublist
			responseData['result'] = 'success'
			return JsonResponse(responseData)

## View for deleting selected error images
@qcr_user_authenticated
def deleteErrorImages(request):
	if request.is_ajax():
		if request.method == 'POST':
			responseData = {}
			jsonData = json.loads(request.body.decode('utf-8'))
			imageIDs = jsonData['ids']
			for id in imageIDs:
				try:
					image = ErrorImage.objects.get(pk=int(id))
					image.delete()
				except:
					pass
			responseData = {}
			responseData['success'] = 'True'
			return JsonResponse(responseData)

###############################
## Collection Info Tab Views ##
###############################
@qcr_user_authenticated
def checkCollectionInfoDomains(request):
	qualityLevels = list(QualityLevel.objects.all())
	sensorTypes = list(SensorType.objects.all())
	sensorsUsed = list(SensorUsed.objects.all())
	success = True
	missing = []
	if qualityLevels == []:
		success = False
		missing.append('Quality Level')
	if sensorTypes == []:
		success = False
		missing.append('Sensor Type')
	if sensorsUsed == []:
		success = False
		missing.append('Sensor Used')
	
	responseData = {}
	responseData['success'] = str(success)
	if success == False:
		responseData['missing'] = missing
		
	return JsonResponse(responseData)
	


## View for returning CI for a specific Work Unit, and handling modifications to the CI
@qcr_user_authenticated
def collectionInfo(request, workUnit_id):
	if request.is_ajax():
		responseData = {}
		workUnit = get_object_or_404(WorkUnit, pk = workUnit_id)
		workPackage = workUnit.workPackage
		review = workUnit.review
		projectSpec = workPackage.projectSpec
		projectSpecName = projectSpec.name
		qualLevels = QualityLevel.objects.all()
		sensorsUsed = SensorUsed.objects.all()
		sensorTypes = SensorType.objects.all()
		collectionInfo = None
		if request.method == 'GET':
			try:
				## Retrieve existing collection info tab data
				collectionInfo = workUnit.collectionInfo
				if not collectionInfo.id:
					raise Exception('No Collection Info')
			except:	
				noWuHtml = render_to_string('nocollinfo.html')
				responseData['html'] = noWuHtml
				return JsonResponse(responseData)				
		if request.method == 'POST':
			jsonData = json.loads(request.body.decode('utf-8'))
			wuHtml = ''
			try:
				collectionInfo = workUnit.collectionInfo
				## Break off the non-multiselect input data elements to build the collection info object.
				collInfoDict = {}
				for key, value in jsonData.items():
					if key != "workUnits":
						collInfoDict[key] = value
				## Update the collection info object with the incoming request data
				collectionInfo = buildCollectionInfoObject(collInfoDict, collectionInfo)
				aggWuDelivs = workUnit.aggregatedWuDeliverable.all()
				for deliv in aggWuDelivs:
					if deliv.category.name == 'DEM':
						deliv.resolution = collectionInfo.demResolution
						deliv.resolutionUnits = collectionInfo.demResolutionUnits
						deliv.save()	
				
				if jsonData['workUnits'] != '':
					responseData = applyCollectionInfo(jsonData, collectionInfo, workUnit_id)
			except:
				collectionInfo = workUnit.collectionInfo
				collInfoDict = {}
				for key, value in jsonData.items():
					if key != "workUnits":
						collInfoDict[key] = value	
				collectionInfo = CollectionInfo.objects.create()
				collectionInfo = buildCollectionInfoObject(collInfoDict, collectionInfo)
				aggWuDelivs = workUnit.aggregatedWuDeliverable.all()
				for deliv in aggWuDelivs:
					if deliv.category.name == 'DEM':
						deliv.resolution = collectionInfo.demResolution
						deliv.resolutionUnits = collectionInfo.demResolutionUnits
						deliv.save()
				collectionInfo.save()
				try:
					qualityLevel = collectionInfo.qualityLevel
					vaRequirement = get_object_or_404(VaRequirement, projectSpec = projectSpec, qualityLevel = qualityLevel)
					collectionInfo.vaRequirement = vaRequirement
					collectionInfo.save()
				except:
					pass
				workUnit.collectionInfo = collectionInfo
				workUnit.save()
				responseData = applyCollectionInfo(jsonData, collectionInfo, workUnit_id)
				responseData['updatedWu'] = str(workUnit.name)
				responseData['createdCi'] = str(collectionInfo.id)
				return JsonResponse(responseData)
	
		ql = collectionInfo.qualityLevel
		st = collectionInfo.sensorType
		su = collectionInfo.sensorUsed
		qualityLevel = ql.name		
		sensorType = st.name
		sensorUsed = su.name
		responseCollInfo = buildCollectionInfoJsonResponse(collectionInfo)
		freeWus = freeWorkUnits(review, 'collectionInfo', workUnit_id)
		wus = WorkUnit.objects.filter(collectionInfo = collectionInfo)
		wuSameInfo = []
		for wu in wus:
			if wu != workUnit:
				wuSameInfo.append(wu)			
		vaRequirement = None	
		try:
			## IF project spec changes, this needs to change
			vaRequirement = collectionInfo.vaRequirement
			vaSpec = vaRequirement.projectSpec
			vaQl = vaRequirement.qualityLevel
			if vaSpec != projectSpec:
				vaRequirement = None
				collectionInfo.vaRequirement = None
				collectionInfo.save()
				raise Exception()
			if vaQl != ql:
				vaRequirement = None
				collectionInfo.vaRequirement = None
				collectionInfo.save()
				raise Exception()
			if vaRequirement:
				responseData['vaRequirement'] = 'True'
			else:
				raise Exception()
		except:
			try:
				vaRequirement = VaRequirement.objects.get(projectSpec = projectSpec, qualityLevel = ql)
				collectionInfo.vaRequirement = vaRequirement
				collectionInfo.save()
				if vaRequirement:
					responseData['vaRequirement'] = 'True'
				else:
					raise Exception()
			except:
				responseData['vaRequirement'] = 'False'
		tabHtml = buildCITabHtml(vaRequirement, responseCollInfo, freeWus, qualLevels, qualityLevel, sensorsUsed, sensorUsed, sensorTypes, sensorType, projectSpecName, wuSameInfo)
		responseData['html'] = tabHtml
		responseData['success'] = str(workUnit.name) + ' updated.'
		return JsonResponse(responseData)			

## View for handling the initial display of the CI form
@qcr_user_authenticated		
def collectionInfoForm(request, workunit_id = None):
	if request.is_ajax():
		if request.method == 'GET':
			bootstrapHeader = ''
			workUnits = {}
			if workunit_id:
				wu = get_object_or_404(WorkUnit, pk = workunit_id)
				review = wu.review
				workUnits = freeWorkUnits(review, 'collectionInfo', workunit_id)
				ql = wu.qualityLevel
				qualLevels = list(QualityLevel.objects.all())
				sensorsUsed = list(SensorUsed.objects.all())
				sensorTypes = list(SensorType.objects.all())
			if workUnits != {}:
				formHtml = render_to_string('collinfo_form.html', {'wuList':workUnits, 'qualLevels':qualLevels, 'sensorsUsed':sensorsUsed, 'sensorTypes':sensorTypes, 'form':'true', 'ql':ql})
			else:
				formHtml = render_to_string('collinfo_form.html', {'qualLevels':qualLevels, 'sensorsUsed':sensorsUsed, 'sensorTypes':sensorTypes,'form':'true', 'ql':ql})
			return HttpResponse(formHtml)	

## View for handling the deletion of a specific CI
@qcr_user_authenticated			
def deleteCollectionInfo(request, workunit_id):
	if request.is_ajax():
		if request.method == "POST":
			workUnit = get_object_or_404(WorkUnit, pk = workunit_id)
			aggWuDelivs = workUnit.aggregatedWuDeliverable.all()
			for deliv in aggWuDelivs:
				if deliv.category.name == 'DEM':
					dem = DEM.objects.get(pk = deliv.id)
					dem.resolution = None
					dem.resolutionUnits = None
					dem.save()
			collInfo = workUnit.collectionInfo
			collInfoId = collInfo.id
			collInfo.delete()
			responseData = {}
			responseData['success'] = 'Collection Info ' + str(collInfoId) + ' deleted.';
			return JsonResponse(responseData)

## View for building a list of all WUs linked to a given CI
@qcr_user_authenticated			
def checkRelatedWorkUnits(request, workunit_id):
	if request.is_ajax():
		if request.method == "GET":
			responseData = {}
			workUnit = get_object_or_404(WorkUnit, pk = workunit_id)
			collInfo = workUnit.collectionInfo
			relWus = list(WorkUnit.objects.filter(collectionInfo = collInfo))
			if len(relWus) == 1:
				if relWus[0] == workUnit:
					responseData['warn'] = 'true'
			else:
				responseData['warn'] = 'false'
			return JsonResponse(responseData)

## View for removing WU link from specific CI
@qcr_user_authenticated			
def removeCollectionInfo(request, workunit_id):
	if request.is_ajax():
		if request.method == "POST":
			workUnit = get_object_or_404(WorkUnit, pk = workunit_id)
			collInfo = workUnit.collectionInfo			
			collInfoId = str(collInfo.id)
			workUnit.collectionInfo = None
			workUnit.save()	
			responseData = {}
			responseData['success'] = 'Collection Info ' + str(collInfoId) + ' removed.';
			return JsonResponse(responseData)

############################################
## Aggregated Work Unit Deliverable Views ##
############################################

## View for handling the  of DEM, Swath, and Classified Tabs
@qcr_user_authenticated
def aggregatedWuDeliverableTabs(request, review_id, category_id):
	if request.is_ajax():
		if request.method == "GET":
			responseData = {}
			review = get_object_or_404(Review, pk = review_id)
			wus = WorkUnit.objects.filter(review = review)
			classifications = []
			# If displaying classified tab, get classifications from WP
			if category_id == '3':
				classifications = PointCloudClassification.objects.filter(workPackage = wus[0].workPackage).order_by('classificationId')
			delivs = getAggregatedWuDeliverables(wus, category_id)
			tabIds = {}
			if delivs != []:
				tabIds = getAggregatedWuDeliverableTabs(delivs, review)
			if tabIds != {}:
				sortedTabIds = {}
				sortedDelivs = sorted(tabIds.values())
				for deliv in sortedDelivs:
					for tabId, delivId in tabIds.items():
						if delivId == deliv:
							sortedTabIds[tabId] = delivId
				tabIds = sortedTabIds
				html = buildAggregatedWuTabHtml(category_id, tabIds, review, classifications)
				minVal = min(list(tabIds.keys()))
				responseData['minVal'] = minVal
				responseData['html'] = html
			else:
				type = None
				if category_id == '1':
					type = 'DEM'
				if category_id == '2':
					type = 'Swath'
				if category_id == '3':
					type = 'Classified'
				html = render_to_string('noAggWuDeliverables.html', {'type':type})
				responseData['html'] = html		
			return JsonResponse(responseData)

## View for handling the creation of DEM, Swath, and Classified Deliverables
@qcr_user_authenticated			
def createAggregatedWuDeliverable(request, review_id, category_id):
	if request.is_ajax():
		if request.method == "POST":
			responseData = {}	
			delivDict = {}
			deliv = None
			jsonData = json.loads(request.body.decode('utf-8'))
			for key, value in jsonData.items():
				if key != "workUnits":
					delivDict[key] = value
			deliv = buildAggregatedWuDeliverable(category_id, delivDict)
			
			if deliv:
				if jsonData['workUnits'] != '':
					responseData = applyAggregatedWuDeliverable(jsonData['workUnits'], deliv)
				try:
					wus = deliv.workunit_set.all()
					wu = wus[0]
					vaReq = wu.vaRequirement
					collInfo = wu.collectionInfo
					vaData = None
					if vaReq:
						vaData = VaData.objects.get(vaRequirement = vaReq, category = deliv.category)
					
					if vaData:
						deliv.vaData = vaData
						deliv.save()
						
					if deliv.category.name == 'DEM':
						dem = DEM.objects.get(pk = deliv.id)
						dem.resolution = collInfo.demResolution
						dem.resolutionUnits = collInfo.demResolutionUnits
						dem.save()
						deliv = dem
						
						
				except:
					pass
				review = get_object_or_404(Review, pk = review_id)
				wus = WorkUnit.objects.filter(aggregatedWuDeliverable = deliv, review = review)
				returnTab = buildAggregatedWuDeliverableTab(wus, deliv)
				returnTabId = returnTab.id
				responseData['tabId'] = str(returnTabId)
				return JsonResponse(responseData)	

## View for handling the UI interactions of the indidual Aggregated WU Deliverable Tabs, handles building html based on
## category ID as well as generating initial error list, and displaying all required forms
@qcr_user_authenticated				
def aggregatedWuDeliverableTab(request, tab_id, review_id, category_id):
	vaRequirement = None
	if request.is_ajax():
		responseData = {}
		deliv = None
		tab = get_object_or_404(AggregatedWuDeliverableTab, pk = tab_id)
		if request.method == 'GET':
			deliv = tab.deliverable
			if category_id == '1':
				deliv = DEM.objects.get(pk = tab.deliverable.id)
				wu = WorkUnit.objects.get(vaRequirement = tab.vaRequirement, aggregatedWuDeliverable = deliv)
				try:
					collInfo = wu.collectionInfo
					deliv.resolution = collInfo.demResolution
					deliv.resolutionUnits = collInfo.demResolutionUnits
					deliv.save()
				except:
					pass
			elif category_id == '2':
				deliv = Swath.objects.get(pk = tab.deliverable.id)
			elif category_id == '3':
				deliv = Classified.objects.get(pk = tab.deliverable.id)
			wus = deliv.workunit_set.all()
			wu = wus[0]
			vaRequirement = wu.vaRequirement
		if request.method == 'POST':
			jsonData = json.loads(request.body.decode('utf-8'))
			deliv = tab.deliverable
			wus = deliv.workunit_set.all()
			wu = wus[0]
			vaRequirement = wu.vaRequirement
			## Break off the non-multiselect input data elements to build the DEM object.
			delivDict = {}
			for key, value in jsonData.items():
				if key != "workUnits":
					delivDict[key] = value
			## Update the DEM object with the incoming request data
			if delivDict != {}:
				if category_id == '1':
					dem = get_object_or_404(DEM, pk = deliv.id)
					dem = buildDem(delivDict, dem)
					deliv = AggregatedWuDeliverable.objects.get(pk = dem.id)
			
				if category_id == '2':
					swath = get_object_or_404(Swath, pk = deliv.id)
					swath = buildSwath(delivDict, swath)
					deliv = AggregatedWuDeliverable.objects.get(pk = swath.id)
					
				if category_id == '3':
					classified = get_object_or_404(Classified, pk = deliv.id)
					classified = buildClassified(delivDict, classified)
					deliv = AggregatedWuDeliverable.objects.get(pk = classified.id)			
			
			if jsonData['workUnits'] != '':
				applyAggregatedWuDeliverable(jsonData['workUnits'], deliv)
		review = get_object_or_404(Review, pk = review_id)
		freeWus = []
		if category_id == '1':
			freeWus = freeWorkUnitsSameVa(review, 'dem', vaRequirement)
		if category_id == '2':
			freeWus = freeWorkUnitsSameVa(review, 'swath', vaRequirement)
		if category_id == '3':
			freeWus = freeWorkUnitsSameVa(review, 'classified', vaRequirement)
		
		
		errors = list(Error.objects.filter(aggregatedWuDeliverable = deliv))
		errorTypes = ErrorType.objects.filter(aggDeliverableCategory__category = category_id)
		wuSameInfo = WorkUnit.objects.filter(aggregatedWuDeliverable = deliv)
		svaData = None
		svas = []
		try:
			qualityLevel = wu.qualityLevel
			wp = wu.workPackage
			projectSpec = wp.projectSpec
			projectSpecName = projectSpec.name
			try:
				svas = list(SuppVaMeasure.objects.filter(vaRequirement = vaRequirement))
				if svas == []:
					raise Exception()
				responseData['vaRequirement'] = 'True'
			except:
				responseData['vaRequirement'] = 'False'

			vaData = deliv.vaData
			svaIds = []
			for sva in svas:
				svaIds.append(sva.vaReqSvaId)
			suppReqs = []
			suppDatas = []
			for id in svaIds:
				sReq = SuppVaMeasure.objects.get(vaReqSvaId = id)
				suppReqs.append(sReq)
				try:
					sData = SuppVaResults.objects.get(vaData = vaData, sva = sReq)
					suppDatas.append(sData)
				except:
					suppDatas.append('')
			svaData = zip(suppReqs, suppDatas)
		except:
			pass

		tabHtml = ''
		if vaRequirement == None:
			tabHtml = buildAggWuTabHtmlNoVaReq(responseData, category_id, deliv, freeWus, wuSameInfo, errors, errorTypes, tab_id)
		elif vaRequirement != None and projectSpecName == 1.0:
			tabHtml = buildAggWuTabHtmlVaReqSpec10(vaRequirement, vaData, category_id, deliv, freeWus, wuSameInfo, errors, errorTypes, svaData, tab_id)
		elif vaRequirement != None and projectSpecName == 1.2:
			tabHtml = buildAggWuTabHtmlVaReqSpec12(vaRequirement, vaData, category_id, deliv, freeWus, wuSameInfo, errors, errorTypes, svaData, tab_id)

		if category_id == '1':
			responseData['success'] = 'DEM ' + str(deliv.id) + ' updated.'
		if category_id == '2':
			responseData['success'] = 'Swath ' + str(deliv.id) + ' updated.'
		if category_id == '3':
			responseData['success'] = 'Classified ' + str(deliv.id) + ' updated.'

		responseData['html'] = tabHtml
		return JsonResponse(responseData)						

## View for handling the deletion of an aggregated Work Unit
@qcr_user_authenticated		
def deleteAggregatedWuDeliverable(request, tab_id, category_id):
	if request.is_ajax():
		if request.method == "POST":
			tab = get_object_or_404(AggregatedWuDeliverableTab, pk = tab_id)
			deliv = tab.deliverable
			delivId = deliv.id
			deliv.delete()
			responseData = {}
			if category_id == '1':
				responseData['success'] = 'DEM ' + str(delivId) + ' deleted.';
			if category_id == '2':
				responseData['success'] = 'Swath ' + str(delivId) + ' deleted.';
			if category_id == '3':
				responseData['success'] = 'Classified ' + str(delivId) + ' deleted.';
			return JsonResponse(responseData)

## View for handling unlinking an Aggregated Deliverable from a Work Unit
@qcr_user_authenticated			
def removeDelivFromWu(request, workunit_id, category_id):
	if request.is_ajax():
		if request.method == "POST":
			workUnit = get_object_or_404(WorkUnit, pk = workunit_id)
			aggWuDelivs = workUnit.aggregatedWuDeliverable.all()
			if category_id == '1':
				for deliv in aggWuDelivs:
					if str(deliv.category.category) == '1':
						workUnit.aggregatedWuDeliverable.remove(deliv)
			if category_id == '2':
				for deliv in aggWuDelivs:
					if str(deliv.category.category) == '2':
						workUnit.aggregatedWuDeliverable.remove(deliv)		
			if category_id == '3':
				for deliv in aggWuDelivs:
					if str(deliv.category.category) == '3':
						workUnit.aggregatedWuDeliverable.remove(deliv)							
			delivWus = list(WorkUnit.objects.filter(aggregatedWuDeliverable = deliv))
			if delivWus == []:
				deliv.vaData.delete()
				deliv.delete()
			workUnit.save()	
			responseData = {}
			responseData['success'] = 'True';
			return JsonResponse(responseData)

## View for creating a new error based on the contents of the Add Error form
@qcr_user_authenticated
def addErrorAggregatedWuDeliv(request, tab_id):
	tab = get_object_or_404(AggregatedWuDeliverableTab, pk = tab_id)
	deliv = tab.deliverable
	if request.method == 'POST':
		responseData = {}
		error = None
		try:
			type = ErrorType.objects.get(name = request.POST.get("type"), aggDeliverableCategory__category = deliv.category.category)
			if request.POST.get("resolved") == 'true':
				error = Error.objects.create(aggregatedWuDeliverable = deliv, errorType = type, resolved = True)
				error.save()
			else:
				error = Error.objects.create(aggregatedWuDeliverable = deliv, errorType = type, resolved = False)
				error.save()
			error = buildError(request, error)
			error.save()
			responseData['success'] = 'True'
		except:
			responseData['success'] = 'False'
		finally:
			return JsonResponse(responseData)

## View for determining how many work units remain linked with the deliverable. If only one work unit remains, a warning
## flag is set to notify the user that the deliverable will be deleted if the final WU link is removed.
@qcr_user_authenticated
def checkRemainingWorkUnits(request, tab_id):			
	if request.is_ajax():
		if request.method == "GET":
			responseData = {}
			tab = get_object_or_404(AggregatedWuDeliverableTab, pk = tab_id)
			deliv = tab.deliverable
			wus = list(deliv.workunit_set.all())
			if len(wus) == 1:
				responseData['warn'] = 'True'
			else:
				responseData['warn'] = 'False'
			return JsonResponse(responseData)

## View for handling the deletion of the VA Table from an Aggregated WU Deliverable tab
@qcr_user_authenticated
def deleteDelivVaTable(request, tab_id):
	if request.is_ajax():
		responseData = {}
		if request.method == 'POST':
			tab = get_object_or_404(AggregatedWuDeliverableTab, pk = tab_id)
			deliv = tab.deliverable
			wus = deliv.workunit_set.all()
			wu = wus[0]
			vaData = deliv.vaData
			if vaData:
				vaData.delete()	
				deliv.vaData = None
				deliv.save()
			vaRequirement = wu.vaRequirement
			vaRequirement.delete()
			tab.vaRequirement = None
			tab.save()
			responseData['result'] = 'success'
			return JsonResponse(responseData)

## View that returns the VA Table associated with a given Deliverable Tab, used primarily for refershing the table after
## an update or a reset button is pressed
@qcr_user_authenticated
def getDelivVaTable(request, tab_id):
	tab = get_object_or_404(AggregatedWuDeliverableTab, pk = tab_id)
	deliv = tab.deliverable
	wus = deliv.workunit_set.all()
	wu = wus[0]
	vaData = deliv.vaData
	vaRequirement = wu.vaRequirement
	svas = SuppVaMeasure.objects.filter(vaRequirement = vaRequirement)
	svaIds = []
	for sva in svas:
		svaIds.append(sva.vaReqSvaId)
	suppReqs = []
	suppDatas = []
	for id in svaIds:
		sReq = SuppVaMeasure.objects.get(vaReqSvaId = id)
		suppReqs.append(sReq)
		try:
			sData = SuppVaResults.objects.get(vaData = vaData, sva = sReq)
			suppDatas.append(sData)
		except:
			suppDatas.append('')
	svaData = zip(suppReqs, suppDatas)
	vaTableHtml = ''
	projectSpec = wu.workPackage.projectSpec
	id = vaRequirement.id
	if projectSpec.name == 1.0:
		req10 = VaRequirement10.objects.get(pk = id)
		if vaData:
			vaData10 = VaData10.objects.get(pk = vaData.id)
			vaTableHtml = render_to_string('deliv_va_table.html', {'req10':True, 'vaReq':req10, 'vaResults':vaData10, 'svaData':svaData})
		else:
			vaTableHtml = render_to_string('deliv_va_table.html', {'req10':True, 'vaReq':req10, 'svaData':svaData})
	if projectSpec.name == 1.2:
		req12 = VaRequirement12.objects.get(pk = id)
		if vaData:
			vaData12 = VaData12.objects.get(pk = vaData.id)
			vaTableHtml = render_to_string('deliv_va_table.html', {'req12':True, 'vaReq':req12, 'vaResults':vaData12})
		else:
			vaTableHtml = render_to_string('deliv_va_table.html', {'req12':True, 'vaReq':req12})
	responseData = {}
	responseData['html'] = vaTableHtml
	return JsonResponse(responseData)

## View handling making updates to a tab's VA table based on the data retrieved from the VA form
@qcr_user_authenticated
def updateDelivVaTable(request, tab_id):
	if request.is_ajax():
		responseData = {}
		tab = get_object_or_404(AggregatedWuDeliverableTab, pk = tab_id)
		if request.method == 'POST':
			jsonData = json.loads(request.body.decode('utf-8'))
			deliv = tab.deliverable
			vaData = deliv.vaData
			deletes = [value for key, value in jsonData.items() if 'delete' in key.lower()]
			for delete in deletes[0]:
				sva = get_object_or_404(SuppVaMeasure, pk = delete)
				sva.delete()
			wus = deliv.workunit_set.all()
			wu = wus[0]
			vaRequirement = wu.vaRequirement
			projectSpec = wu.workPackage.projectSpec
			qualityLevel = wu.qualityLevel
			vaRequirement = buildVaRequirement(jsonData, projectSpec, qualityLevel, vaRequirement)
			
			if projectSpec.name == 1.0:
				svas = list(SuppVaMeasure.objects.filter(vaRequirement = vaRequirement))
				vaData = buildDelivVaData(deliv, vaRequirement, projectSpec, qualityLevel, jsonData, svas)
				suppReqs = []
				suppDatas = []
				for suppVa in svas:
					suppReqs.append(suppVa)
					try:
						sData = SuppVaResults.objects.get(vaData = vaData, sva = suppVa)
						suppDatas.append(sData)
					except:
						suppDatas.append('')
				svaData = zip(suppReqs, suppDatas)
			else:
				vaData = buildDelivVaData(deliv, vaRequirement, projectSpec, qualityLevel, jsonData)
			vaTableHtml = ''
			id = vaRequirement.id
			if projectSpec.name == 1.0:
				req10 = VaRequirement10.objects.get(pk = id)
				if vaData:
					vaData10 = VaData10.objects.get(pk = vaData.id)
					vaTableHtml = render_to_string('deliv_va_table.html', {'req10':True, 'vaReq':req10, 'vaResults':vaData10, 'svaData':svaData})
				else:
					vaTableHtml = render_to_string('deliv_va_table.html', {'req10':True, 'vaReq':req10, 'svaData':svaData})
			if projectSpec.name == 1.2:
				req12 = VaRequirement12.objects.get(pk = id)
				if vaData:
					vaData12 = VaData12.objects.get(pk = vaData.id)
					vaTableHtml = render_to_string('deliv_va_table.html', {'req12':True, 'vaReq':req12, 'vaResults':vaData12})
				else:
					vaTableHtml = render_to_string('deliv_va_table.html', {'req12':True, 'vaReq':req12})
			responseData['html'] = vaTableHtml
		return JsonResponse(responseData)

## View that returns the html template for the DEM Form
@qcr_user_authenticated		
def demForm(request, review_id):
	if request.is_ajax():
		if request.method == 'GET':
			bootstrapHeader = ''
			review = get_object_or_404(Review, pk = review_id)
			workUnits = freeWorkUnits(review, 'dem')
			formHtml = render_to_string('dem_form.html', {'initialWuList':workUnits})
			return HttpResponse(formHtml)	

## View that returns the html template for the Swath Form
@qcr_user_authenticated			
def swathForm(request, review_id):
	if request.is_ajax():
		if request.method == 'GET':
			bootstrapHeader = ''
			review = get_object_or_404(Review, pk=review_id)
			workUnits = freeWorkUnits(review, 'swath')
			formHtml = render_to_string('swath_form.html', {'initialWuList': workUnits})
			return HttpResponse(formHtml)

## View that returns the html template of the Classified Form
@qcr_user_authenticated			
def classifiedForm(request, review_id):
	if request.is_ajax():
		if request.method == 'GET':
			bootstrapHeader = ''
			review = get_object_or_404(Review, pk=review_id)
			workUnits = freeWorkUnits(review, 'classified')
			formHtml = render_to_string('classified_form.html', {'initialWuList': workUnits})
			return HttpResponse(formHtml)

## View that returns the classifications associated with a specified review's work package. Used primarily in refreshing
## the classifications table following an update or a reset.
@qcr_user_authenticated			
def getClassificationsTable(request, reviewId):
	review = get_object_or_404(Review, pk = reviewId)
	wus = WorkUnit.objects.filter(review = review)
	wu = wus[0]
	classifications = PointCloudClassification.objects.filter(workPackage = wu.workPackage).order_by('classificationId')
	responseData = {}
	responseData['html'] = render_to_string('classifications_table.html', {'classifications':classifications})
	return JsonResponse(responseData)

## View that iterates through all checked classifications and deletes classifications marked for removal in the table form.
@qcr_user_authenticated
def deleteClassifications(request):
	if request.is_ajax():
		if request.method == "POST":
			jsonData = json.loads((request.body.decode('utf-8')))
			ids = jsonData['deleteIds']
			for id in ids:
				classification = get_object_or_404(PointCloudClassification, pk = id)
				classification.delete()
			responseData = {}
			responseData['result'] = 'success'
			return JsonResponse(responseData)

## View for processing the input of a classifications table submission, and making necessary updates
@qcr_user_authenticated			
def updateClassifications(request, reviewId):
	if request.is_ajax():
		if request.method == "POST":
			responseData = {}
			jsonData = json.loads(request.body.decode('utf-8'))
			##Update Existing Classifications
			review = get_object_or_404(Review, pk=reviewId)
			wus = WorkUnit.objects.filter(review=review)
			wu = wus[0]
			wp = wu.workPackage
			classifications = PointCloudClassification.objects.filter(workPackage=wp).order_by('classificationId')
			for c in classifications:
				try:
					c.classificationId = jsonData['cID'+str(c.id)]
					c.classificationType = jsonData['cType'+str(c.id)]
					c.save()
				except:
					continue
			##Add New Classifications
			if jsonData['numNewRows']:
				for x in range(1,jsonData['numNewRows']+1):
					try:
						newClassification = PointCloudClassification.objects.create(classificationId=jsonData['newCID'+str(x)], classificationType=jsonData['newCType'+str(x)], workPackage=wp)
						newClassification.save()
					except:
						continue
			responseData['result'] = 'success'
			return JsonResponse(responseData)

###########################
## VA Requirements Views ##
###########################

## View for retrieving VA Requirement Subtabs
@qcr_user_authenticated
def vaReqSubtabs(request, review_id):
	if request.is_ajax():
		if request.method == 'GET':
			responseData = {}
			review = get_object_or_404(Review, pk=review_id)
			wus = WorkUnit.objects.filter(review=review)
			wu = wus[0]
			wp = wu.workPackage
			wus = WorkUnit.objects.filter(workPackage = wp)
			vaReqs = []
			vaReqs = getVARequirements(wus)
			vaReqIds = []
			for vaReq in vaReqs:
				vaReqIds.append(vaReq.id)
			if vaReqIds != []:
				minVal = min(sorted(vaReqIds))
				responseData['minVal'] = minVal
			freeWus = getVAFreeWus(wus)
			html = render_to_string('va_requirement_tabs.html', {'vaReqs':vaReqs, 'freeWus':freeWus})
			responseData['html'] = html
			return JsonResponse(responseData)

## View for adding new VA Requirement
@qcr_user_authenticated
def createVaReq(request, workunit_id):
	if request.is_ajax():
		if request.method == "POST":
			responseData = {}
			wu = get_object_or_404(WorkUnit, pk=workunit_id)
			wp = wu.workPackage
			spec = wp.projectSpec
			if str(spec.name) == "1.0":
				vaReq = VaRequirement10.objects.create()
				vaReq.save()
			elif str(spec.name) == "1.2":
				vaReq = VaRequirement12.objects.create()
				vaReq.save()
			wu.vaRequirement = vaReq
			wu.save()
			responseData['tabId'] = str(vaReq.id)
			return JsonResponse(responseData)

@qcr_user_authenticated
def addVaReqForm(request, review_id):
	if request.is_ajax():
		if request.method == 'GET':
			responseData = {}
			review = get_object_or_404(Review, pk=review_id)
			wus = WorkUnit.objects.filter(review=review)
			wu = wus[0]
			wus = WorkUnit.objects.filter(workPackage=wu.workPackage).exclude(collectionInfo__isnull=True)
			freeWus = getVAFreeWus(wus)
			formHtml = render_to_string('addVaReq_form.html', {'freeWus': freeWus})
			return HttpResponse(formHtml)

@qcr_user_authenticated
def getVaReqTab(request, vaReq_id):
	if request.is_ajax():
		if request.method == 'GET':
			responseData = {}
			vaReq = get_object_or_404(VaRequirement, pk = vaReq_id)
			req10 = False
			req12 = False
			linkedWus = WorkUnit.objects.filter(vaRequirement = vaReq)
			wu = linkedWus[0]
			wp = wu.workPackage
			spec = wp.projectSpec
			if str(spec.name) == '1.0':
				vaReq = get_object_or_404(VaRequirement10, pk = vaReq_id)
				req10 = True
			if str(spec.name) == '1.2':
				vaReq = get_object_or_404(VaRequirement12, pk = vaReq_id)
				req12 = True
			ci = wu.collectionInfo
			ql = ci.qualityLevel
			freeWus = WorkUnit.objects.filter(workPackage = wu.workPackage, vaRequirement = None, collectionInfo__qualityLevel = ql)
			formHtml = render_to_string('va_requirement_tab.html', {'wuList': freeWus, 'wuSameInfo': linkedWus, 'req10': req10, 'req12': req12, 'vaReq': vaReq})
			return HttpResponse(formHtml)

## View for retrieving the highest sva ID
@qcr_user_authenticated
def getNextSva(request):
	svas = SuppVaMeasure.objects.all()
	highId = 0
	for sva in svas:
		
		if sva.id > highId:
			highId = sva.id
	return JsonResponse({'svaId':highId})

## View for handling the creation of a new VA Table. Builds only the necessary VA fields based on project spec.
@qcr_user_authenticated	
def addVaTable(request, workUnit_id):
	if request.is_ajax():
		responseData = {}
		if request.method == 'POST':
			responseData = {}
			jsonData = json.loads(request.body.decode('utf-8'))
			wu = WorkUnit.objects.get(workUnitId = workUnit_id)
			wp = wu.workPackage
			projectSpec = wp.projectSpec
			ci = wu.collectionInfo
			ql = ci.qualityLevel
			vaRequirement = buildVaRequirement(jsonData, projectSpec, ql)
			ci.vaRequirement = vaRequirement
			ci.save()		
			cis = CollectionInfo.objects.filter(qualityLevel = ql)
			workUnits = []
			for ci in cis:
				try:
					wkUnit = WorkUnit.objects.get(collectionInfo = ci)
					if wkUnit.workPackage == wp:
						try:
							aggWuDelivs = wkUnit.aggregatedWuDeliverable.all()
							if aggWuDelivs != []:
								for aggWuDeliv in aggWuDelivs:
									try:
										tab = AggregatedWuDeliverableTab.objects.get(deliverable = aggWuDeliv)
										tab.vaRequirement = vaRequirement
										tab.save()
									except:
										tab = AggregatedWuDeliverableTab.objects.create(deliverable = aggWuDeliv, vaRequirement = vaRequirement)
										continue
						except:
							continue
				except:
					continue
			collInfo = wu.collectionInfo
			va = collInfo.vaRequirement
			vaTableHtml = ''
			if projectSpec.name == 1.0:
				va10 = VaRequirement10.objects.get(pk = vaRequirement.id)
				vaTableHtml = render_to_string('va_table.html',{'req10':True, 'vaReq':va10})
			if projectSpec.name == 1.2:
				va12 = VaRequirement12.objects.get(pk = vaRequirement.id)
				vaTableHtml = render_to_string('va_table.html',{'req12':True, 'vaReq':va12})
			responseData['html'] = vaTableHtml

			return JsonResponse(responseData)

## View that handles parsing the input of a submitted VA table form, and making necessary updates.
@qcr_user_authenticated			
def updateVaTable(request, vaReq_id):
	if request.is_ajax():
		responseData = {}
		if request.method == 'POST':
			jsonData = json.loads(request.body.decode('utf-8'))
			deletes = [value for key, value in jsonData.items() if 'delete' in key.lower()]
			for delete in deletes[0]:
				sva = get_object_or_404(SuppVaMeasure, pk = delete)
				sva.delete()
			vaRequirement = get_object_or_404(VaRequirement, pk = vaReq_id)
			linkedWus = WorkUnit.objects.filter(vaRequirement = vaRequirement)
			wu = linkedWus[0]
			wp = wu.workPackage
			projectSpec = wp.projectSpec
			qualityLevel = wu.qualityLevel
			vaRequirement = buildVaRequirement(jsonData, projectSpec, qualityLevel, vaRequirement)
			vaTableHtml = ''
			id = vaRequirement.id
			if projectSpec.name == 1.0:
				req10 = VaRequirement10.objects.get(pk = id)
				vaTableHtml = render_to_string('va_table.html',{'req10':True, 'vaReq':req10})
			if projectSpec.name == 1.2:
				req12 = VaRequirement12.objects.get(pk = id)
				vaTableHtml = render_to_string('va_table.html',{'req12':True, 'vaReq':req12})
			responseData['html'] = vaTableHtml
		return JsonResponse(responseData)

## View that handles the deletion of a specified VA Table
@qcr_user_authenticated		
def deleteVaTable(request, vaReq_id):
	if request.is_ajax():
		responseData = {}
		if request.method == 'POST':
			try:
				vaRequirement = get_object_or_404(VaRequirement, pk = vaReq_id)
				vaRequirement.delete()
				responseData['result'] = 'success'
				return JsonResponse(responseData)
			except:
				responseData['result'] = 'failure'
				return JsonResponse(responseData)

## View for retrieving an updated copy of the VA Table
@qcr_user_authenticated				
def getVaTable(request, vaReq_id):
	vaRequirement = get_object_or_404(VaRequirement, pk = vaReq_id)
	vaTableHtml = ''
	linkedWus = WorkUnit.objects.filter(vaRequirement = vaRequirement)
	wu = linkedWus[0]
	wp = wu.workPackage
	projectSpec = wp.projectSpec
	id = vaRequirement.id
	if projectSpec.name == 1.0:
		req10 = VaRequirement10.objects.get(pk = id)
		vaTableHtml = render_to_string('va_table.html', {'req10':True, 'vaReq':req10})
	if projectSpec.name == 1.2:
		req12 = VaRequirement12.objects.get(pk = id)
		vaTableHtml = render_to_string('va_table.html', {'req12':True, 'vaReq':req12})
	responseData = {}
	responseData['html'] = vaTableHtml
	return JsonResponse(responseData)

## View for linking WUs to a given VA Requirement
@qcr_user_authenticated
def linkVaWus(request, vaReq_id):
	if request.is_ajax():
		if request.method == 'POST':
			jsonData = json.loads(request.body.decode('utf-8'))
			vaReq = get_object_or_404(VaRequirement, pk = vaReq_id)
			workUnits = jsonData.split(',')
			wuNames = []
			if workUnits != []:
				for wu in workUnits:
					workUnit = None
					try:
						workUnit = WorkUnit.objects.get(pk=wu)
					except:
						workUnit = WorkUnit.objects.get(name=wu)
					wuNames.append(workUnit.name)
					workUnit.vaRequirement = vaReq
					workUnit.save()
			responseData = {}
			responseData['applied'] = wuNames
			responseData['result'] = 'success'
			return JsonResponse(responseData)

## View for checking remaining WUs linked to a given VA Requirement, returns warning if only one WU remains
@qcr_user_authenticated
def checkRemainingWuVA(request, vaReq_id):
	if request.is_ajax():
		if request.method == "GET":
			responseData = {}
			vaReq = get_object_or_404(VaRequirement, pk=vaReq_id)
			wus = WorkUnit.objects.filter(vaRequirement = vaReq)
			if len(wus) == 1:
				responseData['warn'] = 'True'
			else:
				responseData['warn'] = 'False'
			return JsonResponse(responseData)

def removeVaReq(request, workunit_id):
	if request.is_ajax():
		if request.method == "POST":
			responseData = {}
			wu = get_object_or_404(WorkUnit, pk = workunit_id)
			vaReq = wu.vaRequirement
			wu.vaRequirement = None
			wu.save()
			wus = WorkUnit.objects.filter(vaRequirement = vaReq)
			if (wus):
				return JsonResponse(responseData)
			else:
				vaReq.delete()
				return JsonResponse(responseData)

## View for checking whether a specific SVA ID already exists
@qcr_user_authenticated	
def svaExists(request, sva_id):
	responseData = {}
	try:
		SuppVaMeasure.objects.get(pk = sva_id)
		responseData['svaExists'] = 'True'
	except:
		responseData['svaExists'] = 'False'
	return JsonResponse(responseData)

###############################
## Supplemental view methods ##
###############################
def init():
    ##Check for default Project Spec values
    check = ProjectSpecification.objects.get_or_create(name=1.0)
    check = ProjectSpecification.objects.get_or_create(name=1.2)
    ##Check for default Quality Level values
    check = QualityLevel.objects.get_or_create(name="LiDAR QL0")
    check = QualityLevel.objects.get_or_create(name="LiDAR QL1")
    check = QualityLevel.objects.get_or_create(name="LiDAR QL2")
    check = QualityLevel.objects.get_or_create(name="LiDAR QL3")
    ##Check for default METADATA DeliverableCategory values
    check = DeliverableCategory.objects.get_or_create(category=1, name="Project-level XML Metadata")
    check = DeliverableCategory.objects.get_or_create(category=1, name="Swath LAS XML Metadata")
    check = DeliverableCategory.objects.get_or_create(category=1, name="Classified LAS XML Metadata")
    check = DeliverableCategory.objects.get_or_create(category=1, name="Breakline XML Metadata")
    check = DeliverableCategory.objects.get_or_create(category=1, name="BE DEM XML Metadata")
    check = DeliverableCategory.objects.get_or_create(category=1, name="Intensity Imagery XML Metadata")
    ##Check for default BREAKLINES DeliverableCategory values
    check = DeliverableCategory.objects.get_or_create(category=2, name="Polygon Breaklines")
    check = DeliverableCategory.objects.get_or_create(category=2, name="Polyline Breaklines")

    ##Check for default REPORTS DeliverableCategory values
    check = DeliverableCategory.objects.get_or_create(category=6, name="Vendor Acquisition Report")
    check = DeliverableCategory.objects.get_or_create(category=6, name="Vendor Project Report")
    check = DeliverableCategory.objects.get_or_create(category=6, name="Vendor QA Report")
    check = DeliverableCategory.objects.get_or_create(category=6, name="Vendor Data Accuracy Report")
    check = DeliverableCategory.objects.get_or_create(category=6, name="Project Tiling Scheme")
    check = DeliverableCategory.objects.get_or_create(category=6, name="Buffered Project Area Polygon")
    check = DeliverableCategory.objects.get_or_create(category=6, name="Ground Control Points")
    check = DeliverableCategory.objects.get_or_create(category=6, name="Independent Accuracy Checkpoints")
    ##Check for default OTHER DeliverableCategory values
    check = DeliverableCategory.objects.get_or_create(category=7, name="Intensity Imagery")
    check = DeliverableCategory.objects.get_or_create(category=7, name="Orthorectified Radar Intensity Imagery")
    check = DeliverableCategory.objects.get_or_create(category=7, name="Digital Surface Model")
    ##Check for default AGGREGATED WU DELIVERABLE category values
    check = AggregatedWuDeliverableCategory.objects.get_or_create(category=1, name='DEM')
    check = AggregatedWuDeliverableCategory.objects.get_or_create(category=2, name='Unclassified Swath')
    check = AggregatedWuDeliverableCategory.objects.get_or_create(category=3, name='Classified Pointcloud')
    ##Check for ErrorType values
    ##Check for Reports And Shapefiles ErrorTypes
    category = DeliverableCategory.objects.get(name="Vendor Acquisition Report")
    check = ErrorType.objects.get_or_create(name="Failed Parser", deliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Content Inaccurate", deliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Missing Tag", deliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Reports Missing", deliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Reports Inaccurate", deliverableCategory=category)
    ##Check for Metadata ErrorTypes
    category = DeliverableCategory.objects.get(name="Project-level XML Metadata")
    check = ErrorType.objects.get_or_create(name="Failed Parser", deliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Content Inaccurate", deliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Missing Tag", deliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Reports Missing", deliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Reports Inaccurate", deliverableCategory=category)
    ##Check for Other ErrorTypes
    category = DeliverableCategory.objects.get(name="Intensity Imagery")
    check = ErrorType.objects.get_or_create(name="Failed Parser", deliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Content Inaccurate", deliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Missing Tag", deliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Reports Missing", deliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Reports Inaccurate", deliverableCategory=category)
    ##Check for Breaklines ErrorTypes
    category = DeliverableCategory.objects.get(name="Polygon Breaklines")
    check = ErrorType.objects.get_or_create(name="Breaklines Not 3D", deliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Breakline Geometry Error", deliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Missing Feature", deliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Adjust Monotonicity", deliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Spatial Reference/Units", deliverableCategory=category)
    ##Check for DEM ErrorTypes
    category = AggregatedWuDeliverableCategory.objects.get(category=1)
    check = ErrorType.objects.get_or_create(name="Bridge Saddle", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="DEM Void", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Edge Artifact", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Tile Mismatch", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Raster Format", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Spatial Reference/Units", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="DEM Properties", aggDeliverableCategory=category)
    ##Check for Swath Unclassified ErrorTypes
    category = AggregatedWuDeliverableCategory.objects.get(category=2)
    check = ErrorType.objects.get_or_create(name="Point/Header Mismatch", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Density Deviation", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="LAS Version", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Point Misclassification", aggDeliverableCategory=category)
    ##Check for Misclassification Error Subtypes
    errorType = ErrorType.objects.get(name="Point Misclassification", aggDeliverableCategory=category)
    check = ErrorSubtype.objects.get_or_create(name="Unclassified", errorType=errorType)
    check = ErrorType.objects.get_or_create(name="Point Source IDs", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="File Source ID", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Intensity", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="GPS Time", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Edge of Flightline Scan Not Set", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Scan Direction Flag Not Set", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Scan Angle Error", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Insufficient Points", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Set Overlap", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Tiles Do Not Match Tiling Scheme", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Global Encoder", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="PDR Format Incorrect", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="PDR Points Incorrect", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Scale Factor XYZ", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Offset XYZ", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Generating Software", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="File Creation", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Bounding Box Incorrect", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Return of Zero", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="EVLR", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="VLR", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Spatial Reference/Units", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Well Known Text", aggDeliverableCategory=category)
    ##Check for Classified ErrorTypes
    category = AggregatedWuDeliverableCategory.objects.get(category=3)
    check = ErrorType.objects.get_or_create(name="Point/Header Mismatch", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Density Deviation", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="LAS Version", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Point Misclassification", aggDeliverableCategory=category)
    ##Check for Misclassification Error Subtypes
    errorType = ErrorType.objects.get(name="Point Misclassification", aggDeliverableCategory=category)
    check = ErrorSubtype.objects.get_or_create(name="Ground", errorType=errorType)
    check = ErrorSubtype.objects.get_or_create(name="Ignored Ground/Buffer", errorType=errorType)
    check = ErrorSubtype.objects.get_or_create(name="High Noise", errorType=errorType)
    check = ErrorSubtype.objects.get_or_create(name="Low Noise", errorType=errorType)
    check = ErrorSubtype.objects.get_or_create(name="Low Vegetation", errorType=errorType)
    check = ErrorSubtype.objects.get_or_create(name="Medium Vegetation", errorType=errorType)
    check = ErrorSubtype.objects.get_or_create(name="High Vegetation", errorType=errorType)
    check = ErrorSubtype.objects.get_or_create(name="Water", errorType=errorType)
    check = ErrorSubtype.objects.get_or_create(name="Building", errorType=errorType)
    check = ErrorSubtype.objects.get_or_create(name="Unclassified", errorType=errorType)
    check = ErrorType.objects.get_or_create(name="Point Source IDs", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Intensity", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="GPS Time", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Edge of Flightline Scan Not Set", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Scan Direction Flag Not Set", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Scan Angle Error", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Set Overlap", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Tiles Do Not Match Tiling Scheme", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Global Encoder", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="PDR Format Incorrect", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="PDR Points Incorrect", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Scale Factor XYZ", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Offset XYZ", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Generating Software", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="File Creation", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Bounding Box Incorrect", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Return of Zero", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="EVLR", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="VLR", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Spatial Reference/Units", aggDeliverableCategory=category)
    check = ErrorType.objects.get_or_create(name="Well Known Text", aggDeliverableCategory=category)
    check = ChecklistCategory.objects.get_or_create(name='Collection Information')
    check = ChecklistCategory.objects.get_or_create(name='Metadata')
    check = ChecklistCategory.objects.get_or_create(name='Raw LPC')
    check = ChecklistCategory.objects.get_or_create(name='Classified LPC')
    check = ChecklistCategory.objects.get_or_create(name='DEM')
    check = ChecklistCategory.objects.get_or_create(name='Breaklines')
    check = ChecklistCategory.objects.get_or_create(name='Vertical Accuracy')
    check = ChecklistCategory.objects.get_or_create(name='Other')
    check = None

def addDefaultClassifications(wp):
	try:
		PointCloudClassification.objects.create(classificationId="1", classificationType="Processed, But Unclassified", workPackage=wp)
		PointCloudClassification.objects.create(classificationId="2", classificationType="Bare Earth", workPackage=wp)
		PointCloudClassification.objects.create(classificationId="7", classificationType="Low Noise", workPackage=wp)
		PointCloudClassification.objects.create(classificationId="9", classificationType="Water", workPackage=wp)
		PointCloudClassification.objects.create(classificationId="10", classificationType="Ignored Ground", workPackage=wp)
		PointCloudClassification.objects.create(classificationId="17", classificationType="Bridge Decks", workPackage=wp)
		PointCloudClassification.objects.create(classificationId="18", classificationType="High Noise", workPackage=wp)
	except:
		return

def recurseWorkUnitIds(randomWuId, existingWus):
	for wu in existingWus:
		if wu.workUnitId == randomWuId:
			randomWuId = random.randint(100000, 9999999)
			recurseWorkUnitIds(randomWuId, existingWus)
	return randomWuId
	
def convertDateTime(dateTimeString):
	removeExtraneous = dateTimeString.split('+')[0]
	dateTimeList = removeExtraneous.split(' ')
	date = dateTimeList[0]
	dateList = date.split('-')
	year = dateList[0]
	month = dateList[1]
	day = dateList[2]
	formattedDate = month + '/' + day + '/' + year
	time = dateTimeList[1]
	timeList = time.split(':')
	hour = timeList[0]
	min = timeList[1]
	amPm = 'AM'
	hour = int(hour)
	if hour >= 12:
		if hour > 12:
			hour = hour - 12
		amPm = 'PM'
	if hour == '00':
		hour = '12'
	
	formattedTime = str(hour) + ':' + min + ' ' + amPm
	formattedDateTime = formattedDate + ' ' + formattedTime
	return formattedDateTime	

def applyCollectionInfo(jsonData, collectionInfo, workUnit_id):
	reqWus = jsonData["workUnits"]
	workUnits = []
	if reqWus != '':
		reqWusNames = []
		workUnits = reqWus.split(',')
		if workUnits != []:
			for wu in workUnits:
				workUnit = WorkUnit.objects.get(pk = wu)
				workUnit.collectionInfo = collectionInfo
				workUnit.qualityLevel = collectionInfo.qualityLevel
				workUnit.save()
				reqWusNames.append(workUnit.name) 
	responseData = {}
	initWu = WorkUnit.objects.get(pk = workUnit_id)
	initWu.qualityLevel = collectionInfo.qualityLevel
	initWu.save()
	if reqWus != '':
		responseData['applied'] = str(reqWusNames).strip("[]").strip("'") + ',' + str(initWu.name)
	else:
		responseData['applied'] = str(initWu.name)
	return responseData

def buildDeliverableWUSelect(review_id = None, workunit_id = None):
	html  = '<label for = "#wuDelivMultiSelect">Link Deliverable to the Following Work Units: </label>'
	html += '<br><select id = "wuDelivMultiSelect" multiple = "multiple">'
	optionValues = ''	
	if workunit_id:
		currentWU = get_object_or_404(WorkUnit, pk = workunit_id)
		currentReview = get_object_or_404(Review, pk = currentWU.review.pk)
		wuList = WorkUnit.objects.filter(review = currentReview)	
		for unit in wuList:
			if str(unit.workUnitId) != str(workunit_id):
				optionValues += '<option value = "Work Unit ' + str(unit.workUnitId) + '">' + str(unit.name) + '</option>'
	else:
		review = get_object_or_404(Review, pk = review_id)
		wuList = WorkUnit.objects.filter(review = review)
		for unit in wuList:
			optionValues += '<option value = "Work Unit ' + str(unit.workUnitId) + '">' + str(unit.name) + '</option>'
	if optionValues != '':
		html += optionValues + '<select><br><br>'
	else:
		html = ''
	return html
	
def buildCollInfoMultiSelect(workunit_id):				
	multiSelectLabelHtml = '<label for = "#wuCiMultiSelect">Apply Collection Info to the Following Work Units: </label>'
	multiSelectHtmlHeader = '<br><select id = "wuCiMultiSelect" multiple = "multiple">'
	optionValues = ''

def freeWorkUnits(review, type, workunit_id = None):
	workUnit = None
	if workunit_id:
		workUnit = get_object_or_404(WorkUnit, pk = workunit_id)
	wus = list(WorkUnit.objects.filter(review = review))
	freeWorkUnitList = []
	for wu in wus:
		if type == 'collectionInfo':
			if wu.collectionInfo == None:
				freeWorkUnitList.append(wu)
		aggWuDelivs = wu.aggregatedWuDeliverable.all()
		wuDelivTypes = []
		if aggWuDelivs != []:
			for deliv in aggWuDelivs:
				wuDelivTypes.append(deliv.category.category)
		if type == 'dem':
			if not 1 in wuDelivTypes:
				freeWorkUnitList.append(wu)
		if type == 'swath':
			if not 2 in wuDelivTypes:
				freeWorkUnitList.append(wu)
		if type == 'classified':
			if not 3 in wuDelivTypes:
				freeWorkUnitList.append(wu)
	returnIdName = {}	
	if workunit_id:
		for unit in freeWorkUnitList:
			if str(unit.workUnitId) != str(workunit_id):
				returnIdName[unit.workUnitId] = unit.name
	else:
		for unit in freeWorkUnitList:
			returnIdName[unit.workUnitId] = unit.name
	return returnIdName	

def freeWorkUnitsSameVa(review, type, vaRequirement):
	wus = list(WorkUnit.objects.filter(review = review))
	freeWorkUnitList = []
	for wu in wus:
		aggWuDelivs = wu.aggregatedWuDeliverable.all()
		wuDelivTypes = []
		if aggWuDelivs != []:
			for deliv in aggWuDelivs:
				if deliv.category.category == 1:
					wuDelivTypes.append('dem')
				if deliv.category.category == 2:
					wuDelivTypes.append('swath')
				if deliv.category.category == 3:
					wuDelivTypes.append('classified')
		if type not in wuDelivTypes:
			try:
				vaReq = wu.vaRequirement
				if vaReq == vaRequirement:
					freeWorkUnitList.append(wu)
				else:
					raise Exception()
			except:
				continue	
	return freeWorkUnitList
	
def buildWorkPackage(jsonData, workPackage):
	if jsonData["name"] != '':
		workPackage.name = jsonData["name"]
	if jsonData["description"] != '':
		workPackage.description = jsonData["description"]
	if jsonData["type"] != '':	
		workPackage.type = jsonData["type"]	
	if jsonData["vendor"] != '':
		workPackage.vendor = jsonData["vendor"]
	if jsonData["poc"] != '':	
		workPackage.poc = jsonData["poc"]		
	if jsonData["pocEmail"] != '':
		workPackage.pocEmail = jsonData["pocEmail"]
	if jsonData["projectSpec"] != '':
		workPackage.projectSpec = ProjectSpecification.objects.get(name = float(jsonData["projectSpec"]))				
	if jsonData["restrictions"] == 'False':
		workPackage.restrictions = False
	elif jsonData["restrictions"] == 'True':
		workPackage.restrictions = True
	if jsonData["restrictionsDate"] != '':
		workPackage.restrictionsDate = jsonData["restrictionsDate"]
	if jsonData["restrictionsLayer"] == 'False':
		workPackage.restrictionsLayer = False
	elif jsonData["restrictionsLayer"] == 'True':
		workPackage.restrictionsLayer = True
	if jsonData["thirdPartyQa"] == 'False':
		workPackage.thirdPartyQa = False
	elif jsonData["thirdPartyQa"] == 'True':
		workPackage.thirdPartyQa = True
	if jsonData["thirdPartyQaBy"] != '':
		workPackage.thirdPartyQaBy = jsonData["thirdPartyQaBy"]
	if jsonData["receivedDate"] != '':
		workPackage.receivedDate = jsonData["receivedDate"]
	if jsonData["assignedDate"] != '':
		workPackage.assignedDate = jsonData["assignedDate"]
	workPackage.save()
	return workPackage

def buildWorkPackageContext(workPackage, method):
	workPackageContext = {}
	restDate = str(workPackage.restrictionsDate)
	try:
		dateArray = restDate.split('-')
		year = dateArray[0]
		month = dateArray[1]
		day = dateArray[2]
		newDate = month + '/' + day + '/' + year
		workPackageContext['restrictionsDate'] = newDate
	except:
		workPackageContext['restrictionsDate'] = None
	recdDate = str(workPackage.receivedDate)	
	try:
		dateArray = recdDate.split('-')
		year = dateArray[0]
		month = dateArray[1]
		day = dateArray[2]
		newDate = month + '/' + day + '/' + year
		workPackageContext['receivedDate'] = newDate
	except:
		workPackageContext['receivedDate'] = None
	assDate = str(workPackage.assignedDate)
	try:
		dateArray = assDate.split('-')
		year = dateArray[0]
		month = dateArray[1]
		day = dateArray[2]
		newDate = month + '/' + day + '/' + year
		workPackageContext['assignedDate'] = newDate
	except:
		workPackageContext['assignedDate'] = None	
	workPackageContext['workPackageId'] = workPackage.workPackageId
	workPackageContext['name'] = workPackage.name
	workPackageContext['description'] = workPackage.description
	workPackageContext['type'] = workPackage.type
	workPackageContext['vendor'] = workPackage.vendor
	workPackageContext['poc'] = workPackage.poc
	workPackageContext['pocEmail'] = workPackage.pocEmail
	projectSpec = workPackage.projectSpec
	workPackageContext['projectSpec'] = str(projectSpec.name)
	workPackageContext['restrictions'] = str(workPackage.restrictions)
	workPackageContext['restrictionsLayer'] = str(workPackage.restrictionsLayer)
	workPackageContext['thirdPartyQa'] = str(workPackage.thirdPartyQa)
	workPackageContext['thirdPartyQaBy'] = workPackage.thirdPartyQaBy
	return workPackageContext
	
def buildCollectionInfoObject(jsonData, collectionInfo):

	if jsonData["areaExtent"] == '':
		collectionInfo.areaExtent = None
	else:
		collectionInfo.areaExtent = jsonData["areaExtent"]
		
	if jsonData["collStart"] == '':
		collectionInfo.collectionStart = None
	else:
		collectionInfo.collectionStart = jsonData["collStart"]
		
	if jsonData["collEnd"] == '':
		collectionInfo.collectionEnd = None
	else:
		collectionInfo.collectionEnd = jsonData["collEnd"]
		
	if jsonData["tileSize"] == '':
		collectionInfo.tileSize = None
	else:
		collectionInfo.tileSize = jsonData["tileSize"]
		
	if jsonData["tsUnits"] == '':
		collectionInfo.tileSizeUnits = None
	else:
		collectionInfo.tileSizeUnits = jsonData["tsUnits"]
		
	if jsonData["demRes"] == '':
		collectionInfo.demResolution = None
	else:
		collectionInfo.demResolution = jsonData["demRes"]
		
	if jsonData["demResUnits"] == '':
		collectionInfo.demResolutionUnits = None
	else:
		collectionInfo.demResolutionUnits = jsonData["demResUnits"]
		
	if jsonData["horSrs"] == '':
		collectionInfo.horizontalSpatRef = None
	else:
		collectionInfo.horizontalSpatRef = jsonData["horSrs"]

	if jsonData["horEpsg"] == '':
		collectionInfo.horizontalEpsg = None
	else:
		collectionInfo.horizontalEpsg = jsonData["horEpsg"]	
		
	if jsonData["vertSrs"] == '':
		collectionInfo.verticalSpatRef = None
	else:
		collectionInfo.verticalSpatRef = jsonData["vertSrs"]
	
	if jsonData["vertEpsg"] == '':
		collectionInfo.verticalEpsg = None
	else:
		collectionInfo.verticalEpsg = jsonData["vertEpsg"]	
	
	if jsonData["qualLevel"] == '':
		collectionInfo.qualityLevel = None
	else:
		ql = QualityLevel.objects.get(name = jsonData['qualLevel'])
		collectionInfo.qualityLevel = ql
	if jsonData["lasVersion"] == '':
		collectionInfo.lasVersion = None
	else:
		collectionInfo.lasVersion = jsonData["lasVersion"]
		
	if jsonData["configNps"] == '':
		collectionInfo.configuredNps = None
	else:
		collectionInfo.configuredNps = jsonData["configNps"]
		
	if jsonData["configNpsUnits"] == '':
		collectionInfo.configNpsUnits = None
	else:
		collectionInfo.configNpsUnits = jsonData["configNpsUnits"]
		
	if jsonData["configAnps"] == '':
		collectionInfo.configuredAnps = None
	else:
		collectionInfo.configuredAnps = jsonData["configAnps"]
		
	if jsonData["configAnpsUnits"] == '':
		collectionInfo.configAnpsUnits = None
	else:
		collectionInfo.configAnpsUnits = jsonData["configAnpsUnits"]
		
	if jsonData["configAnpsMethod"] == '':
		collectionInfo.configAnpsMethod = None
	else:
		collectionInfo.configAnpsMethod = jsonData["configAnpsMethod"]
	if jsonData["hydroTreatment"] == '':
		collectionInfo.hydroTreatment = None
	else:
		collectionInfo.hydroTreatment = jsonData["hydroTreatment"]
	if jsonData["sensorType"] == '':
		collectionInfo.sensorType = None
	else:
		st = SensorType.objects.get(name = jsonData['sensorType'])
		collectionInfo.sensorType = st
	if jsonData["sensorUsed"] == '':
		collectionInfo.sensorUsed = None
	else:
		su = SensorUsed.objects.get(name = jsonData['sensorUsed'])
		collectionInfo.sensorUsed = su
		
	if jsonData["scanAngle"] == '':
		collectionInfo.configScanAngle = None
	else:
		collectionInfo.configScanAngle = jsonData["scanAngle"]
		
	collectionInfo.save()
	return collectionInfo
	
def buildDeliverableObject(jsonData, workunit_id = None):
	category = jsonData['deliverableCategory']
	deliverable = None
	if category == 'DEM' or category == 'Unclassified Swath' or category == 'Classified Pointcloud':
		catObject = None
		if category == 'DEM':
			catObject = AggregatedWuDeliverableCategory.objects.get(category = 1)
			deliverable = DEM.objects.create(category = catObject)
		if category == 'Unclassified Swath':
			catObject = AggregatedWuDeliverableCategory.objects.get(category = 2)
			deliverable = Swath.objects.create(category = catObject)
		if category == 'Classified Pointcloud':
			catObject = AggregatedWuDeliverableCategory.objects.get(category = 3)
			deliverable = Classified.objects.create(category = catObject)

		if workunit_id:
			wu = get_object_or_404(WorkUnit, pk = workunit_id)
			wu.aggregatedWuDeliverable.add(deliverable)
			wu.save()
	else:
		catObject = DeliverableCategory.objects.get(name = str(jsonData['deliverableCategory']))
		deliverable = Deliverable.objects.create(deliverableCategory = catObject)
		try:
			if jsonData["comment"] == '':
				deliverable.comment = None
			else:
				deliverable.comment = jsonData["comment"]
		except:
			pass
		if workunit_id:
			wu = get_object_or_404(WorkUnit, pk = workunit_id)
			wu.deliverable_set.add(deliverable)
			wu.save()
	
	if jsonData["description"] == '':
		deliverable.description = None
	else:
		deliverable.description = jsonData["description"]
	if jsonData["quantity"] == '':
		deliverable.quantity = None
	else:
		deliverable.quantity = jsonData["quantity"]
	if jsonData["spatRef"] == '':
		deliverable.spatialReference = None
	else:
		deliverable.spatialReference = jsonData["spatRef"]	
	if jsonData["reqPerContract"] == '':
		deliverable.reqPerContract = None
	elif jsonData["reqPerContract"] == 'false':
		deliverable.reqPerContract = False
	elif jsonData["reqPerContract"] == 'true':
		deliverable.reqPerContract = True
	
	if jsonData["reqPerSpec"] == '':
		deliverable.reqPerSpec = None
	elif jsonData["reqPerSpec"] == 'false':
		deliverable.reqPerSpec = False
	elif jsonData["reqPerSpec"] == 'true':
		deliverable.reqPerSpec = True
		
	if jsonData["delivered"] == '':
		deliverable.delivered = None
	elif jsonData["delivered"] == 'false':
		deliverable.delivered = False
	elif jsonData["delivered"] == 'true':
		deliverable.delivered = True	
	if jsonData["accepted"] == '':
		deliverable.accepted = None
	elif jsonData["accepted"] == 'false':
		deliverable.accepted = False
	elif jsonData["accepted"] == 'true':
		deliverable.accepted = True
	
	deliverable.save()
	
	
	
	
	return deliverable
	
def buildCollectionInfoJsonResponse(collectionInfo):
	if collectionInfo.collectionStart:
		collStart = convertDateTime(str(collectionInfo.collectionStart))
	else:
		collStart = None
	if collectionInfo.collectionEnd:
		collEnd = convertDateTime(str(collectionInfo.collectionEnd))
	else:
		collEnd = None
	responseCollInfo = {}
	responseCollInfo["areaExtent"] = str(collectionInfo.areaExtent)
	responseCollInfo["collStart"] = collStart
	responseCollInfo["collEnd"] = collEnd	
	responseCollInfo["tileSize"] = str(collectionInfo.tileSize)
	responseCollInfo["tsUnits"] = str(collectionInfo.tileSizeUnits)
	responseCollInfo["demRes"] = str(collectionInfo.demResolution)
	responseCollInfo["demResUnits"] = str(collectionInfo.demResolutionUnits)
	responseCollInfo["horSrs"] = str(collectionInfo.horizontalSpatRef)
	responseCollInfo["horEpsg"] = str(collectionInfo.horizontalEpsg)
	responseCollInfo["vertSrs"] = str(collectionInfo.verticalSpatRef)
	responseCollInfo["vertEpsg"] = str(collectionInfo.verticalEpsg)
	ql = collectionInfo.qualityLevel
	responseCollInfo["qualLevel"] = ql.name
	responseCollInfo["lasVersion"] = str(collectionInfo.lasVersion)
	responseCollInfo["configNps"] = str(collectionInfo.configuredNps)
	responseCollInfo["configNpsUnits"] = str(collectionInfo.configNpsUnits)
	responseCollInfo["configAnps"] = str(collectionInfo.configuredAnps)
	responseCollInfo["configAnpsUnits"] = str(collectionInfo.configAnpsUnits)
	responseCollInfo["configAnpsMethod"] = str(collectionInfo.configAnpsMethod)
	responseCollInfo['hydroTreatment'] = str(collectionInfo.hydroTreatment)
	responseCollInfo["sensorType"] = str(collectionInfo.sensorType)
	responseCollInfo["sensorUsed"] = str(collectionInfo.sensorUsed)
	responseCollInfo["scanAngle"] = str(collectionInfo.configScanAngle)
	return responseCollInfo

def buildVaRequirement(jsonData, projectSpec, qualityLevel, vaRequirement = None):
	if projectSpec.name == 1.0:
		if vaRequirement == None:
			vaRequirement = VaRequirement10.objects.create(projectSpec = projectSpec, qualityLevel = qualityLevel)
		else:
			vaRequirement.__class__ = VaRequirement10
		vaRequirement.fundamentalVaChkpt = jsonData['fundChkpt']
		vaRequirement.consolidatedVaChkpt = jsonData['consChkpt']
		vaRequirement.fundamentalVaValue = jsonData['fundVal']
		vaRequirement.consolidatedVaValue = jsonData['consVal']
		## Section badly needs lambdas
		svaIds = jsonData['svaIds']
		if svaIds != []:
			for id in svaIds:
				landcover = ''
				checkpoints = ''
				val = ''
				for key, value in jsonData.items():
					if 'Landcover' in key and str(id) in key and not 'rep' in key and not 'test' in key:
						landcover = jsonData[key]
					if 'Chkpts' in key and str(id) in key and not 'rep' in key and not 'test' in key:
						checkpoints = jsonData[key]
					if 'Val' in key and str(id) in key and not 'rep' in key and not 'test' in key:
						val = jsonData[key]
				if landcover == '' and checkpoints == '' and val == '':
					return
				else:
					try:
						sva = SuppVaMeasure.objects.get(pk = id)
					except:
						req10 = VaRequirement10.objects.get(id = vaRequirement.id)
						sva = SuppVaMeasure.objects.create(vaReqSvaId = id, vaRequirement = req10)
					sva.landcover = landcover
					sva.reqChkpts = checkpoints
					sva.reqVal = val
					sva.save()
	elif projectSpec.name == 1.2:
		if vaRequirement == None:
			vaRequirement = VaRequirement12(projectSpec = projectSpec, qualityLevel = qualityLevel)
		else:
			vaRequirement.__class__ = VaRequirement12
		vaRequirement.vegetatedVaChkpt = jsonData['vegChkpt']
		vaRequirement.nonvegetatedVaChkpt = jsonData['nonvegChkpt']
		vaRequirement.vegetatedVaValue = jsonData['vegVal']
		vaRequirement.nonvegetatedVaValue = jsonData['nonvegVal']
	vaRequirement.save()
	return vaRequirement

def buildError(request, error):
	if request.POST.get("subtype") != '':
		subtype = ErrorSubtype.objects.get(name=request.POST.get("subtype"), errorType = error.errorType)
		error.errorSubtype = subtype
	if request.POST.get("description") != '':
		error.description = request.POST.get("description")
	if request.POST.get('loc') != '':
		error.location = request.POST.get("loc") 
	if request.FILES:
		if request.FILES["image"]:
			file = request.FILES["image"]
			errImg = ErrorImage.objects.create(picture = file, error = error)
			errImg.save()
	error.save()
	return error

def buildDem(jsonData, dem):
	if jsonData["description"] !='':
		dem.description =jsonData["description"]
	if jsonData["quantity"] !='':
		dem.quantity =jsonData["quantity"]
	if jsonData["spatRef"] !='':
		dem.spatialReference =jsonData["spatRef"]
	if jsonData["reqPerContract"] !='':
		if jsonData["reqPerContract"] == 'true':
			dem.reqPerContract = True
		else:
			dem.reqPerContract = False
	if jsonData["reqPerSpec"] !='':
		if jsonData["reqPerSpec"] == 'true':
			dem.reqPerSpec = True
		else:
			dem.reqPerSpec = False
	if jsonData["pixelType"] != '':
		dem.pixelType = jsonData["pixelType"]
	if jsonData["interpolation"] != '':
		dem.interpolation = jsonData["interpolation"]	
	if jsonData["delivered"] !='':
		if jsonData["delivered"] == 'true':
			dem.delivered = True
		else:
			dem.delivered = False
	if jsonData["accepted"] !='':
		if jsonData["accepted"] == 'true':
			dem.accepted = True
		else:
			dem.accepted = False
	dem.save()
	return dem

def buildSwath(jsonData, swath):
	if jsonData["description"] !='':
		swath.description =jsonData["description"]
	if jsonData["quantity"] !='':
		swath.quantity =jsonData["quantity"]
	if jsonData["spatRef"] !='':
		swath.spatialReference =jsonData["spatRef"]
	if jsonData["reqPerContract"] !='':
		if jsonData["reqPerContract"] == 'true':
			swath.reqPerContract = True
		else:
			swath.reqPerContract = False
	if jsonData["reqPerSpec"] !='':
		if jsonData["reqPerSpec"] == 'true':
			swath.reqPerSpec = True
		else:
			swath.reqPerSpec = False
	if jsonData["swathPCVS"] != '':
		swath.swathPCVs = jsonData["swathPCVS"]
	if jsonData["prdf"] != '':
		swath.pointRecDataFormat = jsonData["prdf"]
	if jsonData["requiredInterswath"] != '':
		swath.requiredInterswath = jsonData["requiredInterswath"]
	if jsonData["recordedInterswath"] != '':
		swath.recordedInterswath = jsonData["recordedInterswath"]
	if jsonData["testedInterswath"] != '':
		swath.testedInterswath = jsonData["testedInterswath"]
	if jsonData["delivered"] !='':
		if jsonData["delivered"] == 'true':
			swath.delivered = True
		else:
			swath.delivered = False
	if jsonData["accepted"] !='':
		if jsonData["accepted"] == 'true':
			swath.accepted = True
		else:
			swath.accepted = False
	swath.save()
	return swath

def buildClassified(jsonData, classified):
	if jsonData["description"] !='':
		classified.description =jsonData["description"]
	if jsonData["quantity"] !='':
		classified.quantity =jsonData["quantity"]
	if jsonData["spatRef"] !='':
		classified.spatialReference =jsonData["spatRef"]
	if jsonData["reqPerContract"] !='':
		if jsonData["reqPerContract"] == 'true':
			classified.reqPerContract = True
		else:
			classified.reqPerContract = False
	if jsonData["reqPerSpec"] !='':
		if jsonData["reqPerSpec"] == 'true':
			classified.reqPerSpec = True
		else:
			classified.reqPerSpec = False
	if jsonData["classPCVS"] != '':
		classified.classPCVs = jsonData["classPCVS"]
	if jsonData["prdf"] != '':
		classified.pointRecDataFormat = jsonData["prdf"]
	if jsonData["delivered"] !='':
		if jsonData["delivered"] == 'true':
			classified.delivered = True
		else:
			classified.delivered = False
	if jsonData["accepted"] !='':
		if jsonData["accepted"] == 'true':
			classified.accepted = True
		else:
			classified.accepted = False
	classified.save()
	return classified

def applyAggregatedWuDeliverable(reqWus, deliverable):
	workUnits = reqWus.split(',')
	wuNames = []
	if workUnits != []:
		for wu in workUnits:
			workUnit = None
			try:
				workUnit = WorkUnit.objects.get(pk = wu)
			except:
				workUnit = WorkUnit.objects.get(name = wu)
			wuNames.append(workUnit.name)
			workUnit.aggregatedWuDeliverable.add(deliverable)
			workUnit.save()
	responseData = {}
	responseData['applied'] = wuNames
	return responseData

def buildDelivVaData(deliverable, vaRequirement, projectSpec, qualityLevel, jsonData, svas = None):
	vaData = None
	if projectSpec.name == 1.0:
		try:
			delivVaData = deliverable.vaData
			vaId = delivVaData.id
			vaData = VaData10.objects.get(pk = vaId)
			if vaData.id == None:
				raise Exception('Check for existing VA Data for this category')
		except:
			try:
				vaData = VaData10.objects.get(vaRequirement = vaRequirement, category = deliverable.category)
				if vaData.id == None:
					raise Exception('Create new VA Data')
			except:
				vaData = VaData10.objects.create(vaRequirement = vaRequirement, category = deliverable.category)
		if jsonData['repfundChkpt'] != '':
			vaData.reportedFvaChkpts = jsonData['repfundChkpt']
		if jsonData['repfundVal'] != '':
			vaData.reportedFvaValue = jsonData['repfundVal']
		if jsonData['repconsChkpt'] != '':
			vaData.reportedCvaChkpts = jsonData['repconsChkpt']
		if jsonData['repconsVal'] != '':
			vaData.reportedCvaValue = jsonData['repconsVal']
		if jsonData['testconsChkpt'] != '':
			vaData.testedCvaChkpts = jsonData['testconsChkpt']
		if jsonData['testconsVal'] != '':
			vaData.testedCvaValue = jsonData['testconsVal']
		if jsonData['testfundChkpt'] != '':
			vaData.testedFvaChkpts = jsonData['testfundChkpt']
		if jsonData['testfundVal'] != '':
			vaData.testedFvaValue = jsonData['testfundVal']
		if svas != [] and svas != '':
			for sva in svas:
				sResults = None	
				for key, value in jsonData.items():	
					if 'repSuppChkpts' in key:
						if str(sva.id) in key or str(sva.vaReqSvaId) in key:
							repChkpts = jsonData[key]
					if 'repSuppVal' in key:
						if str(sva.id) in key or str(sva.vaReqSvaId) in key:
							repVal = jsonData[key]					
					if 'testSuppChkpts' in key:
						if str(sva.id) in key or str(sva.vaReqSvaId) in key:
							testChkpts = jsonData[key]	
					if 'testSuppVal' in key:
						if str(sva.id) in key or str(sva.vaReqSvaId) in key:
							testVal = jsonData[key]
				if repChkpts == '' and repVal == '' and testChkpts == '' and testVal == '':
					continue
				else:
					try:
						sResults = SuppVaResults.objects.get(sva = sva, vaData = vaData)
					except:
						sResults = SuppVaResults.objects.create(sva = sva, vaData = vaData)
					sResults.vaData = vaData
					sResults.reportedChkpts = repChkpts	
					sResults.reportedValue = repVal
					sResults.testedChkpts = testChkpts
					sResults.testedValue = testVal
					sResults.save()
					sva.vaReqSvaId = None
					sva.save
					
	if projectSpec.name == 1.2:
		try:
			delivVaData = deliverable.vaData
			vaId = delivVaData.id
			vaData = VaData12.objects.get(pk=vaId)
			if vaData.id == None:
				raise Exception('Check for existing VA Data for this category')
		except:
			try:
				vaData = VaData12.objects.get(vaRequirement = vaRequirement, category = deliverable.category)
				if vaData.id == None:
					raise Exception('Create new VA Data')
			except:
				vaData = VaData12.objects.create(vaRequirement = vaRequirement, category = deliverable.category)
				
		if jsonData['repvegChkpt'] != '':
			vaData.reportedVvaChkpts = jsonData['repvegChkpt']
		if jsonData['repvegVal'] != '':
			vaData.reportedVvaValue = jsonData['repvegVal']
		if jsonData['repnonvegChkpt'] != '':
			vaData.reportedNvaChkpts = jsonData['repnonvegChkpt']
		if jsonData['repnonvegVal'] != '':
			vaData.reportedNvaValue = jsonData['repnonvegVal']
		if jsonData['testvegChkpt'] != '':
			vaData.testedVvaChkpts = jsonData['testvegChkpt']
		if jsonData['testvegVal'] != '':
			vaData.testedVvaValue = jsonData['testvegVal']
		if jsonData['testnonvegChkpt'] != '':
			vaData.testedNvaChkpts = jsonData['testnonvegChkpt']
		if jsonData['testnonvegVal'] != '':
			vaData.testedNvaValue = jsonData['testnonvegVal']
	vaData.save()
	deliverable.vaData = vaData
	deliverable.save()
	return vaData

def buildAggregatedWuDeliverable(category_id, delivDict):
	if category_id == '1':
		category = AggregatedWuDeliverableCategory.objects.get(category=1)
		dem = DEM.objects.create(category=category)
		dem = buildDem(delivDict, dem)
		deliv = AggregatedWuDeliverable.objects.get(pk=dem.id)
		deliv.save()
	if category_id == '2':
		category = AggregatedWuDeliverableCategory.objects.get(category=2)
		swath = Swath.objects.create(category=category)
		swath = buildSwath(delivDict, swath)
		deliv = AggregatedWuDeliverable.objects.get(pk=swath.id)
		deliv.save()
		
	if category_id == '3':
		category = AggregatedWuDeliverableCategory.objects.get(category=3)
		classified = Classified.objects.create(category=category)
		classified = buildClassified(delivDict, classified)
		deliv = AggregatedWuDeliverable.objects.get(pk=classified.id)
	return deliv

def buildAggregatedWuDeliverableTab(wus, deliv):
	vaReqs = getVaReqsFromWus(wus)
	if len(vaReqs) > 0:
		# create new tab for each
		for vaReqID in vaReqs:
			vaRequirement = VaRequirement.objects.get(pk=vaReqID)
			AggregatedWuDeliverableTab.objects.create(deliverable=deliv, vaRequirement=vaRequirement)
	if len(vaReqs) == 0:
		AggregatedWuDeliverableTab.objects.create(deliverable=deliv)
	## return 1st tab ID for redirect
	returnTab = None
	if len(vaReqs) > 0:
		vaReq = VaRequirement.objects.get(pk=vaReqs[0])
		returnTab = AggregatedWuDeliverableTab.objects.get(deliverable=deliv, vaRequirement=vaReq)
	else:
		returnTab = AggregatedWuDeliverableTab.objects.get(deliverable=deliv)
	return returnTab

def getAggregatedWuDeliverables(wus, category_id):
	delivs = []
	deliv = None
	vaReq = None
	# needs to be unique (some wus will have same deliverable, don't want repeated)
	for wu in wus:
		aggWuDelivs = list(wu.aggregatedWuDeliverable.all())
		if aggWuDelivs != []:
			if category_id == '1':
				aggWuDelivCat = AggregatedWuDeliverableCategory.objects.get(category=1)
				dem = None
				for deliverable in aggWuDelivs:
					if deliverable.category == aggWuDelivCat:
						dem = deliverable
						deliv = AggregatedWuDeliverable.objects.get(pk=dem.id)

			if category_id == '2':
				aggWuDelivCat = AggregatedWuDeliverableCategory.objects.get(category=2)
				swath = None
				for deliverable in aggWuDelivs:
					if deliverable.category == aggWuDelivCat:
						swath = deliverable
						deliv = AggregatedWuDeliverable.objects.get(pk=swath.id)
			if category_id == '3':
				aggWuDelivCat = AggregatedWuDeliverableCategory.objects.get(category=3)
				classified = None
				for deliverable in aggWuDelivs:
					if deliverable.category == aggWuDelivCat:
						classified = deliverable
						deliv = AggregatedWuDeliverable.objects.get(pk=classified.id)
			if deliv:
				if not deliv in delivs:
					delivs.append(deliv)
			else:
				continue
	return delivs

def getVARequirements(wus):
	vaReqs = []
	for wu in wus:
		vaReq = wu.vaRequirement
		if vaReq:
			if not vaReq in vaReqs:
				vaReqs.append(vaReq)
	return vaReqs

def getVAFreeWus(wus):
	freeWus = {}
	for wu in wus:
		if not wu.vaRequirement:
			freeWus[wu.workUnitId] = wu.name
	return freeWus

def getAggregatedWuDeliverableTabs(delivs, review):
	tabIds = {}
	for deliv in delivs:
		wus = WorkUnit.objects.filter(aggregatedWuDeliverable=deliv, review=review)
		vaReqs = getVaReqsFromWus(wus)
		if len(vaReqs) > 0:
			# create new tab for each
			for vaReq in vaReqs:
				tabId = None
				vaRequirement = VaRequirement.objects.get(pk=vaReq)
				try:
					## if no va req on dem tab, delete it and throw exception
					try:
						tab = AggregatedWuDeliverableTab.objects.get(deliverable=deliv, vaRequirement=None)
						tab.delete()
						raise Exception()
					except:
						tab = AggregatedWuDeliverableTab.objects.get(deliverable=deliv, vaRequirement=vaRequirement)
						tabId = tab.id
				except:
					tab = AggregatedWuDeliverableTab.objects.create(deliverable=deliv, vaRequirement=vaRequirement)
					tabId = tab.id
				tabIds[tabId] = deliv.id
		if len(vaReqs) == 0:
			## CREATE TAB WITH DEM ONLY
			tabId = None
			try:
				tab = AggregatedWuDeliverableTab.objects.get(deliverable=deliv)
				tabId = tab.id
			except:
				tab = AggregatedWuDeliverableTab.objects.create(deliverable=deliv)
				tabId = tab.id
			tabIds[tabId] = deliv.id
	return tabIds

def getVaReqsFromWus(wus):
	vaReqs = []
	for wu in wus:
		try:
			vaReq = wu.vaRequirement
			if vaReq.id not in vaReqs:
				vaReqs.append(vaReq.id)
		except:
			continue
	return vaReqs

def buildAggregatedWuTabHtml(category_id, tabIds, review, classifications = None):
	## determine if free work units so '+' tab can be added
	freeWus = {}
	type = None
	if category_id == '1':
		freeWus = freeWorkUnits(review, 'dem')
		type = 'DEM'
	if category_id == '2':
		freeWus = freeWorkUnits(review, 'swath')
		type = 'Swath'
	if category_id == '3':
		freeWus = freeWorkUnits(review, 'classified')
		type = 'Classified'

	if freeWus != {} and category_id == '3':
		html = render_to_string('aggregatedWuDeliverable_tabs.html',
								{'aggWuDelivTabs': tabIds, 'type': type, 'wus': 'True',
								 'classifications': classifications})
	elif category_id == '3':
		html = render_to_string('aggregatedWuDeliverable_tabs.html',
								{'aggWuDelivTabs': tabIds, 'type': type, 'classifications': classifications})
	elif freeWus != {}:
		html = render_to_string('aggregatedWuDeliverable_tabs.html',
								{'aggWuDelivTabs': tabIds, 'type': type, 'wus': 'True'})
	else:
		html = render_to_string('aggregatedWuDeliverable_tabs.html', {'aggWuDelivTabs': tabIds, 'type': type})

	return html

def buildAggWuTabHtmlNoVaReq(responseData, category_id, deliv, freeWus, wuSameInfo, errors, errorTypes, tab_id):
	responseData['noVa'] = 'True'
	if category_id == '1':
		dem = DEM.objects.get(pk=deliv.id)
		tabHtml = render_to_string('aggregatedWuDeliv_tab.html',
								   {'dem': dem, 'wuList': freeWus, 'wuSameInfo': wuSameInfo, 'errors': errors,
									'errorTypes': errorTypes, 'id': tab_id})
	if category_id == '2':
		swath = Swath.objects.get(pk=deliv.id)
		tabHtml = render_to_string('aggregatedWuDeliv_tab.html',
								   {'swath': swath, 'wuList': freeWus, 'wuSameInfo': wuSameInfo, 'errors': errors,
									'errorTypes': errorTypes, 'id': tab_id})
	if category_id == '3':
		classified = Classified.objects.get(pk=deliv.id)
		tabHtml = render_to_string('aggregatedWuDeliv_tab.html',
								   {'classified': classified, 'wuList': freeWus, 'wuSameInfo': wuSameInfo,
									'errors': errors,
									'errorTypes': errorTypes, 'id': tab_id})
	return tabHtml

def buildAggWuTabHtmlVaReqSpec10(vaRequirement, vaData, category_id, deliv, freeWus, wuSameInfo, errors, errorTypes, svaData, tab_id):
	vaRequirement = VaRequirement10.objects.get(pk=vaRequirement.id)
	if vaData:
		vaData = VaData10.objects.get(pk=vaData.id)
		if category_id == '1':
			dem = DEM.objects.get(pk=deliv.id)
			tabHtml = render_to_string('aggregatedWuDeliv_tab.html',
									   {'dem': dem, 'wuList': freeWus, 'wuSameInfo': wuSameInfo, 'req10': True,
										'vaReq': vaRequirement, 'errors': errors, 'errorTypes': errorTypes,
										'svaData': svaData, 'vaResults': vaData, 'id': tab_id})
		if category_id == '2':
			swath = Swath.objects.get(pk=deliv.id)
			tabHtml = render_to_string('aggregatedWuDeliv_tab.html',
									   {'swath': swath, 'wuList': freeWus, 'wuSameInfo': wuSameInfo, 'req10': True,
										'vaReq': vaRequirement, 'errors': errors, 'errorTypes': errorTypes,
										'svaData': svaData, 'vaResults': vaData, 'id': tab_id})
		if category_id == '3':
			classified = Classified.objects.get(pk=deliv.id)
			tabHtml = render_to_string('aggregatedWuDeliv_tab.html',
									   {'classified': classified, 'wuList': freeWus, 'wuSameInfo': wuSameInfo,
										'req10': True,
										'vaReq': vaRequirement, 'errors': errors, 'errorTypes': errorTypes,
										'svaData': svaData, 'vaResults': vaData, 'id': tab_id})
	else:
		if category_id == '1':
			dem = DEM.objects.get(pk=deliv.id)
			tabHtml = render_to_string('aggregatedWuDeliv_tab.html',
									   {'dem': dem, 'wuList': freeWus, 'wuSameInfo': wuSameInfo, 'req10': True,
										'vaReq': vaRequirement, 'errors': errors, 'errorTypes': errorTypes,
										'svaData': svaData, 'id': tab_id})
		if category_id == '2':
			swath = Swath.objects.get(pk=deliv.id)
			tabHtml = render_to_string('aggregatedWuDeliv_tab.html',
									   {'swath': swath, 'wuList': freeWus, 'wuSameInfo': wuSameInfo, 'req10': True,
										'vaReq': vaRequirement, 'errors': errors, 'errorTypes': errorTypes,
										'svaData': svaData, 'id': tab_id})
		if category_id == '3':
			classified = Classified.objects.get(pk=deliv.id)
			tabHtml = render_to_string('aggregatedWuDeliv_tab.html',
									   {'classified': classified, 'wuList': freeWus, 'wuSameInfo': wuSameInfo,
										'req10': True,
										'vaReq': vaRequirement, 'errors': errors, 'errorTypes': errorTypes,
										'svaData': svaData, 'id': tab_id})
	return tabHtml

def buildAggWuTabHtmlVaReqSpec12(vaRequirement, vaData, category_id, deliv, freeWus, wuSameInfo, errors, errorTypes, svaData, tab_id):
	vaRequirement = VaRequirement12.objects.get(pk=vaRequirement.id)
	if vaData:
		vaData = VaData12.objects.get(pk=vaData.id)
		if category_id == '1':
			dem = DEM.objects.get(pk=deliv.id)
			tabHtml = render_to_string('aggregatedWuDeliv_tab.html',
									   {'dem': dem, 'wuList': freeWus, 'wuSameInfo': wuSameInfo, 'req12': True,
										'vaReq': vaRequirement,'errors': errors,'errorTypes': errorTypes,
										'svaData': svaData, 'vaResults': vaData, 'id': tab_id})
		if category_id == '2':
			swath = Swath.objects.get(pk=deliv.id)
			tabHtml = render_to_string('aggregatedWuDeliv_tab.html',
									   {'swath': swath, 'wuList': freeWus, 'wuSameInfo': wuSameInfo, 'req12': True,
										'vaReq': vaRequirement, 'errors': errors,'errorTypes': errorTypes,
										'svaData': svaData, 'vaResults': vaData, 'id': tab_id})
		if category_id == '3':
			classified = Classified.objects.get(pk=deliv.id)
			tabHtml = render_to_string('aggregatedWuDeliv_tab.html',
									   {'classified': classified, 'wuList': freeWus, 'wuSameInfo': wuSameInfo,
										'req12': True,
										'vaReq': vaRequirement,'errors': errors, 'errorTypes': errorTypes,
										'svaData': svaData, 'vaResults': vaData, 'id': tab_id})
	else:
		if category_id == '1':
			dem = DEM.objects.get(pk=deliv.id)
			tabHtml = render_to_string('aggregatedWuDeliv_tab.html',
									   {'dem': dem, 'wuList': freeWus, 'wuSameInfo': wuSameInfo, 'req12': True,
										'vaReq': vaRequirement,'errors': errors, 'errorTypes': errorTypes,
										'svaData': svaData, 'id': tab_id})
		if category_id == '2':
			swath = Swath.objects.get(pk=deliv.id)
			tabHtml = render_to_string('aggregatedWuDeliv_tab.html',
									   {'swath': swath, 'wuList': freeWus, 'wuSameInfo': wuSameInfo, 'req12': True,
										'vaReq': vaRequirement,'errors': errors, 'errorTypes': errorTypes,
										'svaData': svaData, 'id': tab_id})
		if category_id == '3':
			classified = Classified.objects.get(pk=deliv.id)
			tabHtml = render_to_string('aggregatedWuDeliv_tab.html',
									   {'classified': classified, 'wuList': freeWus, 'wuSameInfo': wuSameInfo,
										'req12': True,
										'vaReq': vaRequirement,'errors': errors, 'errorTypes': errorTypes,
										'svaData': svaData, 'id': tab_id})
	return tabHtml

def buildCITabHtml(vaRequirement, responseCollInfo, freeWus, qualLevels, qualityLevel, sensorsUsed, sensorUsed, sensorTypes, sensorType, projectSpecName, wuSameInfo):
	if freeWus != {} and vaRequirement == None:
		tabHtml = render_to_string('collinfo_tab.html',
								   {'collInfo': responseCollInfo, 'wuList': freeWus, 'qualLevels': qualLevels,
									'qualityLevel': qualityLevel, 'sensorsUsed':sensorsUsed, 'sensorUsed':sensorUsed,
									'sensorTypes':sensorTypes, 'sensorType':sensorType, 'projectSpec': projectSpecName,
									'wuSameInfo': wuSameInfo})
	elif freeWus == {} and vaRequirement == None:
		tabHtml = render_to_string('collinfo_tab.html', {'collInfo': responseCollInfo, 'qualLevels': qualLevels,
														 'qualityLevel': qualityLevel, 'sensorsUsed':sensorsUsed, 'sensorUsed':sensorUsed,
														 'sensorTypes':sensorTypes, 'sensorType':sensorType,'projectSpec': projectSpecName,
														 'wuSameInfo': wuSameInfo})
	elif freeWus != {} and vaRequirement != None and projectSpecName == 1.0:
		vaRequirement = VaRequirement10.objects.get(pk=vaRequirement.id)
		tabHtml = render_to_string('collinfo_tab.html',
								   {'collInfo': responseCollInfo, 'wuList': freeWus, 'qualLevels': qualLevels,
									'qualityLevel': qualityLevel, 'sensorsUsed':sensorsUsed, 'sensorUsed':sensorUsed,
									'sensorTypes':sensorTypes, 'sensorType':sensorType,'projectSpec': projectSpecName, 'req10': True,
									'vaReq': vaRequirement, 'wuSameInfo': wuSameInfo})
	elif freeWus == {} and vaRequirement != None and projectSpecName == 1.0:
		vaRequirement = VaRequirement10.objects.get(pk=vaRequirement.id)
		tabHtml = render_to_string('collinfo_tab.html', {'collInfo': responseCollInfo, 'qualLevels': qualLevels,
														 'qualityLevel': qualityLevel, 'sensorsUsed':sensorsUsed, 'sensorUsed':sensorUsed,
														 'sensorTypes':sensorTypes, 'sensorType':sensorType,'projectSpec': projectSpecName,
														 'req10': True, 'vaReq': vaRequirement,
														 'wuSameInfo': wuSameInfo})
	## does not account for if project spec changes
	elif freeWus != {} and vaRequirement != None and projectSpecName == 1.2:
		vaRequirement = VaRequirement12.objects.get(pk=vaRequirement.id)
		tabHtml = render_to_string('collinfo_tab.html',
								   {'collInfo': responseCollInfo, 'wuList': freeWus, 'qualLevels': qualLevels,
									'qualityLevel': qualityLevel, 'sensorsUsed':sensorsUsed, 'sensorUsed':sensorUsed,
									'sensorTypes':sensorTypes, 'sensorType':sensorType,'projectSpec': projectSpecName, 'req12': True,
									'vaReq': vaRequirement, 'wuSameInfo': wuSameInfo})
	elif freeWus == {} and vaRequirement != None and projectSpecName == 1.2:
		vaRequirement = VaRequirement12.objects.get(pk=vaRequirement.id)
		tabHtml = render_to_string('collinfo_tab.html', {'collInfo': responseCollInfo, 'qualLevels': qualLevels,
														 'qualityLevel': qualityLevel, 'sensorsUsed':sensorsUsed, 'sensorUsed':sensorUsed,
														 'sensorTypes':sensorTypes, 'sensorType':sensorType,'projectSpec': projectSpecName,
														 'req12': True, 'vaReq': vaRequirement,
														 'wuSameInfo': wuSameInfo})
	return tabHtml

	
@qcr_user_authenticated	
def reports(request, review_id):
	return render(request, 'reports.html', {'reviewId':review_id})
@qcr_user_authenticated	
def contractorReports(request, review_id):
	user = request.user
	admin = False
	if user.is_staff:
		admin = True
	reports = []
	reportDatas = ReportData.objects.filter(type='contractor')
	review = Review.objects.get(pk = review_id)
	for reportData in reportDatas:
		report = reportData.report
		reports.append(report)
	return render(request, 'reportType.html', {'type':'Contractor', 'reports':reports, 'review':review, 'admin':str(admin)})
@qcr_user_authenticated	
def newContractorReport(request, review_id = None):
	if request.method == 'POST':
		saveReport = False
		aoiImage = None
		if request.FILES:
			files = request.FILES
			file = None
			for k, v in files.items():
				file = request.FILES[k]
				aoiImage = file
				break	
		reviewId = None
		requestFilenames = []
		relVaPassFail = False
		absVaPassFail = False
		for key, value in request.POST.items():
			if 'hidden' in key:
				if value != '':
					filename = ''
					if str(sys.platform) == 'win32':
						filename = value.split('%5C')[-1]
					else:
						filename = value.split('%2F')[-1]
					requestFilenames.append(filename)
			if key == 'review':
				reviewId = value
			if key == 'save':
				saveReport = True
			if key == 'relVaPassFail':
				if value == 'true':
					relVaPassFail = True
			if key == 'absVaPassFail':
				if value == 'true':
					absVaPassFail = True	
				
		errorGroups = summarizeErrorData(reviewId)
		serializedErrorGroups = serializeErrorGroups(errorGroups, requestFilenames)
		reportGraphics = serializeReportGraphics()
		serializedPassFailData = getSerializedPassFailData(reviewId, relVaPassFail, absVaPassFail)
		serializedVaData = serializeVaData(reviewId)
		inputDict = aggregateContractorReportData(reviewId)
		if saveReport:
			user = request.user
			report = saveQcReport(user, inputDict, aoiImage, serializedErrorGroups, serializedPassFailData, serializedVaData)
			type = inputDict['type']
			if type == 'contractor':
				type = 'Contractor'	
				url = reverse('contractorReports', args = (), kwargs = {'review_id':reviewId})
				return HttpResponseRedirect(url)
		else:
			response = HttpResponse(content_type='application/pdf')
			response['Content-Disposition'] = 'inline; filename="contractor_report.pdf"'
			report = ReportGenerator(response, inputDict, aoiImage, serializedErrorGroups, reportGraphics, serializedPassFailData, serializedVaData)
			response = report.buildReport()
			return response		
	else:
		type = 'Contractor'
		review = Review.objects.get(pk = review_id)
		errorGroups = summarizeErrorData(review_id)
		return render(request, 'new_contractor_report.html', {'review':review, 'type':type, 'errorGroups':errorGroups})

@qcr_user_authenticated	
def deleteReport(request, review_id, report_id):
	report = SavedReport(pk = report_id)
	reportErrorGroup = ReportErrorGroup.objects.get(report = report)
	reportData = ReportData.objects.get(report = report)
	aoiImage = ReportAoiImage.objects.get(reportData = reportData)
	try:
		img = FileModelReportAoiImage.objects.get(filename = str(aoiImage.picture))
		if img:
			img.delete()
	except:
		pass
	errImgs = ReportErrorImage.objects.filter(errorGroup = reportErrorGroup)
	for img in errImgs:
		try:
			errImg = FileModelReportErrorImage.objects.get(filename = str(img.picture))
			if errImg:
				errImg.delete()
		except:
			continue
	report.delete()
	url = reverse('contractorReports', args = (), kwargs = {'review_id':review_id})
	return HttpResponseRedirect(url)
		
def summarizeErrorData(review_id):
	errorGroups = {}
	review = Review.objects.get(pk = review_id)
	wus = WorkUnit.objects.filter(review = review)
	metaDelivs = []
	breaklineDelivs = []
	reportDelivs = []
	otherDelivs = []
	demAggWuDelivs = []
	swathAggWuDelivs = []
	classAggWuDelivs = []
	##
	for wu in wus:	
		catDelivs = list(Deliverable.objects.filter(workUnit = wu, deliverableCategory__category = 1))
		for deliv in catDelivs:
			if deliv not in metaDelivs:
				metaDelivs.append(deliv)
		catDelivs = list(Deliverable.objects.filter(workUnit = wu, deliverableCategory__category = 2))
		for deliv in catDelivs:
			if deliv not in breaklineDelivs:
				breaklineDelivs.append(deliv)
		catDelivs = list(Deliverable.objects.filter(workUnit = wu, deliverableCategory__category = 6))
		for deliv in catDelivs:
			if deliv not in reportDelivs:
				reportDelivs.append(deliv)		
		catDelivs = list(Deliverable.objects.filter(workUnit = wu, deliverableCategory__category = 7))
		for deliv in catDelivs:
			if deliv not in otherDelivs:
				otherDelivs.append(deliv)
		catDelivs = AggregatedWuDeliverable.objects.filter(workunit__workUnitId = wu.workUnitId, category__category=1)
		for deliv in catDelivs:
			if deliv not in demAggWuDelivs:
				demAggWuDelivs.append(deliv)
		
		catDelivs = AggregatedWuDeliverable.objects.filter(workunit__workUnitId = wu.workUnitId, category__category=2)
		for deliv in catDelivs:
			if deliv not in swathAggWuDelivs:
				swathAggWuDelivs.append(deliv)
		
		catDelivs = AggregatedWuDeliverable.objects.filter(workunit__workUnitId = wu.workUnitId, category__category=3)
		for deliv in catDelivs:
			if deliv not in classAggWuDelivs:
				classAggWuDelivs.append(deliv)
		
	metadataGroups = listMatchingErrors(metaDelivs)
	breaklineGroups = listMatchingErrors(breaklineDelivs)
	reportGroups = listMatchingErrors(reportDelivs)
	otherGroups = listMatchingErrors(otherDelivs)
	demAggWuDelivErrGroups = listMatchingErrors(demAggWuDelivs, agg = True)
	swathAggWuDelivErrGroups = listMatchingErrors(swathAggWuDelivs, agg = True)
	classAggWuDelivErrGroups = listMatchingErrors(classAggWuDelivs, agg = True)
	
	if metadataGroups != []:
		errorGroups['metadata'] = metadataGroups
	if breaklineGroups != []:
		errorGroups['breaklines'] = breaklineGroups
	if reportGroups != []:
		errorGroups['reports'] = reportGroups
	if otherGroups != []:
		errorGroups['other'] = otherGroups
	if demAggWuDelivErrGroups != []:
		errorGroups['dem'] = demAggWuDelivErrGroups
	if swathAggWuDelivErrGroups != []:
		errorGroups['swath'] = swathAggWuDelivErrGroups
	if classAggWuDelivErrGroups != []:
		errorGroups['classified'] = classAggWuDelivErrGroups
	return errorGroups 
	
def listMatchingErrors(delivs, agg = False):
	errorList = []
	for deliv in delivs:
		errors = None
		if agg:
			errors = Error.objects.filter(aggregatedWuDeliverable = deliv)
		else:
			errors = Error.objects.filter(deliverable = deliv)
		for error in errors:
			errorList.append(error)
	matches = []
	runningList = []
	for error in errorList:
		type = error.errorType.name
		subtype = error.errorSubtype
		sameList = []
		for error in errorList:
			if error.errorType.name == type and error.errorSubtype == subtype:
				if error.id not in runningList:
					runningList.append(error.id)
					sameList.append(error)
		if sameList != []:
			matches.append(sameList)
	return matches
	
def serializeErrorGroups(errorGroups, reportErrorImages):
	errorImgGroups = {}
	for cat, groups in errorGroups.items():
		groupList = []
		for errorGroup in groups:
			errorDict = defaultdict(list)
			for error in errorGroup:
				if not errorDict['NUM_ERR']:
					errorDict['NUM_ERR'] = str(len(errorGroup))
				if not errorDict['ERR_TYPE']:
					errorDict['ERR_TYPE'] = str(error.errorType)
				if not errorDict['ERR_SUB']:
					try:
						errorDict['ERR_SUB'] = str(error.errorSubtype.name)
					except:
						errorDict['ERR_SUB'] = 'None'
				images = ErrorImage.objects.filter(error = error)				
				if images != []:
					for image in images:
						pic = image.picture
						picFilenameString = ''
						if str(sys.platform) == 'win32':
							picFilenameString = str(pic).split('\\')[-1]
						else:
							picFilenameString = str(pic).split('/')[-1]
						## PROBLEM IS HERE
						if picFilenameString in reportErrorImages:
							errorDict['IMG_LIST'].append(pic)				
			groupList.append(errorDict)
		errorImgGroups[cat] = groupList
	return errorImgGroups

def serializeReportGraphics():
		static_root = settings.STATIC_ROOT
		usgs_banner = os.path.join(static_root,'USGS_Banner.png')
		usgs_logo = os.path.join(static_root,'usgs_BW.jpg')
		natMap_logo = os.path.join(static_root,'NatMap_Logo.jpg')
		graphicsDict = {}
		graphicsDict['BANNER'] = usgs_banner
		graphicsDict['USGS_LOGO'] = usgs_logo
		graphicsDict['NATMAP_LOGO'] = natMap_logo
		return graphicsDict

def serializeVaData(reviewId):
	review = Review.objects.get(pk = reviewId)
	workUnits = WorkUnit.objects.filter(review = review)
	wuDict = {}
	for wu in workUnits:
		vaRequirement = wu.vaRequirement
		vaDatas = VaData.objects.filter(vaRequirement = vaRequirement)
		workPackage = wu.workPackage
		projectSpec = workPackage.projectSpec.name
		vaDict = {}
		if vaRequirement and vaDatas != []:
			for vaData in vaDatas:		
				delivCatString = vaData.category
				valsDict = {}
				if str(projectSpec) == '1.0':
					vaReq10 = VaRequirement10.objects.get(pk = vaRequirement.id)
					vaData10 = VaData10.objects.get(pk = vaData.id)
					reqRepTestDict = {}
					fvaReqChkpt = vaReq10.fundamentalVaChkpt
					fvaReqValue = vaReq10.fundamentalVaValue
					cvaReqChkpt = vaReq10.consolidatedVaChkpt
					cvaReqValue = vaReq10.consolidatedVaValue
					fvaRepChkpt = vaData10.reportedFvaChkpts
					fvaRepValue = vaData10.reportedFvaValue
					cvaRepChkpt = vaData10.reportedCvaChkpts
					cvaRepValue = vaData10.reportedCvaValue
					fvaTestChkpt = vaData10.testedFvaChkpts
					fvaTestValue = vaData10.testedFvaValue
					cvaTestChkpt = vaData10.testedCvaChkpts
					cvaTestValue = vaData10.testedCvaValue
					cvaDict = {}
					cvaDict['ReqChkpts'] = cvaReqChkpt
					cvaDict['ReqVal'] = cvaReqValue
					cvaDict['RepChkpts'] = cvaRepChkpt
					cvaDict['RepVal'] = cvaRepValue
					cvaDict['TestChkpts'] = cvaTestChkpt
					cvaDict['TestVal'] = cvaTestValue
					fvaDict = {}
					fvaDict['ReqChkpts'] = fvaReqChkpt
					fvaDict['ReqVal'] = fvaReqValue
					fvaDict['RepChkpts'] = fvaRepChkpt
					fvaDict['RepVal'] = fvaRepValue
					fvaDict['TestChkpts'] = fvaTestChkpt
					fvaDict['TestVal'] = fvaTestValue
					valsDict['CVA'] = cvaDict
					valsDict['FVA'] = fvaDict
					svaReqs = list(SuppVaMeasure.objects.filter(vaRequirement = vaReq10))
					if svaReqs:
						svaList = []
						for sva in svaReqs:
							svaData = SuppVaResults.objects.get(sva = sva, vaData = vaData)
							svaValsDict = {}
							svaReqValue = sva.reqVal
							svaReqChkpt = sva.reqChkpts
							svaRepValue = svaData.reportedValue
							svaRepChkpt = svaData.reportedChkpts
							svaTestValue = svaData.testedValue
							svaTestChkpt = svaData.testedChkpts
							svaValsDict['ReqVal'] = svaReqValue
							svaValsDict['ReqChkpts'] = svaReqChkpt
							svaValsDict['RepVal'] = svaRepValue
							svaValsDict['RepChkpts'] = svaReqChkpt
							svaValsDict['TestVal'] = svaTestValue
							svaValsDict['TestChkpts'] = svaTestChkpt
							svaList.append(svaValsDict)

					valsDict['SVA'] = svaList
				if str(projectSpec) == '1.2':
					vaReq12 = VaRequirement12.objects.get(pk = vaRequirement.id)
					vaData12 = VaData12.objects.get(pk = vaData.id)
					reqRepTestDict = {}
					nvaReqChkpt = vaReq12.nonvegetatedVaChkpt
					nvaReqValue = vaReq12.nonvegetatedVaValue
					vvaReqChkpt = vaReq12.vegetatedVaChkpt
					vvaReqValue = vaReq12.vegetatedVaValue
					nvaRepChkpt = vaData12.reportedNvaChkpts
					nvaRepValue = vaData12.reportedNvaValue
					vvaRepChkpt = vaData12.reportedVvaChkpts
					vvaRepValue = vaData12.reportedVvaValue
					nvaTestChkpt = vaData12.testedNvaChkpts
					nvaTestValue = vaData12.testedNvaValue
					vvaTestChkpt = vaData12.testedVvaChkpts
					vvaTestValue = vaData12.testedVvaValue
					nvaDict = {}
					nvaDict['ReqChkpts'] = nvaReqChkpt
					nvaDict['ReqVal'] = nvaReqValue
					nvaDict['RepChkpts'] = nvaRepChkpt
					nvaDict['RepVal'] = nvaRepValue
					nvaDict['TestChkpts'] = nvaTestChkpt
					nvaDict['TestVal'] = nvaTestValue
					vvaDict = {}
					vvaDict['ReqChkpts'] = vvaReqChkpt
					vvaDict['ReqVal'] = vvaReqValue
					vvaDict['RepChkpts'] = vvaRepChkpt
					vvaDict['RepVal'] = vvaRepValue
					vvaDict['TestChkpts'] = vvaTestChkpt
					vvaDict['TestVal'] = vvaTestValue
					valsDict['NVA'] = nvaDict
					valsDict['VVA'] = vvaDict
				cat = ''
				if str(delivCatString) == '1':
					cat = 'DEM'
				if str(delivCatString) == '2':
					cat = 'Unclassified Swath'
				if str(delivCatString) == '3':
					cat = 'Classified Point Cloud'
				vaDict[cat] = valsDict
			wuDict[wu] = vaDict
	return wuDict
	
## Convert saved/archived report data into EXACT SAME serialized data
## which goes into the create report method
def serializeReportDataObject(report):
	inputDict = {}
	reportData = ReportData.objects.get(report = report)
	errorGroups = ReportErrorGroup.objects.filter(report = report)
	passFailData = ReportPassFailData.objects.filter(report = report)
	vaData = ReportVaDataCollectionWorkUnit.objects.filter(report = report)
	workUnits = ReportWorkUnitId.objects.filter(reportData = reportData)
	delivs = ReportDeliverableData.objects.filter(reportData = reportData)
	img = ReportAoiImage.objects.get(reportData = reportData)
	aoiImage = img.picture
	
	workUnitIds = []
	for wu in workUnits:
		workUnitIds.append(wu.workUnitId)
	
	serializedDelivs = []
	for deliv in delivs:
		delivDict = {}
		delivDict['category'] = deliv.category
		delivDict['description'] = deliv.description
		delivDict['accepted'] = deliv.accepted
		delivDict['summary'] = deliv.summary
		serializedDelivs.append(delivDict)
	inputDict['type'] = reportData.type
	inputDict['wpName'] = reportData.wpName
	inputDict['reportGenTime'] = report.createdDate
	inputDict['workUnits'] = workUnitIds
	inputDict['poc'] = reportData.poc
	#inputDict['pocPhone'] = workPackage.pocPhone
	inputDict['pocEmail'] = reportData.pocEmail
	#inputDict['errorShp'] = ## FUTURE - FIGURE IT OUT ##
	inputDict['delivDicts'] = serializedDelivs
	categories = []
	
	for group in errorGroups:
		category = group.category
		if category not in categories:
			categories.append(category)
	errDict = {}
	for category in categories:
		groupList = []
		errGroups = ReportErrorGroup.objects.filter(report = report, category = category)
		for errGroup in errGroups:
			errGroupDict = {}
			numErrs = errGroup.numErrors
			type = errGroup.errorType
			subtype = errGroup.errorSubtype
			images = ReportErrorImage.objects.filter(errorGroup = errGroup)
			imageList = []
			for image in images:
				imageList.append(image.picture)
			errGroupDict['NUM_ERR'] = numErrs
			errGroupDict['ERR_TYPE'] = type
			errGroupDict['ERR_SUB'] = subtype
			errGroupDict['IMG_LIST'] = imageList
			groupList.append(errGroupDict)
		errDict[category] = groupList
	passFailDict = {}	
	for data in passFailData:
		if data.review == True:
			passFailDict['review'] = 'MEETS'
		else:
			passFailDict['review'] = 'DOES NOT MEET'
		if data.relVa != None:
			if data.relVa == True:
				passFailDict['relVa'] = 'ACCEPTS'
			elif data.relVa == False:
				passFailDict['relVa'] = 'DOES NOT ACCEPT'
		if data.absVa != None:
			if data.absVa == True:
				passFailDict['absVa'] = 'ACCEPTS'
			elif data.absVa == False:
				passFailDict['absVa'] = 'DOES NOT ACCEPT'
		if data.metadata != None:
			if data.metadata == True:
				passFailDict['metadata'] = 'ACCEPTS'
			elif data.metadata == False:
				passFailDict['metadata'] = 'DOES NOT ACCEPT'
		if data.breaklines != None:
			if data.breaklines == True:
				passFailDict['breaklines'] = 'ACCEPTS'
			elif data.breaklines == False:
				passFailDict['breaklines'] = 'DOES NOT ACCEPT'
		if data.reports != None:
			if data.reports == True:
				passFailDict['reports'] = 'ACCEPTS'
			elif data.reports == False:
				passFailDict['reports'] = 'DOES NOT ACCEPT'
		if data.other != None:
			if data.other == True:
				passFailDict['other'] = 'ACCEPTS'
			elif data.other == False:
				passFailDict['other'] = 'DOES NOT ACCEPT'
		if data.dem != None:
			if data.dem == True:
				passFailDict['dem'] = 'ACCEPTS'
			elif data.dem == False:
				passFailDict['dem'] = 'DOES NOT ACCEPT'
		if data.swath != None:
			if data.swath == True:
				passFailDict['swath'] = 'ACCEPTS'
			elif data.swath == False:
				passFailDict['swath'] = 'DOES NOT ACCEPT'
		if data.classified != None:
			if data.classified == True:
				passFailDict['classified'] = 'ACCEPTS'
			elif data.classified == False:
				passFailDict['classified'] = 'DOES NOT ACCEPT'
	
	vaDataDict = {}
	for data in vaData:
		wu = data.wu
		cats = ReportVaDataCollectionCategory.objects.filter(wu = data)
		catDict = {}
		for cat in cats:
			vaData = ReportVaData.objects.get(cat = cat)
			try:
				measDict = {}
				vaData10 = ReportVaData10.objects.get(pk = vaData.id)
				cvaValsDict = {}
				cvaValsDict['ReqChkpts'] = vaData10.cvaReqChkpts
				cvaValsDict['ReqVal'] = vaData10.cvaReqValue
				cvaValsDict['RepChkpts'] = vaData10.cvaRepChkpts
				cvaValsDict['RepVal'] = vaData10.cvaRepValue
				cvaValsDict['TestChkpts'] = vaData10.cvaTestChkpts
				cvaValsDict['TestVal'] = vaData10.cvaTestValue
				measDict['CVA'] = cvaValsDict
				fvaValsDict = {}
				fvaValsDict['ReqChkpts'] = vaData10.fvaReqChkpts
				fvaValsDict['ReqVal'] = vaData10.fvaReqValue
				fvaValsDict['RepChkpts'] = vaData10.fvaRepChkpts
				fvaValsDict['RepVal'] = vaData10.fvaRepValue
				fvaValsDict['TestChkpts'] = vaData10.fvaTestChkpts
				fvaValsDict['TestVal'] = vaData10.fvaTestValue
				measDict['FVA'] = fvaValsDict
				svas = ReportSva.objects.filter(reportVaData = vaData10)
				if svas != []:
					svaList = []
					for sva in svas:
						svaDict = {}
						svaDict['ReqChkpts'] = sva.svaReqChkpts
						svaDict['ReqVal'] = sva.svaReqValue
						svaDict['RepChkpts'] = sva.svaRepChkpts
						svaDict['RepVal'] = sva.svaRepValue
						svaDict['TestChkpts'] = sva.svaTestChkpts
						svaDict['TestVal'] = sva.svaTestValue
						svaList.append(svaDict)
					measDict['SVA'] = svaList
				catDict[cat.category] = measDict

			except:
				measDict = {}
				vaData12 = ReportVaData12.objects.get(pk = vaData.id)
				nvaValsDict = {}
				nvaValsDict['ReqChkpts'] = vaData12.nvaReqChkpts
				nvaValsDict['ReqVal'] = vaData12.nvaReqValue
				nvaValsDict['RepChkpts'] = vaData12.nvaRepChkpts
				nvaValsDict['RepVal'] = vaData12.nvaRepValue
				nvaValsDict['TestChkpts'] = vaData12.nvaTestChkpts
				nvaValsDict['TestVal'] = vaData12.nvaTestValue
				measDict['NVA'] = nvaValsDict
				vvaValsDict = {}
				vvaValsDict['ReqChkpts'] = vaData12.vvaReqChkpts
				vvaValsDict['ReqVal'] = vaData12.vvaReqValue
				vvaValsDict['RepChkpts'] = vaData12.vvaRepChkpts
				vvaValsDict['RepVal'] = vaData12.vvaRepValue
				vvaValsDict['TestChkpts'] = vaData12.vvaTestChkpts
				vvaValsDict['TestVal'] = vaData12.vvaTestValue
				measDict['VVA'] = vvaValsDict
				catDict[cat.category] = measDict
			
			vaDataDict[wu] = catDict
	
	return aoiImage, inputDict, errDict, passFailDict, vaDataDict

def getSerializedPassFailData(reviewId, relVaPassFail, absVaPassFail):	
	review = Review.objects.get(pk = reviewId)
	categories = defaultdict()
	reviewWorkUnits = WorkUnit.objects.filter(review = review)
	for wu in reviewWorkUnits:
		genDelivs = Deliverable.objects.filter(workUnit = wu)
		for deliv in genDelivs:
			cat = deliv.deliverableCategory.category
			catName = None
			if cat == 1:
				catName = 'metadata'
			if cat == 2:
				catName = 'breaklines'
			if cat == 6:
				catName = 'reports'
			if cat == 7:
				catName = 'other'
			if catName:
				if not catName in categories.keys():
					categories[catName] = [str(deliv.accepted)]
				else:
					categories[catName].append(str(deliv.accepted))
		aggWuDelivs = wu.aggregatedWuDeliverable.all()
		for deliv in aggWuDelivs:
			catName = deliv.category.name
			name = ''
			if catName == 'DEM':
				name = 'dem'
			if catName == 'Classified Pointcloud':
				name = 'classified'
			if catName == 'Unclassified Swath':
				name = 'swath'
			#make catname consistent with report keys
			if not name in categories.keys():
				categories[name] = [str(deliv.accepted)]
	passFailDict = {}
	for cat, list in categories.items():
		if 'False' in list:
			passFailDict[cat] = 'DOES NOT ACCEPT'
		else:
			passFailDict[cat]= 'ACCEPTS'
	reviewPass = 'MEETS'
	for cat, result in passFailDict.items():
		if result == 'DOES NOT ACCEPT':
			reviewPass ='DOES NOT MEET'
		if cat == 'metadata':
			if result == 'ACCEPTS':
				review.metadataAccept = True
			else:
				review.metadataAccept = False
		elif cat == 'breaklines':
			if result == 'ACCEPTS':
				review.breaklinesAccept = True
			else:
				review.breaklinesAccept = False
		elif cat == 'reports':
			if result == 'ACCEPTS':
				review.reportsAccept = True
			else:
				review.reportsAccept = False
		elif cat == 'other':
			if result == 'ACCEPTS':
				review.otherAccept = True
			else:
				review.otherAccept = False
		elif cat == 'dem':
			if result == 'ACCEPTS':
				review.demAccept = True
			else:
				review.demAccept = False
		elif cat == 'classified':
			if result == 'ACCEPTS':
				review.classifiedAccept = True
			else:
				review.classifiedAccept = False
		elif cat == 'swath':
			if result == 'ACCEPTS':
				review.swathAccept = True
			else:
				review.swathAccept = False
	if str(absVaPassFail) == 'True':
		passFailDict['absVa'] = 'ACCEPTS'
		review.absVaAccept = True
	else:
		passFailDict['absVa'] = 'DOES NOT ACCEPT'
		reviewPass = 'DOES NOT MEET'
		review.absVaAccept = False
	
	if str(relVaPassFail) == 'True':
		passFailDict['relVa'] = 'ACCEPTS'
		review.relVaAccept = True
	else:
		passFailDict['relVa'] = 'DOES NOT ACCEPT'
		reviewPass = 'DOES NOT MEET'
		review.relVaAccept = False
	passFailDict['review'] = reviewPass
	if reviewPass == 'DOES NOT MEET':
		review.accepted = False
	else:
		review.accepted = True
	review.save()
	return passFailDict
	
def aggregateContractorReportData(review):
	inputDict = {}
	review = Review.objects.get(pk = review)
	workUnits = WorkUnit.objects.filter(review = review)
	workPackage = None
	genericDeliverables = []
	aggWuDelivs = []
	workUnitIds = []
	for wu in workUnits:
		workUnitIds.append(wu.workUnitId)
		workPackage = wu.workPackage
		deliverables = list(Deliverable.objects.filter(workUnit = wu))
		aggWuDeliverables = wu.aggregatedWuDeliverable.all()
		for deliv in deliverables:
			genericDeliverables.append(deliv)
		for deliv in aggWuDeliverables:
			aggWuDelivs.append(deliv)
	serializedDelivs = []
	serializedDelivErrors = []
	for deliverable in genericDeliverables:
		delivDict = {}
		delivDict['category'] = str(deliverable.deliverableCategory.name)
		if deliverable.description and deliverable.description != '' and deliverable.description != None:
			delivDict['description'] = deliverable.description
		else:
			delivDict['description'] = ''
		delivDict['accepted'] = str(deliverable.accepted)
		if deliverable.comment and deliverable.comment != '' and deliverable.comment != None:
			delivDict['summary'] = str(deliverable.comment)
		else:
			delivDict['summary'] = ''
		serializedDelivs.append(delivDict)
	for deliverable in aggWuDelivs:
		delivDict = {}
		categoryId = deliverable.category.category
		if categoryId:
			if str(categoryId) == '1':
				delivDict['category'] = 'DEM'
			if str(categoryId) == '2':
				delivDict['category'] = 'Unclassified Swath'
			if str(categoryId) == '3':
				delivDict['category'] = 'Classified Pointcloud'
		if deliverable.description and deliverable.description != '' and deliverable.description != None:
			delivDict['description'] = deliverable.description
		else:
			delivDict['description'] = ''
		if deliverable.accepted != None:
			delivDict['accepted'] = str(deliverable.accepted)
		else:
			delivDict['accepted'] = ''
		if deliverable.comment and deliverable.comment != '' and deliverable.comment != None:
			delivDict['summary'] = str(deliverable.comment)
		else:
			delivDict['summary'] = ''
		serializedDelivs.append(delivDict)
	
	inputDict['type'] = 'contractor'
	inputDict['wpName'] = workPackage.name
	inputDict['reportGenTime'] = datetime.now().strftime("%Y-%m-%d %H:%M")
	inputDict['workUnits'] = workUnitIds
	inputDict['poc'] = workPackage.poc
	#inputDict['pocPhone'] = workPackage.pocPhone
	inputDict['pocEmail'] = workPackage.pocEmail
	#inputDict['errorShp'] = ## FUTURE - FIGURE IT OUT ##
	inputDict['delivDicts'] = serializedDelivs
	return inputDict

def saveQcReport(user, inputDict, aoiImage, serializedErrorGroups, serializedPassFailData, serializedVaData):
	reportPocEmail = inputDict['pocEmail']
	reportPoc = inputDict['poc']
	reportType = inputDict['type']
	genDate = inputDict['reportGenTime']
	workUnitIds = inputDict['workUnits']
	delivDicts = inputDict['delivDicts']
	wpName = inputDict['wpName']
	reportName = ''
	
	reportNameDateTimeSplit = genDate.split(' ')
	reportNameDate = reportNameDateTimeSplit[0]
	reportNameDateSplit = reportNameDate.split('-')
	newDate = reportNameDateSplit[1] + '_' + reportNameDateSplit[2] + '_' + reportNameDateSplit[0]
	reportNameTime = reportNameDateTimeSplit[1]
	reportNameTimeSplit = reportNameTime.split(':')
	newTime = reportNameTimeSplit[0] + reportNameTimeSplit[1]
	newDateTime = newDate + '_' + newTime
	
	if reportType == 'contractor':
		reportName = 'QC_Contractor_Report_' + str(user) + '_' + newDateTime

	else:
		name = 'UNKNOWN REPORT TYPE'
	report = SavedReport.objects.create(name = reportName, createdDate = genDate, createdUser = user)
	reportData = ReportData.objects.create(report = report, wpName = wpName, type = reportType, poc = reportPoc, pocEmail = reportPocEmail)
	
	## Report Data objects
	aoiImage = ReportAoiImage.objects.create(picture = aoiImage, reportData = reportData)
	
	if workUnitIds != []:
		for id in workUnitIds:
			wuId = ReportWorkUnitId.objects.create(reportData = reportData, workUnitId = id)
			wuId.save()
			
	if delivDicts != []:
		for delivDict in delivDicts:
			category = delivDict['category']
			description = delivDict['description']
			accepted = delivDict['accepted']
			summary = delivDict['summary']
			delivData = ReportDeliverableData.objects.create(reportData =  reportData, category = category, description = description, accepted = accepted, summary = summary)
			delivData.save()

	reportData.save()
	
	## Error Group objects
	if serializedErrorGroups != {}:
		for cat, groups in serializedErrorGroups.items():
			for group in groups:
				numErrors = group['NUM_ERR']
				type = group['ERR_TYPE']
				subtype = group['ERR_SUB']
				errGroup = ReportErrorGroup.objects.create(report = report, category = cat, numErrors = numErrors, errorType = type, errorSubtype = subtype)
				images = group['IMG_LIST']
				if images != []:
					for image in images:
						errImg = ReportErrorImage.objects.create(picture = image, errorGroup = errGroup)
						errImg.save()
				errGroup.save()	
	
	if serializedPassFailData != {}:
		review = False	
		if serializedPassFailData['review'] == 'MEETS':
			review = True
		pfData = ReportPassFailData.objects.create(report = report, review = review)
		try:
			if serializedPassFailData['absVa'] == 'ACCEPTS':
				absVa = True
			else:
				absVa = False
			pfData.absVa = absVa
		except:
			pass
		try:
			if serializedPassFailData['relVa'] == 'ACCEPTS':
				relVa = True
			else:
				relVa = False
			pfData.relVa = relVa
		except:
			pass
		try:
			if serializedPassFailData['metadata'] == 'ACCEPTS':
				metadata = True
			else:
				metadata = False
			pfData.metadata = metadata
		except:
			pass
		try:
			if serializedPassFailData['breaklines'] == 'ACCEPTS':
				breaklines = True
			else:
				breaklines = False
			pfData.breaklines = breaklines
		except:
			pass
		try:
			if serializedPassFailData['reports'] == 'ACCEPTS':
				reports = True
			else:
				reports = False
			pfData.reports = reports
		except:
			pass
		try:
			if serializedPassFailData['other'] == 'ACCEPTS':
				other = True
			else:
				other = False
			pfData.other = other
		except:
			pass	
		try:
			if serializedPassFailData['dem'] == 'ACCEPTS':
				dem = True
			else:
				dem = False
			pfData.dem = dem
		except:
			pass			
		try:
			if serializedPassFailData['swath'] == 'ACCEPTS':
				swath = True
			else:
				swath = False
			pfData.swath = swath
		except:
			pass
		try:
			if serializedPassFailData['classified'] == 'ACCEPTS':
				classified = True
			else:
				classified = False
			pfData.classified = False
		except:
			pass
		pfData.save()
		
	if serializedVaData != {}:
		for workunit, vaData in serializedVaData.items():
			workPackage = workunit.workPackage
			spec = workPackage.projectSpec.name
			vaDataObj = None	
			collWu = ReportVaDataCollectionWorkUnit.objects.create(wu = str(workunit), report = report)
			for category, measure in vaData.items():
				collCat = ReportVaDataCollectionCategory.objects.create(category = category, wu = collWu)
				if str(spec) == '1.0':
					vaDataObj = ReportVaData10.objects.create(cat = collCat)
					for type, data in measure.items():
						if type == 'CVA':
							vaDataObj.cvaReqChkpts = data['ReqChkpts']
							vaDataObj.cvaReqValue = data['ReqVal']
							vaDataObj.cvaRepChkpts = data['RepChkpts']
							vaDataObj.cvaRepValue = data['RepVal']
							vaDataObj.cvaTestChkpts = data['TestChkpts']
							vaDataObj.cvaTestValue = data['TestVal']
													
						if type == 'FVA':
							vaDataObj.fvaReqChkpts = data['ReqChkpts']
							vaDataObj.fvaReqValue = data['ReqVal']
							vaDataObj.fvaRepChkpts = data['RepChkpts']
							vaDataObj.fvaRepValue = data['RepVal']
							vaDataObj.fvaTestChkpts = data['TestChkpts']
							vaDataObj.fvaTestValue = data['TestVal']
							
						if type == 'SVA':
							for sva in data:
								svaObj = ReportSva.objects.create(reportVaData = vaDataObj)
								svaObj.svaReqChkpts = sva['ReqChkpts']
								svaObj.svaReqValue = sva['ReqVal']
								svaObj.svaRepChkpts = sva['RepChkpts']
								svaObj.svaRepValue = sva['RepVal']
								svaObj.svaTestChkpts = sva['TestChkpts']
								svaObj.svaTestValue = sva['TestVal']
								svaObj.save()
						
					vaDataObj.save()
						
				if str(spec) == '1.2':
					vaDataObj = ReportVaData12.objects.create(cat = collCat)
					for type, data in measure.items():
						if type == 'NVA':
							vaDataObj.nvaReqChkpts = data['ReqChkpts']
							vaDataObj.nvaReqValue = data['ReqVal']
							vaDataObj.nvaRepChkpts = data['RepChkpts']
							vaDataObj.nvaRepValue = data['RepVal']
							vaDataObj.nvaTestChkpts = data['TestChkpts']
							vaDataObj.nvaTestValue = data['TestVal']
						if type == 'VVA':
							vaDataObj.vvaReqChkpts = data['ReqChkpts']
							vaDataObj.vvaReqValue = data['ReqVal']
							vaDataObj.vvaRepChkpts = data['RepChkpts']
							vaDataObj.vvaRepValue = data['RepVal']
							vaDataObj.vvaTestChkpts = data['TestChkpts']
							vaDataObj.vvaTestValue = data['TestVal']
						
					vaDataObj.save()	
	return report
	
	
@qcr_user_authenticated	
def retrieveSavedReport(request, report_id):
	report = SavedReport.objects.get(pk = report_id)
	aoiImage, inputDict, errorDict, passFailDict, vaDataDict = serializeReportDataObject(report)
	reportGraphics = serializeReportGraphics()
	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = 'inline; filename="contractor_report.pdf"'
	report = ReportGenerator(response, inputDict, aoiImage, errorDict, reportGraphics, passFailDict, vaDataDict)
	response = report.buildReport()
	return response
	
@qcr_user_authenticated	
def errorMapPage(request, review_id):	
	review = Review.objects.get(pk = review_id)
	return render(request, 'new_error_shapefile.html', {'review':review})
	
@qcr_user_authenticated
def getGeojson(request, review_id):
	if request.is_ajax():
		errors = []
		review = Review.objects.get(pk = review_id)
		wus = WorkUnit.objects.filter(review = review)
		for wu in wus:
			vaReq = wu.vaRequirement
			vaDatas = VaData.objects.filter(vaRequirement = vaReq)
			for vaData in vaDatas:
				delivs = AggregatedWuDeliverable.objects.filter(vaData = vaData)
				for deliv in delivs:
					type = deliv.category.name
					id = deliv.id
					errs = list(Error.objects.filter(aggregatedWuDeliverable = deliv))
					for err in errs:
						e = serializeError(err, type, id)
						if e:
							errors.append(e)
			deliverables = Deliverable.objects.filter(workUnit = wu)
			for deliverable in deliverables:
				type = deliverable.deliverableCategory.name
				id = deliverable.id
				errs = Error.objects.filter(deliverable = deliverable)
				for err in errs:
					e = serializeError(err, type, id)
					if e:
						errors.append(e)
		responseData = {}
		responseData['errors'] = errors
		return JsonResponse(responseData)
	
@qcr_user_authenticated	
def buildErrorGeopackage(request, review_id):	
	if request.method == 'POST':

		
		errors = []
		review = Review.objects.get(pk = review_id)
		wus = WorkUnit.objects.filter(review = review)
		for wu in wus:
			vaReq = wu.vaRequirement
			vaDatas = VaData.objects.filter(vaRequirement = vaReq)
			for vaData in vaDatas:
				delivs = AggregatedWuDeliverable.objects.filter(vaData = vaData)
				for deliv in delivs:
					type = deliv.category.name
					id = deliv.id
					errs = list(Error.objects.filter(aggregatedWuDeliverable = deliv))
					for err in errs:
						e = serializeError(err, type, id)
						if e:
							errors.append(e)
			deliverables = Deliverable.objects.filter(workUnit = wu)
			for deliverable in deliverables:
				type = deliverable.deliverableCategory.name
				id = deliverable.id
				errs = Error.objects.filter(deliverable = deliverable)
				for err in errs:
					e = serializeError(err, type, id)
					if e:
						errors.append(e)
		#errorShp = ErrorShapefileGenerator(errors, review.id)
		errorGpkg = ErrorGeopackageGenerator(errors, review.id)
		s, filename = errorGpkg.buildGeopackage()
		#s, filename = errorShp.buildShapefile()
		response = HttpResponse(s.getvalue(), content_type = "application/vnd.opengeospatial.geopackage+sqlite3")
		response['Content-Disposition'] = 'attachment; filename=%s' % filename
		return response

def serializeError(error, type, id):
	errorDict = {}
	try:
		errorDict['delivType'] = type
		errorDict['delivId'] = id
	except:
		return None
	try:
		if error.errorType:
			errorDict['type'] = error.errorType.name
		else:
			errorDict['type'] = 'None'
		if error.errorSubtype:
			errorDict['subtype'] = error.errorSubtype.name
		else:
			errorDict['subtype'] = 'None'
		if error.description:
			errorDict['desc'] = error.description
		else:
			errorDict['desc'] = 'None'
		if error.resolved:
			errorDict['resolved'] = str(error.resolved)
		else:
			errorDict['resolved'] = 'False'
	except:
		return None
	try:
		location = error.location
		decIndex = [i for i, n in enumerate(location) if n == '.'][0]
		latString = location[:(5 + decIndex)]
		lonString = location[(5 + decIndex):]
	
		latDecIndex = [i for i, n in enumerate(latString) if n == '.'][0]
		latSeconds = float(latString[(latDecIndex - 2):])
		latMinutes = int(latString[(latDecIndex - 4):(latDecIndex - 2)])
		latDegrees = int(latString[:(latDecIndex - 4)])
		latDecDegrees = latDegrees + (latMinutes/60) + (latSeconds/3600)
	
		lonDecIndex = [i for i, n in enumerate(lonString) if n == '.'][0]
		lonSeconds = float(lonString[(lonDecIndex - 2):])
		lonMinutes = int(lonString[(lonDecIndex - 4):(lonDecIndex - 2)])
		lonDegrees = int(lonString[:(lonDecIndex - 4)])
		lonDecDegrees = -(lonDegrees + (lonMinutes/60) + (lonSeconds/3600))
		
		errorDict['lon'] = lonDecDegrees
		errorDict['lat'] = latDecDegrees
		return errorDict
	except:
		return None
