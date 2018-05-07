var METADATA = METADATA || (function(){
	
	//object property URLs
	var _review;
	var _metadataTab;
	
	//object property variables
	var _reviewId;
	
	return{
		//Initialization function depends on instantiated FUNCTIONS object and instantiated GENERIC object
		init: function(urls, vars){
			if (FUNCTIONS && GENERIC){
				//Passed-in URLs
				_review = urls["review"];
				_metadataTab = urls["metadataTab"]
			}
			else{
				alert('FATAL ERROR: \nQC REPORT FUNCTIONS OBJECT NOT INITIALIZED');
				url = _review.replace('123', _reviewId);
				location.href = url;
				//LOG ME!!
			}
		},
		
		//Builds the xmlMetadata and Reports subtabs and sets the tab click handlers for
		//each.
		buildMetadataTab: function(){
			$.ajax({
				url: _metadataTab,
				type: "GET",
				success: function(data) {
					$('#metadata').html(data['html']);
					METADATA.setMetadataSubtabHandlers();	
					$('#subTabObjects li a[href="#xmlMetadata"]').click();
					$("#subTabs").show();
				}
			});
		},

		//Uses the GENERIC object's buildDeliverableSubtabs method to populate the clicked
		//subtab's content.
		setMetadataSubtabHandlers: function(){
			$('#subTabObjects').on("click", "li", function (event) {	
				event.preventDefault();
				var subtabSelector = $(this).find('a').attr('href');
				$(subtabSelector).addClass('tab_pane active');		
				if (subtabSelector == '#xmlMetadata'){
					GENERIC.buildDeliverableSubtabs(false, true, false, false);
				}
				if (subtabSelector == '#reports'){
					GENERIC.buildDeliverableSubtabs(false, false, true, false);
				}
			});
		},
		
	};	
}());