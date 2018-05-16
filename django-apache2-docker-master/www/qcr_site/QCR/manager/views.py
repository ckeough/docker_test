## Python imports
import json
import random
import ast
import os
import sys
from datetime import datetime
from collections import defaultdict
import urllib, io
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
from manager.models import WorkPackage
from manager.models import Review
from manager.models import ReviewProgressChecklist
from manager.models import ChecklistItem
from manager.models import ChecklistCategory
from report.models import CollectionInfo
from report.models import WorkUnit
from report.models import VaRequirement
from report.models import ErrorType
from report.models import ErrorSubtype
from report.models import DeliverableCategory
from manager.models import ProjectSpecification
from manager.models import QualityLevel
from manager.models import SensorUsed
from manager.models import SensorType
from report.models import AggregatedWuDeliverableCategory
from manager.models import PointCloudClassification

from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.urls import reverse

from .decorators import qcr_user_authenticated


# Create your views here.

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
                    clItems = ChecklistItem.objects.filter(checklist=cl).order_by('placement')
                    i = 2
                    if clItems != []:
                        for item in clItems:
                            cat = item.category.name
                            catItemsDict[cat].append(item)
                            catPositionDict[cat].append(i)
                            i += 1
        else:
            ReviewProgressChecklist.objects.create(master=True)

        if settings.DEV_TOOLS:
            if catItemsDict == {} and catPositionDict == {}:

                return render(request, 'admin_home.html', {'devMode': 'True',
                                                           'user': user.username,
                                                           'qcrUsers': qcrUsers,
                                                           'usgsUsers': usgsUsers,
                                                           'reviews': reviews,
                                                           'packageList': packageList,
                                                           'qualityLevels': qualityLevels,
                                                           'sensorTypes': sensorTypes,
                                                           'sensorsUsed': sensorsUsed})
            else:
                templateDict = dict(catItemsDict)
                posDict = dict(catPositionDict)
                return render(request, 'admin_home.html', {'devMode': 'True',
                                                           'user': user.username,
                                                           'qcrUsers': qcrUsers,
                                                           'usgsUsers': usgsUsers,
                                                           'reviews': reviews,
                                                           'packageList': packageList,
                                                           'qualityLevels': qualityLevels,
                                                           'sensorTypes': sensorTypes,
                                                           'sensorsUsed': sensorsUsed,
                                                           'checklistItems': templateDict,
                                                           'checklistPositions': posDict})
        else:
            if catItemsDict == {} and catPositionDict == {}:
                return render(request, 'admin_home.html', {'user': user.username,
                                                           'qcrUsers': qcrUsers,
                                                           'usgsUsers': usgsUsers,
                                                           'reviews': reviews,
                                                           'packageList': packageList,
                                                           'qualityLevels': qualityLevels,
                                                           'sensorTypes': sensorTypes,
                                                           'sensorsUsed': sensorsUsed})
            else:
                templateDict = dict(catItemsDict)
                posDict = dict(catPositionDict)
                return render(request, 'admin_home.html', {'user': user.username,
                                                           'qcrUsers': qcrUsers,
                                                           'usgsUsers': usgsUsers,
                                                           'reviews': reviews,
                                                           'packageList': packageList,
                                                           'qualityLevels': qualityLevels,
                                                           'sensorTypes': sensorTypes,
                                                           'sensorsUsed': sensorsUsed,
                                                           'checklistItems': templateDict,
                                                           'checklistPositions': posDict})

    else:
        review_list = Review.objects.filter(user=user)
        return render(request, 'user_home.html', {'review_list': review_list, 'user': user.username})

## View that handles activating users from the admin page.
@qcr_user_authenticated
def addUser(request):
    if request.is_ajax():
        if request.method == "POST":
            responseData = {}
            delivDict = {}
            deliv = None
            jsonData = json.loads(request.body.decode('utf-8'))
            username = jsonData['user'][0]
            userToAdd = User.objects.get(username=username)
            qcrGroup = Group.objects.get(name='qcr_user')
            userToAdd.groups.add(qcrGroup)
            userToAdd.save()
            users = User.objects.all()
            qcrUsers = []
            usgsUsers = []
            for u in users:
                groups = u.groups.all()
                for g in groups:
                    if g.name == 'qcr_user':
                        qcrUsers.append(u.username)
                if u.username not in qcrUsers and not u.is_staff:
                    usgsUsers.append(u.username)
            responseData['qcrUsers'] = qcrUsers
            responseData['usgsUsers'] = usgsUsers
            responseData['success'] = 'True'
            return JsonResponse(responseData)


## View for handling deactivating user accounts
@qcr_user_authenticated
def removeUser(request):
    if request.is_ajax():
        if request.method == "POST":
            responseData = {}
            delivDict = {}
            deliv = None
            jsonData = json.loads(request.body.decode('utf-8'))
            username = jsonData['user'][0]
            userToRemove = User.objects.get(username=username)
            qcrGroup = Group.objects.get(name='qcr_user')
            qcrGroup.user_set.remove(userToRemove)
            qcrGroup.save()
            users = User.objects.all()
            qcrUsers = []
            usgsUsers = []
            for u in users:
                groups = u.groups.all()
                for g in groups:
                    if g.name == 'qcr_user':
                        qcrUsers.append(u.username)
                if u.username not in qcrUsers and not u.is_staff:
                    usgsUsers.append(u.username)
            responseData['qcrUsers'] = qcrUsers
            responseData['usgsUsers'] = usgsUsers
            responseData['success'] = 'True'
            return JsonResponse(responseData)

@qcr_user_authenticated
def addChecklistItem(request):
    if request.is_ajax():
        if request.method == "POST":
            jsonData = json.loads(request.body.decode('utf-8'))
            checklist = ReviewProgressChecklist.objects.get(master=True)
            category = ChecklistCategory.objects.get(name=jsonData['category'])
            items = ChecklistItem.objects.filter(checklist=checklist, category=category)
            for item in items:
                placement = str(item.placement)
                if placement == jsonData['placement']:
                    for it in items:
                        if it.placement >= int(placement):
                            it.placement = it.placement + 1
                            it.save()
                    break
            newItem = ChecklistItem.objects.create(checklist=checklist, category=category,
                                                   placement=jsonData['placement'],
                                                   name=jsonData['description'], complete=False)
            ## Clone new item for each existing checklist
            checklists = ReviewProgressChecklist.objects.all()
            for cl in checklists:
                if cl.master == True:
                    continue
                else:
                    items = ChecklistItem.objects.filter(checklist=cl, category=category)
                    for item in items:
                        placement = item.placement
                        if placement == jsonData['placement']:
                            for it in items:
                                if it.placement >= placement:
                                    it.placement = it.placement + 1
                                    it.save()
                            break

                    ChecklistItem.objects.create(checklist=cl, category=category,
                                                 placement=jsonData['placement'], name=jsonData['description'],
                                                 complete=False)

            catPositionDict = defaultdict(list)
            categories = ChecklistCategory.objects.all()
            for cat in categories:
                checklist = ReviewProgressChecklist.objects.get(master=True)
                items = ChecklistItem.objects.filter(checklist=checklist, category=cat)
                catPositionDict[cat.name].append(1)
                i = 2
                if items != []:
                    for item in items:
                        cat = item.category.name
                        catPositionDict[cat].append(i)
                        i += 1
            items = ChecklistItem.objects.filter(checklist=checklist, category=category).order_by('placement')
            html = render_to_string('checklistTabContent.html', {'category': category.name, 'items': items,
                                                                 'checklistPositions': dict(catPositionDict)})
            responseData = {}
            responseData['html'] = html
            return JsonResponse(responseData)

@qcr_user_authenticated
def deleteChecklistItem(request):
    if request.is_ajax():
        if request.method == "POST":
            jsonData = json.loads(request.body.decode('utf-8'))
            checklist = ReviewProgressChecklist.objects.get(master=True)
            category = None
            categories = ChecklistCategory.objects.all()
            for cat in categories:
                if cat.name.startswith(jsonData['category']):
                    category = cat
            placement = jsonData['placement']
            itemsToDelete = ChecklistItem.objects.filter(category=category, placement=placement)
            for item in itemsToDelete:
                item.delete()

            clItems = ChecklistItem.objects.filter(checklist=checklist)
            for item in clItems:
                if item.placement > int(jsonData['placement']):
                    item.placement = item.placement - 1
                    item.save()

            catPositionDict = defaultdict(list)
            categories = ChecklistCategory.objects.all()
            for cat in categories:
                checklist = ReviewProgressChecklist.objects.get(master=True)
                items = ChecklistItem.objects.filter(checklist=checklist, category=cat)
                catPositionDict[cat.name].append(1)
                i = 2
                if items != []:
                    for item in items:
                        cat = item.category.name
                        catPositionDict[cat].append(i)
                        i += 1

            items = ChecklistItem.objects.filter(checklist=checklist, category=category).order_by('placement')
            html = render_to_string('checklistTabContent.html', {'category': category.name, 'items': items,
                                                                 'checklistPositions': dict(catPositionDict)})
            responseData = {}
            responseData['html'] = html
            return JsonResponse(responseData)

@qcr_user_authenticated
def updateChecklist(request):
    if request.is_ajax():
        if request.method == "POST":
            jsonData = json.loads(request.body.decode('utf-8'))
            reviewId = jsonData['review']
            review = Review.objects.get(pk=reviewId)
            checklist = ReviewProgressChecklist.objects.get(review=review)
            categories = ChecklistCategory.objects.all()
            category = None
            for cat in categories:
                if cat.name.startswith(jsonData['category']):
                    category = cat
            placement = int(jsonData['placement'])

            item = ChecklistItem.objects.get(checklist=checklist, category=category, placement=placement)

            if jsonData['complete'] == 'True':
                item.complete = True
            else:
                item.complete = False

            item.save()

            responseData = {}
            responseData['success'] = 'true'
            return JsonResponse(responseData)

@qcr_user_authenticated
def getChecklistModal(request, review_id):
    review = Review.objects.get(pk=review_id)
    checklist = ReviewProgressChecklist.objects.get(review=review)
    catItemsDict = defaultdict(list)
    categories = ChecklistCategory.objects.all()
    for cat in categories:
        catItemsDict[cat.name] = []

    clItems = ChecklistItem.objects.filter(checklist=checklist).order_by('placement')
    if clItems != []:
        for item in clItems:
            cat = item.category.name
            catItemsDict[cat].append(item)
    checklistItems = {}
    for key, value in catItemsDict.items():
        checklistItems[key] = value
    html = render_to_string('checklist_modal.html', {'review': review, 'checklistItems': checklistItems})
    responseData = {}
    responseData['html'] = html
    return JsonResponse(responseData)

## Admin View for listing all reviews associated with an individual user
@qcr_user_authenticated
def adminListUserReviews(request, user):
    userObj = User.objects.get(username=user)
    review_list = Review.objects.filter(user=userObj)
    return render(request, 'admin_userReviewList.html', {'review_list': review_list, 'user': user})


## Admin View for handling adding users from qcr_user group
@qcr_user_authenticated
def addUser(request):
    if request.is_ajax():
        if request.method == "POST":
            responseData = {}
            delivDict = {}
            deliv = None
            jsonData = json.loads(request.body.decode('utf-8'))
            username = jsonData['user'][0]
            userToAdd = User.objects.get(username=username)
            qcrGroup = Group.objects.get(name='qcr_user')
            userToAdd.groups.add(qcrGroup)
            userToAdd.save()
            users = User.objects.all()
            qcrUsers = []
            usgsUsers = []
            for u in users:
                groups = u.groups.all()
                for g in groups:
                    if g.name == 'qcr_user':
                        qcrUsers.append(u.username)
                if u.username not in qcrUsers and not u.is_staff:
                    usgsUsers.append(u.username)
            responseData['qcrUsers'] = qcrUsers
            responseData['usgsUsers'] = usgsUsers
            responseData['success'] = 'True'
            return JsonResponse(responseData)


## Admin View for handling removing	users from qcr_user group
@qcr_user_authenticated
def removeUser(request):
    if request.is_ajax():
        if request.method == "POST":
            responseData = {}
            delivDict = {}
            deliv = None
            jsonData = json.loads(request.body.decode('utf-8'))
            username = jsonData['user'][0]
            userToRemove = User.objects.get(username=username)
            qcrGroup = Group.objects.get(name='qcr_user')
            qcrGroup.user_set.remove(userToRemove)
            qcrGroup.save()
            users = User.objects.all()
            qcrUsers = []
            usgsUsers = []
            for u in users:
                groups = u.groups.all()
                for g in groups:
                    if g.name == 'qcr_user':
                        qcrUsers.append(u.username)
                if u.username not in qcrUsers and not u.is_staff:
                    usgsUsers.append(u.username)
            responseData['qcrUsers'] = qcrUsers
            responseData['usgsUsers'] = usgsUsers
            responseData['success'] = 'True'
            return JsonResponse(responseData)


## Admin View that handles PTS Work Package Queries, supports searching PTS on State Code and Work Package Name. Submit
## a blank form to retrieve all activate Work Packages
@qcr_user_authenticated
def searchWps(request):
    if request.is_ajax():
        responseData = {}
        try:
            jsonData = json.loads(request.body.decode('utf-8'))
            name = jsonData['name']
            state = jsonData['state']
        except:
            responseData['fail'] = 'JSON'
            return JsonResponse(responseData)

        cursor = connections['pts'].cursor()

        wpList = []
        if name == '' and state != '':
            try:
                cursor.execute(
                    "SELECT public.work_package.name, public.work_package.id, public.work_package.state_code FROM public.work_package WHERE public.work_package.state_code = '{0}' AND public.work_package.track=5635 AND public.work_package.archived=false ORDER BY public.work_package.name ASC".format(
                        state))
            except:
                print('PTS CONNECTION FAILED - NEED FAILURE TEMPLATE TO RETURN')
        else:
            try:
                cursor.execute(
                    "SELECT public.work_package.name, public.work_package.id, public.work_package.state_code FROM public.work_package WHERE ( public.work_package.name LIKE %s OR public.work_package.state_code = %s ) AND public.work_package.track=5635 AND public.work_package.archived=false ORDER BY public.work_package.name ASC",
                    ('%' + name + '%', state))
            except:
                print('PTS CONNECTION FAILED - NEED FAILURE TEMPLATE TO RETURN')

        for row in cursor:
            if not WorkPackage.objects.filter(workPackageId=row[1]).exists():
                wpList.append((row[0], row[1], row[2]))
        cursor.close()

        html = "<select id = 'wpManagerSelect' multiple = 'multiple'>"
        for wp, id, state in wpList:
            html += '<option value=' + str(id) + '>' + str(wp) + '</option>'
        html += '</select><br>'
        responseData = {'html': html}
        return JsonResponse(responseData)


## Admin View for handling the creation of Work Package objects in QCR that correspond to selected Work Packages from PTS
@qcr_user_authenticated
def addWpFromPts(request):
    if request.is_ajax():
        jsonData = json.loads(request.body.decode('utf-8'))
        selection = jsonData['selection']
        if selection:
            packageList = WorkPackage.objects.all()
            wpList = []
            wpSelected = []
            for wpid in selection:
                try:
                    wpCur = connections['pts'].cursor()
                    wpCur.execute(
                        "SELECT wp.id, wp.name, wp.description, m.name, wp.review_specification, c.name, c.email, c.first_name, c.last_name FROM public.work_package wp, public.work_package_contact wpc, public.contact c, public.mechanism m WHERE wp.id='{0}' AND wp.id=wpc.work_package AND wpc.contact=c.id AND m.id=wp.mechanism".format(
                            wpid))
                    record = wpCur.fetchone()
                    if (record):
                        wp = WorkPackage(workPackageId=record[0],
                                         name=record[1],
                                         description=record[2],
                                         type=record[3],
                                         vendor=record[5],
                                         pocEmail=record[6],
                                         poc=record[7] + " " + record[8])
                    else:
                        wpCur.execute(
                            "SELECT public.work_package.id, public.work_package.name, public.work_package.description, public.mechanism.name, public.work_package.review_specification FROM public.work_package, public.mechanism WHERE public.work_package.id = '{0}' AND public.mechanism.id = public.work_package.mechanism".format(
                                wpid))
                        record = wpCur.fetchone()
                        if (record):
                            wp = WorkPackage(workPackageId=record[0],
                                             name=record[1],
                                             description=record[2],
                                             type=record[3],
                                             poc="None",
                                             vendor="None",
                                             pocEmail="None"
                                             )
                    if record[4]:
                        if "2" in record[4]:
                            wp.projectSpec = ProjectSpecification.objects.get(name="1.2")
                        else:
                            wp.projectSpec = ProjectSpecification.objects.get(name="1.0")
                    wp.save()
                    addDefaultClassifications(wp)
                    wpCur.close()
                except:
                    continue
            return JsonResponse({'success': 'True'})
        else:
            return JsonResponse({'success': 'False'})


## Admin view that handles the creation of new Quality Level objects
@qcr_user_authenticated
def addQualityLevel(request):
    jsonData = json.loads(request.body.decode('utf-8'))
    qualityLevelName = jsonData['qualityLevel']
    qualityLevel = QualityLevel.objects.create(name=qualityLevelName)
    qualityLevel.save()
    responseData = {}
    responseData['success'] = 'CREATED QUALITY LEVEL: ' + qualityLevelName
    return JsonResponse(responseData)


## Admin view that handles the deletion of Quality Level objects
@qcr_user_authenticated
def deleteQualityLevel(request):
    jsonData = json.loads(request.body.decode('utf-8'))
    qualityLevelName = jsonData['qualityLevel']
    qualityLevel = QualityLevel.objects.get(name=qualityLevelName)
    collInfos = CollectionInfo.objects.filter(qualityLevel=qualityLevel)
    for ci in collInfos:
        ci.delete()
    qualityLevel.delete()
    qls = list(QualityLevel.objects.all())
    if qls == []:
        reviews = Review.objects.all()
        for review in reviews:
            review.delete()
    responseData = {}
    responseData['success'] = 'Quality Level ' + qualityLevelName + ' deleted.'
    return JsonResponse(responseData)


## Admin view that handles the creation of new SensorType objects
@qcr_user_authenticated
def addSensorType(request):
    jsonData = json.loads(request.body.decode('utf-8'))
    sensorTypeName = jsonData['sensorType']
    sensorType = SensorType.objects.create(name=sensorTypeName)
    sensorType.save()
    responseData = {}
    responseData['success'] = 'CREATED "SENSOR TYPE": ' + sensorTypeName
    return JsonResponse(responseData)


## Admin view that handles the deletion of SensorType objects
@qcr_user_authenticated
def deleteSensorType(request):
    jsonData = json.loads(request.body.decode('utf-8'))
    sensorTypeName = jsonData['sensorType']
    sensorType = SensorType.objects.get(name=sensorTypeName)
    sensorType.delete()
    responseData = {}
    responseData['success'] = 'Sensor Type ' + sensorTypeName + ' deleted.'
    return JsonResponse(responseData)


## Admin view that handles the creation of new SensorUsed objects
@qcr_user_authenticated
def addSensorUsed(request):
    jsonData = json.loads(request.body.decode('utf-8'))
    sensorUsedName = jsonData['sensorUsed']
    sensorUsed = SensorUsed.objects.create(name=sensorUsedName)
    sensorUsed.save()
    responseData = {}
    responseData['success'] = 'CREATED "SENSOR USED": ' + sensorUsedName
    return JsonResponse(responseData)


## Admin view that handles the deletion of SensorUsed objects
@qcr_user_authenticated
def deleteSensorUsed(request):
    jsonData = json.loads(request.body.decode('utf-8'))
    sensorUsedName = jsonData['sensorUsed']
    sensorUsed = SensorUsed.objects.get(name=sensorUsedName)
    sensorUsed.delete()
    responseData = {}
    responseData['success'] = 'Sensor Used ' + sensorUsedName + ' deleted.'
    return JsonResponse(responseData)


## Admin view that handles the creation of new ProjectSpec objects
@qcr_user_authenticated
def addProjectSpec(request):
    jsonData = json.loads(request.body.decode('utf-8'))
    projectSpecName = jsonData['projectSpec']
    projectSpec = ProjectSpecification.objects.create(name=projectSpecName)
    projectSpec.save()
    projectSpecs = ProjectSpecification.objects.values_list('name', flat=True)
    responseData = {}
    responseData['values'] = list(projectSpecs)
    return JsonResponse(responseData)


## Admin view that handles the deletion of ProjectSpec objects
@qcr_user_authenticated
def deleteProjectSpec(request):
    jsonData = json.loads(request.body.decode('utf-8'))
    projectSpecName = jsonData['projectSpec']
    projectSpec = ProjectSpecification.objects.get(name=projectSpecName)
    projectSpec.delete()
    projectSpecs = ProjectSpecification.objects.values_list('name', flat=True)
    responseData = {}
    responseData['values'] = list(projectSpecs)
    return JsonResponse(responseData)


@qcr_user_authenticated
def adminHomePage(request, tabId=None, userFilter=None):
    user = request.user
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
    if settings.DEV_TOOLS:
        if userFilter:
            return render(request, 'admin_home.html',
                          {'devMode': 'True', 'userFilter': userFilter, 'tabId': tabId, 'user': user.username,
                           'qcrUsers': qcrUsers, 'usgsUsers': usgsUsers, 'reviews': reviews, 'packageList': packageList,
                           'qualityLevels': qualityLevels, 'sensorTypes': sensorTypes, 'sensorsUsed': sensorsUsed})
        else:
            return render(request, 'admin_home.html',
                          {'devMode': 'True', 'tabId': tabId, 'user': user.username, 'qcrUsers': qcrUsers,
                           'usgsUsers': usgsUsers, 'reviews': reviews, 'packageList': packageList,
                           'qualityLevels': qualityLevels, 'sensorTypes': sensorTypes, 'sensorsUsed': sensorsUsed})
    else:
        if userFilter:
            return render(request, 'admin_home.html',
                          {'userFilter': userFilter, 'tabId': tabId, 'user': user.username, 'qcrUsers': qcrUsers,
                           'usgsUsers': usgsUsers, 'reviews': reviews, 'packageList': packageList,
                           'qualityLevels': qualityLevels, 'sensorTypes': sensorTypes, 'sensorsUsed': sensorsUsed})
        else:
            return render(request, 'admin_home.html',
                          {'tabId': tabId, 'user': user.username, 'qcrUsers': qcrUsers, 'usgsUsers': usgsUsers,
                           'reviews': reviews, 'packageList': packageList, 'qualityLevels': qualityLevels,
                           'sensorTypes': sensorTypes, 'sensorsUsed': sensorsUsed})


@qcr_user_authenticated
def adminListReviews(request):
    if request.is_ajax():
        if request.method == "POST":
            jsonData = json.loads(request.body.decode('utf-8'))
            user = User.objects.get(username=jsonData['user'])
            userReviews = Review.objects.filter(user=user)
            qcrUsers = []
            users = User.objects.all()
            for u in users:
                groups = u.groups.all()
                for g in groups:
                    if g.name == 'qcr_user':
                        qcrUsers.append(u.username)
            html = render_to_string('admin_ReviewTabContent.html',
                                    {'userFilter': True, 'reviewUser': user.username, 'userReviews': userReviews,
                                     'qcrUsers': qcrUsers})
        else:
            reviews = Review.objects.all()
            qcrUsers = []
            users = User.objects.all()
            for u in users:
                groups = u.groups.all()
                for g in groups:
                    if g.name == 'qcr_user':
                        qcrUsers.append(u.username)
            html = render_to_string('admin_ReviewTabContent.html', {'reviews': reviews, 'qcrUsers': qcrUsers})
        responseData = {}
        responseData['html'] = html
        return JsonResponse(responseData)


## Admin view that handles loading all eligible Work Units from a specified WorkPackage, and displays them in a MultiSelect
## Box used for Review Creation.
@qcr_user_authenticated
def adminPopulateReviewWuSelect(request):
    if request.is_ajax():
        if request.method == "POST":
            responseData = {}
            jsonData = json.loads(str(request.body.decode('utf-8')))
            workPackage = WorkPackage.objects.get(pk=jsonData['workPackageId'])
            wpid = workPackage.workPackageId
            workUnits = list(WorkUnit.objects.filter(workPackage=workPackage))
            wus = []
            if not settings.DEV_TOOLS:
                cursor = connections['pts'].cursor()
                cursor.execute(
                    "SELECT public.work_unit.id, public.work_unit.name FROM public.work_unit WHERE public.work_unit.work_package = {0} ORDER BY public.work_unit.name ASC".format(
                        wpid))
                for row in cursor:
                    if not WorkUnit.objects.filter(workUnitId=row[0]).exists():
                        wus.append(str(row[0]) + ':' + str(row[1]))
            for wu in workUnits:
                try:
                    review = wu.review
                    id = review.id
                except:
                    wus.append(str(wu.workUnitId) + ':' + str(wu.name))
            responseData['result'] = 'success'
            responseData['wus'] = wus
            return JsonResponse(responseData)


@qcr_user_authenticated
def adminReviewDetail(request, review_id=None, userFilter=None):
	if request.is_ajax():

		jsonData = json.loads(str(request.body.decode('utf-8')))
		user = User.objects.get(username=jsonData['user'])
		review = Review.objects.get(pk=jsonData['reviewId'])
		name = jsonData['name']
		jsonWorkPackage = None
		if name != review.name:
			review.name = name
		try:
			if jsonData['wpId']:
				jsonWorkPackage = WorkPackage.objects.get(pk=jsonData['wpId'])
		except:
			pass
		if user != review.user:
			review.user = user
			review.save()
		## Gets assigned wus for pkg
		workUnits = list(WorkUnit.objects.filter(review=review))
		currentWorkPackage = None
		for wu in workUnits:
			currentWorkPackage = wu.workPackage
		jsonWorkUnitIds = []
		try:
			if jsonData['wus']:
				jsonWorkUnitIds = jsonData['wus']
		except:
			pass
        # Improve query or validation to avoid double iteration (work package should be the same for all work units associated with the review)
		if jsonWorkUnitIds != []:
			if currentWorkPackage != jsonWorkPackage:
				for wu in workUnits:
					if wu.review == review:
						wu.review = None
						wu.save()
			for jwu in jsonWorkUnitIds:
				wu = None
				try:
					wu = WorkUnit.objects.get(pk=jwu)
				except:
					if not settings.DEV_TOOLS:
						cursor = connections['pts'].cursor()
						sql = "SELECT public.work_unit.name FROM public.work_unit WHERE public.work_unit.id = {0}".format(str(jwu))
						cursor.execute(sql)
						for row in cursor:
							wu = WorkUnit.objects.create(name=row[0], workUnitId=jwu, status='active',workPackage=currentWorkPackage)
					else:
						continue
				wu.review = review
				wu.save()
		
		wus = list(WorkUnit.objects.filter(review = review))
		review.save()
		responseData = {}
		responseData['result'] = 'success'
		return JsonResponse(responseData)
	else:
		review = get_object_or_404(Review, pk=review_id)
		assignedUser = review.user.username
		users = User.objects.all()
		nonAdminUsers = []
		for user in users:
			if not user.is_staff:
				nonAdminUsers.append(user)
		wus = WorkUnit.objects.filter(review=review)
		selectedWorkPackage = None
		relWus = []
		for wu in wus:
			selectedWorkPackage = wu.workPackage
			relWus.append(wu)
		workUnits = WorkUnit.objects.filter(workPackage=selectedWorkPackage)
		wus = []
		for workUnit in workUnits:
			try:
				review = workUnit.review
				id = review.id
			except:
				wus.append(workUnit)
		wps = WorkPackage.objects.all()
		resWps = []
		for wp in wps:
			wpid = wp.workPackageId
			workUnits = list(WorkUnit.objects.filter(workPackage=wp))
			if not settings.DEV_TOOLS:
				cursor = connections['pts'].cursor()
				cursor.execute("SELECT public.work_unit.id, public.work_unit.name, public.work_unit.date_created FROM public.work_unit WHERE public.work_unit.work_package = {0} ORDER BY public.work_unit.name ASC".format(wpid))
				for row in cursor:
					if not WorkUnit.objects.filter(workUnitId=row[0]).exists():
						if not wp in resWps:
							resWps.append(wp)
			for wu in workUnits:
				try:
					review = wu.review
					id = review.id
				except:
					if not wp in resWps:
						resWps.append(wp)
		review = get_object_or_404(Review, pk=review_id)
		if userFilter:
			return render(request, 'admin_review_detail.html',
							{'userFilter': 'True', 'id': review_id, 'review': review, 'wps': resWps,
							'selectedWp': selectedWorkPackage, 'workUnits': wus, 'relWus': relWus,
							'assignedUser': assignedUser, 'users': nonAdminUsers})
		else:
			return render(request, 'admin_review_detail.html',
							{'id': review_id, 'review': review, 'wps': resWps, 'selectedWp': selectedWorkPackage,
							'workUnits': wus, 'relWus': relWus, 'assignedUser': assignedUser, 'users': nonAdminUsers})


@qcr_user_authenticated
def adminGetWorkPackages(request):
    responseData = {}
    resWps = []
    wps = WorkPackage.objects.all()
    for wp in wps:
        wpid = wp.workPackageId
        workUnits = list(WorkUnit.objects.filter(workPackage=wp))
        if not settings.DEV_TOOLS:
            cursor = connections['pts'].cursor()
            cursor.execute(
                "SELECT public.work_unit.id, public.work_unit.name, public.work_unit.date_created FROM public.work_unit WHERE public.work_unit.work_package = {0} ORDER BY public.work_unit.name ASC".format(
                    wpid))
            for row in cursor:
                if not WorkUnit.objects.filter(workUnitId=row[0]).exists():
                    resWps.append(wp)
                    break
        if resWps == []:
            for wu in workUnits:
                try:
                    review = wu.review
                    id = review.id
                except:
                    resWps.append(wp)
                    break
    if resWps != []:
        responseData['result'] = 'success'
    else:
        responseData['result'] = 'failure'
    return JsonResponse(responseData)


@qcr_user_authenticated
def adminCreateReview(request):
    if request.is_ajax():
        if request.method == "POST":
            responseData = {}
            jsonData = json.loads(str(request.body.decode('utf-8')))
            user = User.objects.get(username=jsonData['user'])
            name = jsonData['name']

            review = Review.objects.create(name=name, user=user)
            reviewChecklist = ReviewProgressChecklist.objects.create(master=False, review=review)

            masterChecklist = ReviewProgressChecklist.objects.get(master=True)
            masterItems = ChecklistItem.objects.filter(checklist=masterChecklist)

            for item in masterItems:
                category = item.category
                placement = item.placement
                name = item.name
                newItem = ChecklistItem.objects.create(checklist=reviewChecklist, category=category,
                                                       placement=placement, name=name, complete=False)

            workPackage = WorkPackage.objects.get(pk=jsonData['workPackage'])
            wus = jsonData['wus']
            for wu in wus:
                workUnit = None
                try:
                    workUnit = get_object_or_404(WorkUnit, workUnitId=wu)
                except:
                    if not settings.DEV_TOOLS:
                        ##Check for Quality Level
                        try:
                            qlcursor = connections['pts'].cursor()
                            qlquery = "SELECT public.tag.value FROM public.tag, public.work_package_tags WHERE public.work_package_tags.work_package = {0} AND public.tag.id = public.work_package_tags.tags AND public.tag.type = 6494".format(
                                workPackage.workPackageId)
                            qlcursor.execute(qlquery)
                            qlresult = qlcursor.fetchone()[0]
                            ql = QualityLevel.objects.get(name=qlresult)
                        except:
                            pass
                        ##Fetch WU Info
                        cursor = connections['pts'].cursor()
                        sql = "SELECT public.work_unit.name FROM public.work_unit WHERE public.work_unit.id = {0}".format(wu)
                        cursor.execute(sql)
                        for row in cursor:
                            try:
                                workUnit = WorkUnit.objects.create(name=row[0], workUnitId=wu, status='active',
                                                                   workPackage=workPackage, qualityLevel=ql)
                            except:
                                workUnit = WorkUnit.objects.create(name=row[0], workUnitId=wu, status='active',
                                                                   workPackage=workPackage)
                    else:
                        continue
                workUnit.review = review
                workUnit.save()
            responseData['result'] = 'success'
            responseData['review'] = str(review.id)
            return JsonResponse(responseData)
    else:
        resWps = []
        allUsers = User.objects.all()
        users = []
        for user in allUsers:
            if not user.is_staff:
                if len(user.groups.filter(name='qcr_user')) > 0:
                    users.append(user.username)
        wps = WorkPackage.objects.all()
        for wp in wps:
            wpid = wp.workPackageId
            workUnits = list(WorkUnit.objects.filter(workPackage=wp))
            if not settings.DEV_TOOLS:
                cursor = connections['pts'].cursor()
                cursor.execute(
                    "SELECT public.work_unit.id, public.work_unit.name, public.work_unit.date_created FROM public.work_unit WHERE public.work_unit.work_package = {0} ORDER BY public.work_unit.name ASC".format(
                        wpid))
                for row in cursor:
                    if not WorkUnit.objects.filter(workUnitId=row[0]).exists():
                        if not wp in resWps:
                            resWps.append(wp)
            for wu in workUnits:
                try:
                    review = wu.review
                    id = review.id
                except:
                    if not wp in resWps:
                        resWps.append(wp)
        return render(request, 'admin_review_create.html', {'wps': resWps, 'users': users})


@qcr_user_authenticated
def adminRemoveWorkUnit(request):
	if request.is_ajax():
		responseData = {}
		if request.method == "POST":
			jsonData = json.loads(str(request.body.decode('utf-8')))
			workUnit = WorkUnit.objects.get(pk=jsonData['workUnitId'])
			review = workUnit.review
			reviewId = review.id
			workUnit.review = None
			workUnit.save()
			responseData['result'] = 'success'
			responseData['reviewId'] = str(reviewId)
			return JsonResponse(responseData)


@qcr_user_authenticated
def adminDeleteReview(request, review_id):
    if request.is_ajax():
        if request.method == "POST":
            responseData = {}
            review = get_object_or_404(Review, pk=review_id)
            wus = WorkUnit.objects.filter(review=review)
            for wu in wus:
                wu.delete()
            reviewId = review.id
            review.delete()
            responseData['result'] = 'success'
            return JsonResponse(responseData)


@qcr_user_authenticated
def adminWpDetail(request, wpid):
    wp = WorkPackage.objects.get(workPackageId=wpid)
    specList = ProjectSpecification.objects.all()
    currentUser = request.user
    if request.method == 'POST':
        if 'spec' in request.POST:
            spec = request.POST.get('spec')
            wp.projectSpec = ProjectSpecification.objects.get(name=spec)
            wp.save()
    freeWus = []
    assignedWus = []
    wus = WorkUnit.objects.filter(workPackage=wp).order_by('review')
    for wu in wus:
        if wu.review:
            assignedWus.append(wu)
        else:
            freeWus.append(wu)
    if not settings.DEV_TOOLS:
        try:
            # also need work units that have no review
            wus = WorkUnit.objects.filter(workPackage=wp)
            cursor = connections['pts'].cursor()
            cursor.execute(
                "SELECT public.work_unit.id, public.work_unit.name, public.work_unit.date_created FROM public.work_unit WHERE public.work_unit.work_package = {0} ORDER BY public.work_unit.name ASC".format(
                    wpid))
            for row in cursor:
                if not WorkUnit.objects.filter(workUnitId=row[0]).exists():
                    freeWus.append((row[0], row[1], row[2]))
            return render(request, 'admin_workPackage_detail.html',
                          {'wp': wp, 'freeWus': freeWus, 'assignedWus': assignedWus, 'specList': specList})
        except:
            print('FAILED TO CONNECT TO PTS - SHOW A FAILURE TEMPLATE')
    return render(request, 'admin_workPackage_detail.html',
                  {'devMode': 'True', 'wp': wp, 'assignedWus': assignedWus, 'freeWus': freeWus})


#####################
## Developer Views ##
#####################
@qcr_user_authenticated
def devCreateWorkPackage(request):
    if request.is_ajax():
        if request.method == "POST":
            responseData = {}
            jsonData = json.loads(str(request.body.decode('utf-8')))
            wpId = jsonData['workPackageId']
            workPackage = WorkPackage.objects.create(workPackageId=wpId)
            workPackage = buildWorkPackage(jsonData, workPackage)
            wusToAdd = int(jsonData['wusToAdd'])
            i = 1
            while i <= wusToAdd:
                workUnitId = random.randint(100000, 9999999)
                existingWus = WorkUnit.objects.all()
                workUnitId = recurseWorkUnitIds(workUnitId, existingWus)
                wuName = 'TEST WORK UNIT ' + str(workUnitId)
                wu = WorkUnit.objects.create(workUnitId=workUnitId, workPackage=workPackage, name=wuName)
                i += 1
            responseData = {}
            responseData['result'] = 'success'
            responseData['workPackageId'] = workPackage.workPackageId
            return JsonResponse(responseData)
    else:
        projectSpecs = ProjectSpecification.objects.all()
        return render(request, 'dev_workPackage_create.html', {'projectSpecs': projectSpecs})


@qcr_user_authenticated
def devDeleteWorkPackage(request):
    if request.is_ajax():
        if request.method == "POST":
            responseData = {}
            jsonData = json.loads(str(request.body.decode('utf-8')))
            wpId = jsonData['workPackageId']
            workPackage = WorkPackage.objects.get(pk=wpId)
            wus = WorkUnit.objects.filter(workPackage=workPackage)
            reviews = []
            for wu in wus:
                review = wu.review
                try:
                    if review.id not in reviews:
                        reviews.append(review.id)
                except:
                    continue
            for id in reviews:
                review = Review.objects.get(pk=id)
                review.delete()
            workPackage.delete()
            return JsonResponse({'success': 'True'})


@qcr_user_authenticated
def devCreateWorkUnit(request, workPackage_id):
    if request.is_ajax():
        responseData = {}
        workPackage = WorkPackage.objects.get(pk=workPackage_id)
        workUnitId = random.randint(100000, 9999999)
        existingWus = WorkUnit.objects.all()
        workUnitId = recurseWorkUnitIds(workUnitId, existingWus)
        wuName = 'TEST WORK UNIT ' + str(workUnitId)
        wu = WorkUnit.objects.create(workUnitId=workUnitId, workPackage=workPackage, name=wuName)
        wus = list(WorkUnit.objects.filter(workPackage=workPackage))
        assignedWus = []
        freeWus = []
        for wu in wus:
            if wu.review:
                assignedWus.append(wu)
            else:
                freeWus.append(wu)
        wpDetailHtml = render_to_string('admin_workPackage_detail.html',
                                        {'wp': workPackage, 'assignedWus': assignedWus, 'freeWus': freeWus})
        responseData['html'] = wpDetailHtml
        return JsonResponse(responseData)


@qcr_user_authenticated
def devDeleteWorkUnit(request, workunit_id):
    if request.is_ajax():
        if request.method == "POST":
            workUnit = get_object_or_404(WorkUnit, pk=workunit_id)
            workPackage = workUnit.workPackage
            wpId = workPackage.workPackageId
            review = workUnit.review
            workUnit.delete()
            wus = list(WorkUnit.objects.filter(review=review))
            wustring = []
            if wus == []:
                review.delete()
            responseData = {}
            responseData['result'] = 'success'
            responseData['workPackageId'] = str(wpId)
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

def recurseWorkUnitIds(randomWuId, existingWus):
	for wu in existingWus:
		if wu.workUnitId == randomWuId:
			randomWuId = random.randint(100000, 9999999)
			recurseWorkUnitIds(randomWuId, existingWus)
	return randomWuId