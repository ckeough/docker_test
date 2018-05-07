var POINTCLOUD = POINTCLOUD || (function(){
	
	//property variables go here
	var _reviewId;
	//object property urls
	var _review;
	var _pointcloudTab;
	
	return{
		//Initialization function depends on instantiated FUNCTIONS object and instantiated GENERIC object
		init: function(urls, variables){
			if (FUNCTIONS && AGGREGATE_WU_DELIV){
				//passed-in variables
				_reviewId = variables['reviewId'];
				//passed-in Urls
				_review = urls['review'];
				_pointcloudTab = urls['pointcloudTab'];
			}
			else{
				alert('FATAL ERROR: \nQC REPORT FUNCTIONS OBJECT NOT INITIALIZED');
				url = _review.replace('123', _reviewId);
				location.href = url;
				//LOG ME!!
			}			
		},
		
		//Builds the swath and classified subtabs and sets the tab click handlers for
		//each.
		buildPointcloudTab: function(){
            var minVal;
            $.ajax({
                url: _pointcloudTab.replace('123', _reviewId),
                type: "GET",
                success: function(data) {
                    $('#pointcloud').html(data['html']);
                    POINTCLOUD.setPointcloudSubtabHandlers();
                    $('#subTabObjects li a[href="#swath"]').click();
                    $('#subTabs').show();
                }
            });
        },
		
		//Uses the AGGREGATE_WU_DELIV object's buildDelivSubtabs method to populate the clicked
		//subtab's content.
        setPointcloudSubtabHandlers: function(){
            $('#subTabObjects').on("click", "li", function (event) {
				event.preventDefault();
				var subSelector =  $(this).find('a').attr('href');
				var minVal;
				if (subSelector == "#swath"){
					AGGREGATE_WU_DELIV.buildDelivSubtabs(false, true, false);
				}
				if (subSelector == "#classified"){
					AGGREGATE_WU_DELIV.buildDelivSubtabs(false, false, true);
				}
			});
        },
		
		
	};	
}());			
		