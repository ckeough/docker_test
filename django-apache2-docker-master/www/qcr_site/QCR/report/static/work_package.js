var WORK_PACKAGE = WORK_PACKAGE || (function(){
	
	//object property URLs
	var _review;
	var _workPackage;
	//object property variables
	var _reviewId;
	
	return{
		//Initialization function depends on instantiated FUNCTIONS object
		init: function(urls, vars){
			if (FUNCTIONS){
				//Passed-in URLs
				_review = urls["review"];
				_workPackage = urls["workPackage"];	
				//Passed-in variables
				_reviewId = vars['reviewId'];
			}
			else{
				alert('FATAL ERROR: \nQC REPORT FUNCTIONS OBJECT NOT INITIALIZED');
				url = _review.replace('123', _reviewId);
				location.href = url;
				//LOG ME!!
			}
		},
		
		//Function to package form for dispatch to server
		packageWpForm: function(){
			inRestDate = $('#restrictionsDateText').val();
			if (inRestDate){
			restDateArray = inRestDate.split('/');
			restMonth = restDateArray[0];
			restDay = restDateArray[1];
			restYear = restDateArray[2];
			newRestDate = restYear + '-' + restMonth + '-' + restDay;
            }
            else newRestDate = null;
			inRecdDate = $('#receivedDateText').val();
			if (inRecdDate){
			recdDateArray = inRecdDate.split('/');
			recdMonth = recdDateArray[0];
			recdDay = recdDateArray[1];
			recdYear = recdDateArray[2];
			newRecdDate = recdYear + '-' + recdMonth + '-' + recdDay;
			}
			else newRecdDate = null;
			inAssDate = $('#assignedDateText').val();
			if (inAssDate){
			assDateArray = inAssDate.split('/');
			assMonth = assDateArray[0];
			assDay = assDateArray[1];
			assYear = assDateArray[2];
			newAssDate = assYear + '-' + assMonth + '-' + assDay;
			}
			else newAssDate = null;
			var json = JSON.stringify({
				'workPackageId': $('#workPackageId').val(),
				'name': $('#name').val(),
				'description': $('#description').val(),
				'type': $('#type').val(),
				'vendor': $('#vendor').val(),
				'poc': $('#poc').val(),
				'pocEmail': $('#pocEmail').val(),
				'projectSpec': $('select[name=projectSpec]').val(),
				'restrictions': $('select[name=selectRest]').val(),			
				'restrictionsDate': newRestDate,
				'restrictionsLayer': $('select[name=selectRestLayer]').val(),
				'thirdPartyQa': $('select[name=selectThirdPartyQa]').val(),
				'thirdPartyQaBy': $('#thirdPartyQaBy').val(),
				'receivedDate':newRecdDate,
				'assignedDate':newAssDate,
				'wusToAdd':$('#wusToAdd').val()
			});
			return json;
		},
		
		//Calls a Django view to build the work package detail html and sets the form
		//field and update/cancel update button handlers for the work package.
		buildWorkPackageTab: function(){
			$.ajax({
				url: _workPackage.replace('123', _reviewId),
				type: "GET",
				success: function(data) {
					$('#wpInfo').html(data);
					WORK_PACKAGE.setUpdateWorkPackageHandlers();				
				},
			});		
		},		
		
		//Button click handlers for update/cancel update buttons 
		setUpdateWorkPackageHandlers: function(){
			var workPackageUrl = _workPackage.replace('123', _reviewId);
			$(document).off('click', '#updateWp').on('click', '#updateWp', function(e){
				e.preventDefault();
				json = WORK_PACKAGE.packageWpForm();
				$.ajax({
					url: workPackageUrl,
					type: "POST",
					data: json,
					success: function(data) {
						alert('Updates saved!');
						$('#wpInfo').html(data);
					}
				});
			});
			$(document).off('click', '#cancelWp').on('click', '#cancelWp', function(e){
				e.preventDefault();
				$.ajax({
					url: workPackageUrl,
					type: "GET",
					success: function(data) {
						$('#wpInfo').html(data);
					}
				});
			});
		},
	};	
}());		