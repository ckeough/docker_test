var DEM = DEM || (function(){
	//object property urls
	var _review;
	var _demSubtabs;
	//object property variables
	var _reviewId;
		
	return{
		//Initialization function depends on instantiated FUNCTIONS object
		init: function(urls, variables){
			if (FUNCTIONS && AGGREGATE_WU_DELIV && GENERIC){
				//passed-in Urls
				_review = urls['review'];
				_demSubtabs = urls['demSubtabs'];
				//passed-in variables
				_reviewId = variables['reviewId'];
			}
			else{
				alert('FATAL ERROR: \nQC REPORT FUNCTIONS OBJECT NOT INITIALIZED');
				url = _review.replace('123', _reviewId);
				location.href = url;
				//LOG ME!!
			}
		},

		//Builds the html for the DEM Info and Breaklines subtabs (just the tabs, not the content), 
		//sets the click handlers for each.
		buildDemTab: function(){
			$.ajax({
				url: _demSubtabs,
				type: "GET",
				success: function(data) {
					$('#dem').html(data['html']);
					DEM.setDemSubtabHandlers();				
					$('#demTabHeaders li a[href="#demInfo"]').click();
					$("#demSubtabs").show();
				}
			});
		},

		//Click handler for the breaklines and dem info subtabs.  Calls methods to build the subtabs for
		//each which select the appropriate subtab and build/display its html.
		setDemSubtabHandlers: function(){
			$('#demTabHeaders').on("click", "li", function (event) {	
				event.preventDefault();
				var subtabSelector = $(this).find('a').attr('href');
				$(subtabSelector).addClass('tab_pane active');		
				if (subtabSelector == '#demInfo'){
					AGGREGATE_WU_DELIV.buildDelivSubtabs(dem = true);
				}
				if (subtabSelector == '#breaklines'){
					GENERIC.buildDeliverableSubtabs(true, false, false, false);
				}
			});
		},
		
	};	
}());	