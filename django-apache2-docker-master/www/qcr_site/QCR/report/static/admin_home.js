var ADMIN_HOME = ADMIN_HOME || (function(){
	//Object property URLs
	var _adminListReviews;
	var _adminReviewDetail;
	//Object property vars
	
	return{
		//Initialization function depends on instantiated FUNCTIONS object
		init: function(urls){
			//Passed-in URLS
			_adminListReviews = urls['adminListReviews'];
			_adminReviewDetail = urls['adminReview'];
			//Passed-in Variables
		},
		
		userReviewLinkCallback: function(id, user){
			return function(){
				var url = _adminReviewDetail.replace('123', id) + user;
				location.href = url;
			}
		},
		
		buildReviewsTab: function(userFilter){
			if (userFilter=='allUsers'){
				$.ajax({
					url: _adminListReviews,
					type: "GET",
					success: function(data) {
						$('#reviewDetail').html(data['html']);
					}
				});	
			}
			else{
				var selectedQcrUser = userFilter;
				var url = _adminListReviews;
				var jsonDict = {};
				jsonDict['user'] = selectedQcrUser;
				var json = JSON.stringify(jsonDict);
				$.ajax({
					url: url,
					type: 'POST',
					data: json,
					success: function(data){
						$('#reviewDetail').html(data['html']);
						$('#userReviewList li a').each(function(){
							var linkSelector = '#' + $(this).attr('id');
							var id = linkSelector.substring(7);
							$(document).off('click', linkSelector).on('click', linkSelector, ADMIN_HOME.userReviewLinkCallback(id, selectedQcrUser));
						});
					}
				});
			}
		},
	};
}());