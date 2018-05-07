from django.conf.urls import url

from . import views

urlpatterns = [

	
	
	url(r'^$', views.home, name='home'),

	url(r'^add_checklist_item/$', views.addChecklistItem, name = 'addChecklistItem'),
	url(r'^delete_checklist_item/$', views.deleteChecklistItem, name = 'deleteChecklistItem'),

	url(r'^updateChecklist/$', views.updateChecklist, name ='updateChecklist'),
	url(r'^getChecklistModal/(?P<review_id>[0-9]+)/$', views.getChecklistModal, name ='getChecklistModal'),

	##Admin urls
	url(r'^adminListReviews/$', views.adminListReviews, name='adminListReviews'),
	url(r'^adminHomePage/$', views.adminHomePage, name = 'adminHomePage'),
	url(r'^adminHomePage/(?P<tabId>[0-9]+)/$', views.adminHomePage, name = 'adminHomePage'),
	url(r'^adminHomePage/(?P<tabId>[0-9]+)/(?P<userFilter>.+)/$', views.adminHomePage, name = 'adminHomePage'),
	url(r'^adminHomePage/$', views.adminHomePage, name = 'adminHomePage'),
	url(r'^populateReviewWuSelect/$', views.adminPopulateReviewWuSelect, name = 'populateReviewWuSelect'),
	url(r'^adminReviewDetail/(?P<review_id>[0-9]+)/$', views.adminReviewDetail, name = 'adminReview'),
	url(r'^adminReviewDetail/(?P<review_id>[0-9]+)/(?P<userFilter>.+)/$', views.adminReviewDetail, name = 'adminReview'),
	url(r'^adminReviewDetail/$', views.adminReviewDetail, name = 'adminReviewEdit'),
	url(r'^adminWpDetail/(?P<wpid>[0-9]+)/$', views.adminWpDetail, name = 'adminWpDetail'),
	url(r'^getWorkPackages/$', views.adminGetWorkPackages, name = 'getWorkPackages'),
	url(r'^createReview/$', views.adminCreateReview, name = 'createReview'),
	url(r'^remove_workunit/$', views.adminRemoveWorkUnit, name = 'removeWorkUnit'),
	url(r'^delete_review/(?P<review_id>[0-9]+)/$', views.adminDeleteReview, name ='deleteReview'),
	url(r'^search_wps/$', views.searchWps, name = 'searchWps'),
	url(r'^add_wp/$', views.addWpFromPts, name = 'addWp'),
	url(r'^add_user/$', views.addUser, name = 'addUser'),
	url(r'^remove_user/$', views.removeUser, name = 'removeUser'),
	url(r'^addQualityLevel/$', views.addQualityLevel, name ='addQualityLevel'),	
	url(r'^deleteQualityLevel/$', views.deleteQualityLevel, name ='deleteQualityLevel'),
	url(r'^addSensorUsed/$', views.addSensorUsed, name ='addSensorUsed'),	
	url(r'^deleteSensorUsed/$', views.deleteSensorUsed, name ='deleteSensorUsed'),
	url(r'^addSensorType/$', views.addSensorType, name ='addSensorType'),	
	url(r'^deleteSensorType/$', views.deleteSensorType, name ='deleteSensorType'),
	
	## Developer tools urls
	url(r'^addProjectSpec/$', views.addProjectSpec, name ='addProjectSpec'),
	url(r'^deleteProjectSpec/$', views.deleteProjectSpec, name ='deleteProjectSpec'),
	url(r'^createWorkPackage/$', views.devCreateWorkPackage, name = 'createWorkPackage'),
	url(r'^deleteWorkPackage/$', views.devDeleteWorkPackage, name = 'deleteWorkPackage'),
	url(r'^create_workUnit/(?P<workPackage_id>[0-9]+)/$', views.devCreateWorkUnit, name ='createWorkUnit'),
	url(r'^delete_workunit/(?P<workunit_id>[0-9]+)/$', views.devDeleteWorkUnit, name ='deleteWorkUnit'),

	
	
	
]