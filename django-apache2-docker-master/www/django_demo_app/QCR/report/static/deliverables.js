var DELIVERABLES = DELIVERABLES || (function(){
	//object property urls
	var _review;
	var _deliverables;
	var _delivForm;
	var _createDeliv;
	//object property variables
	var _reviewId;

	return{
		//Initialization function depends on instantiated FUNCTIONS object
		init: function(urls, variables){
			if (FUNCTIONS){
				//passed-in Urls
				_review = urls['review'];
				_deliverables = urls['deliverables'];
				_delivForm = urls['delivForm'];
				_createDeliv = urls['createDeliv'];
				_updateDeliv = urls['updateDeliv'];
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
		
		//Builds the work unit subtab controls, determines which work unit subtab to display
		//and uses the getWorkUnitDeliverables function to build the subtab content.
		buildDeliverablesTab: function(){
			FUNCTIONS.buildWorkUnitSubtabs('#deliverables', DELIVERABLES.getWorkUnitDeliverables, _reviewId);
		},
		
		//Calls a view which builds the subtab conntent html for a work unit subtab and sets the 
		//'add deliverable' button click handlers (deliverables may not be updated from this tab).
		getWorkUnitDeliverables: function(workUnitId){
			$.ajax({
				url: _deliverables.replace('123', workUnitId),
				type: "GET",
				success: function(data) {
					div = '#workUnitUpdate' + workUnitId;
					wuHtml = data;												
					$(div).html(wuHtml);	
					$('.updateDeliverable').prop('disabled', true);
					$('.updateDeliverable').css('opacity', 0.5);
					DELIVERABLES.setAddDeliverableButtonHandlers(workUnitId);
				}
			});
		},
		
		//Sets button handlers to show the 'add deliverable' form, create a deliverable, or cancel
		//adding a deliverable
		setAddDeliverableButtonHandlers: function(workUnitId){
			$(document).off('change', '.delivRow input').on('change', '.delivRow input', function (e){
				e.preventDefault();
				var fullId = this.id.split('_')[1]
				var typeId = fullId.substring(0,3)
				if (typeId == 'Gen'){
					btnId  = '#submitGenDelivChg_' + fullId;
				}
				else{
					btnId = '#submitAwDelivChg_' + fullId;
				}
				$(btnId).prop('disabled', false);
				$(btnId).css('opacity', 1)
				
			})
			
			$(document).off('change', '.delivRow select').on('change', '.delivRow select', function (e){
				e.preventDefault();
				var fullId = this.id.split('_')[1]
				var typeId = fullId.substring(0,3)
				if (typeId == 'Gen'){
					btnId  = '#submitGenDelivChg_' + fullId;
				}
				else{
					btnId = '#submitAwDelivChg_' + fullId;
				}
				$(btnId).prop('disabled', false);
				$(btnId).css('opacity', 1)
				
			})
			
			$(document).off('click', '.updateDeliverable').on('click', '.updateDeliverable', function (e){
				e.preventDefault();
				var btnId = '#' + this.id;
				var fullId = this.id.split('_')[1];
				var typeString = fullId.substring(0,3)
				var idString = fullId.substring(3)
				var row = '#rowDeliv_' + fullId;
				var url = _updateDeliv;
				
				json = JSON.stringify({
				'type':typeString,
				'id':idString,
				'description':$('#desc_' + fullId).val(),
				'category':$('#catSelect_' + fullId).val(),
				'quantity':$('#qty_' + fullId).val(),
				'spatRef':$('#spatRef_' + fullId).val(),
				'reqPerContract':$('#reqPerContractSelect_' + fullId).val(),
				'reqPerSpec':$('#reqPerSpecSelect_' + fullId).val(),
				'delivered':$('#delivSelect_' + fullId).val(),
				'accepted':$('#acceptedSelect_' + fullId).val()
				});
				$.ajax({
					url: url,
					type: 'POST',
					data: json,
					success: function(data){
						$(row).replaceWith(data['html']);

						$(btnId).prop('disabled', true);
						$(btnId).css('opacity', 0.5);
					}	
				})
				

			})
			
			$(document).off('click', '#showDelivForm').on('click', '#showDelivForm', function (e){
				e.preventDefault();
				$.ajax({
					//GET TYPES
					url:  _delivForm.replace('123', workUnitId),
					type: "GET",
					success: function(data) {
						startRowHtml = '<tr id = "delivFormRow">';	
						catSelectHtml = '<td><select id = "addDeliverableCategory" name = "addDeliverableCategory" style = "width:100%">';
						$(data['categories']).each(function(){
							catSelectHtml += '<option>'+this+'</option>';
						})
						catSelectHtml += '</select></td>';
						endRowHtml = '<td><input type="text" id="addDescription" style="width:100%"></td>'
						endRowHtml += '<td><input type="number" id="addQuantity" style="width:100%"></td>'
						endRowHtml += '<td><input type="text" id="addSpatRef" style="width:100%"></td>'
						endRowHtml += '<td><select id="addReqPerContract" name="addReqPerContract"><option value= "true">Yes</option><option value = "false">No</option></select></td>'
						endRowHtml += '<td><select id="addReqPerSpec" name="addReqPerSpec"><option value= "true">Yes</option><option value = "false">No</option></select></td>'
						endRowHtml += '<td><select id="addDelivered" name="addDelivered"><option value= "true">Yes</option><option value = "false">No</option></select></td>'
						endRowHtml += '<td><select id="addAccepted" name="addAccepted"><option value= "true">Yes</option><option value = "false" selected>No</option></select></td></tr>'
						newRowHtml = startRowHtml + catSelectHtml + endRowHtml;
						$('#delivsList tr:last').after(newRowHtml);
						$('#showDelivForm').hide();
						$('#delivFormBtns').show();
					}
				});										
			});	
			
			$(document).off('click', '#cancelShowDelivForm').on('click', '#cancelShowDelivForm', function (e){
				e.preventDefault();
				$('#delivFormBtns').hide();
				$('#showDelivForm').show();
				$('#delivFormRow').remove();
			});
			
			$(document).off('click', '#submitDelivForm').on('click', '#submitDelivForm', function (e){
				e.preventDefault();
				json = FUNCTIONS.packageDelivForm();
				$.ajax({
					url: _createDeliv.replace('123', workUnitId),
					type: "POST",
					data: json,
					success: function(data) {
						alert('CREATED DELIVERABLE: ' + data['createdDeliv'] + '\nDELIVERABLE LINKED TO WORK UNITS: ' + data['updatedWu']);
						$.ajax({
							url: _deliverables.replace('123', workUnitId),
							type: "GET",
							success: function(data) {
								div = '#workUnitUpdate' + workUnitId;
								wuHtml = data;												
								$(div).html(wuHtml);
								$('.updateDeliverable').prop('disabled', true);
								$('.updateDeliverable').css('opacity', 0.5);
								DELIVERABLES.setAddDeliverableButtonHandlers(workUnitId);
								
							}
						});		
					}
				})											
			});			
		}
	};	
}());	


