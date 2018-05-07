var GENERIC = GENERIC || (function(){
	
	//object property URLs
	var _review;
	var _workUnits;
	var _delivForm;
	var _deliverablesByCategory;
	var _createDelivNoWu;
	var _createDelivWu;
	var _deleteDeliv;
	var _updateDeliv;
	var _removeGenericDelivWu;
	var _checkRemainingWu;
	//object property variables
	var _reviewId;
	var _workUnitId;
	var _subtabId;

	return{
		//Initialization function depends on instantiated FUNCTIONS object
		init: function(urls, vars){
			if (FUNCTIONS){
				//Passed-in URLs
				_review = urls["review"];
				_workUnits = urls['workUnits'];
				_delivForm = urls['delivForm'];
				_deliverablesByCategory = urls['deliverablesByCategory'];
				_createDelivNoWu = urls['createDelivNoWu'];
				_createDelivWu = urls['createDelivWu'];
				_deleteDeliv = urls['deleteDeliv'];
				_updateDeliv = urls['updateDeliv'];
				_removeGenericDelivWu = urls['removeGenericDelivWu'];
				_checkRemainingWu = urls['checkRemainingWu']
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
		
		//Function to package forms for dispatch to server
        packageDelivUpdateForm: function(deliv_id){
            var kvpString = '"workUnits":"';
			$('#wuSelect'+ deliv_id +' :selected').each(function(i, selected){
				var selItem = $(selected).text().toString();
				kvpString += selItem + ','
			});
			if (kvpString.substring(kvpString.length-1) == ','){
				kvpString = kvpString.slice(0,-1);
			}
			kvpString = kvpString + '"';
			var json = JSON.stringify({
				'deliverableCategory': $('select[name=deliverableCategory'+deliv_id+']').val(),
				'description': $('#desc'+deliv_id).val(),
				'quantity':$('#quantity' + deliv_id).val(),
				'spatRef':$('#spatRef' + deliv_id).val(),
				'reqPerContract': $('select[name=reqPerContract'+deliv_id+']').val(),
				'reqPerSpec': $('select[name=reqPerSpec'+deliv_id+']').val(),
				'delivered': $('select[name=delivered'+deliv_id+']').val(),
				'comment': $('#comment'+deliv_id).val(),
				'accepted': $('select[name=accepted'+deliv_id+']').val()
			})
			var rmvBracket = json.slice(0,-1);
			var finalJson = rmvBracket + ',' + kvpString + '}'
			return finalJson;
        },

		//Functions to enable/disable update and cancel buttons on 'Update' form
		delivEditButtonsEnable: function(){
			$('.updateDelivButton').prop('disabled', false);
			$('.updateDelivButton').css('opacity', 1);
			$('.cancelDelivButton').prop('disabled', false);
			$('.cancelDelivButton').css('opacity', 1);
		},

        delivEditButtonsDisable: function(){
			$('.updateDelivButton').prop('disabled', true);
			$('.updateDelivButton').css('opacity', 0.5);
			$('.cancelDelivButton').prop('disabled', true);
			$('.cancelDelivButton').css('opacity', 0.5);
		},

		//Builds work unit subtab html and places it in the main tab content area, passes the 'buildDeliverableTabContent' function
		//into the setter for the work unit tab click handler in order to build the work unit tab content when the tab is clicked.
		buildDeliverableSubtabs: function(breaklines = false, xmlMetadata = false, reportsShapefiles = false, other = false){
			var selector;
			var delType;
			
			if (breaklines){
				$('#demInfo').html('');
				selector = '#breaklines';
				genericCategory = '2';
			}
			if (xmlMetadata){
				$('#reports').html('');
				selector = '#xmlMetadata';
				genericCategory = '1';
			}
			if (reportsShapefiles){
				$('#xmlMetadata').html('')
				selector = '#reports';
				genericCategory = '6';
			}
			if (other){
				selector = '#other';
				genericCategory = '7';
			}
			$.ajax({
				url: _workUnits.replace('123', _reviewId),
				type:'GET',
				success: function(data){
					$(selector).html(data['html']);
					var generic = true;
					FUNCTIONS.setWuTabClickHandler(GENERIC.buildDeliverableTabContent, data, generic, genericCategory);
					$('#workUnits').show();
				}
			});
		},
		
		//Wrapper function for 'buildGenericDeliverablesTab' to construct the appropriate category URL to pass in
		//to the method
		buildDeliverableTabContent: function(workUnitId, categoryId, subtabSelector){
			url = _deliverablesByCategory.replace('123', workUnitId);
			delivsByCatUrl = url.replace('456', categoryId);
			GENERIC.buildGenericDeliverablesTab(subtabSelector, delivsByCatUrl);
		},
		
		//Builds the html for the clicked work unit subtab for a given generic deliverable type.  Sets the handlers to expand and collapse
		//deliverable panels on the subtab.  Due to dynamic panel creation, passes a callback function to the 'add Error' button click
		//handler in order to show the add error form and set the forms button click handlers.  Sets all handlers for the fields and buttons
		//in a deliverable panel.
		buildGenericDeliverablesTab: function(selector, delivUrl){
			$.ajax({
				url: delivUrl,
				type: "GET",
				success: function(data) {
					$(selector).html(data);
					$(document).off('click', '.panel-heading span.clickable').on('click', '.panel-heading span.clickable', function(e){
						e.preventDefault();
						var $this = $(this);
						if(!$this.hasClass('panel-collapsed')) {
							$this.parents('.panel').find('.panel-body').slideUp();
							$this.addClass('panel-collapsed');
							$this.find('i').removeClass('glyphicon-chevron-up').addClass('glyphicon-chevron-down');
						}
						else {
							$this.parents('.panel').find('.panel-body').slideDown();
							$this.removeClass('panel-collapsed');
							$this.find('i').removeClass('glyphicon-chevron-down').addClass('glyphicon-chevron-up');
						}
					});
					selectorString = selector + ' .row'
					//Set the 'add error' button handlers in a loop for each deliverable.  The deliverable ID has to be 
					//parsed out of the selector string based on different string lengths for different deliverable types.
					$(selectorString).each(function(){
						var id = '';
						var tempSelect = $(this).attr('id');
						if (tempSelect.includes('Add')){
						    return true;
						};						
						if (tempSelect.includes('Metadata')){
							id = $(this).attr('id').substr(19);
						}
						//Do both of these qualifiers need to be here?
						if (selector.includes('workUnit') && tempSelect.includes('Breakline')){
							id = $(this).attr('id').substr(20);
						}
						if (tempSelect.includes('Classified')){
							id = $(this).attr('id').substr(21);
						}
						if (tempSelect.includes('Swath')){
							id = $(this).attr('id').substr(16);
						}
						if (tempSelect.includes('Report')){
							id = $(this).attr('id').substr(17);
						}
						if (tempSelect.includes('Other')){
							id = $(this).attr('id').substr(16);
						}
						addErrorButtonSelector = '#addError' + id;
                        FUNCTIONS.setErrorTableHandlers(id);
                        FUNCTIONS.setEditErrorButtonHandlers(id);
						$(document).off('click', addErrorButtonSelector).on('click', addErrorButtonSelector, FUNCTIONS.createAddErrorCallback(id, addErrorButtonSelector, selector));
					});

					GENERIC.setEditDeliverableButtonHandlers();

					if (typeof _subtabId !== 'undefined' && _subtabId !== ''){
						selector = '#collPanel' + _subtabId;
						FUNCTIONS.expandDeliverablePane(selector);
					}
					_subtabId = '';
					$(selector).show();
				},
			})
		},		
		
		//Handles button click events for add/cancel add new deliverables, deletion of deliverables and associated errors, form and select element
		//changes in deliverable panels, and update/remove/cancel update buttons for a deliverable panel.
		//TODO: Split out 'add' functions from 'edit/update' functions.
		setEditDeliverableButtonHandlers: function(){
		    //Add Listener for Create and CancelCreate Buttons
            $(document).off('click', '#newDeliv').on('click', '#newDeliv', function (e){
                json = FUNCTIONS.packageDelivForm();
                e.preventDefault();
                $.ajax({
                    url: _createDelivWu.replace('123', workUnitId),
                    type: "POST",
                    data: json,
                    success: function(data) {
                        alert('CREATED DELIVERABLE: ' + data['createdDeliv'] + '\nDELIVERABLE LINKED TO WORK UNITS: ' + data['updatedWu']);
                        $('#wuLink' + workUnitId).trigger('click');
                    }
                })
            });
            $(document).off('click', '#cancelNewDeliv').on('click', '#cancelNewDeliv', function (e){
                $('#wuLink' + workUnitId).trigger('click');
            });
            //Add Listener for Delete Button
            $(document).off('click', '.deleteDelivButton').on('click', '.deleteDelivButton', function(e){
                e.preventDefault();
                //Pull Deliv ID Out of Button ID
                deliv_id = $(this).attr('id').substr(11);
                var cont = confirm("Confirm Deletion.");
                if (cont){
                    $.ajax({
                        url: _deleteDeliv.replace('123', deliv_id),
                        type: "POST",
                        success: function(data){
                            if (data['success']=='True'){
                                $('#wuTabController li a[aria-expanded=true]').click();
                            }
                        }
                    });
                }
                else{
                    return false;
                }
            })
            //Add Listener for Edit Buttons
            GENERIC.delivEditButtonsDisable();
            $(document).off('keyup', '.genericDeliv input[type="text"]').on('keyup', '.genericDeliv input[type="text"]', function() {
                if($(this).val() != '') {
                    GENERIC.delivEditButtonsEnable();
                }
            });
            $(document).off('change','.genericDeliv').on('change', '.genericDeliv' , function() {
                GENERIC.delivEditButtonsEnable();
            });
            $(document).off('change', "#genericWUSelect").on('change', "#genericWUSelect", function(e){
                GENERIC.delivEditButtonsEnable();
            });
            $(document).off('click', '.updateDelivButton').on('click', '.updateDelivButton', function(e){
                e.preventDefault();
                //Pull Deliv ID Out of Button ID
                deliv_id = $(this).attr('id').substr(11);
                var json;
                json = GENERIC.packageDelivUpdateForm(deliv_id);
                $.ajax({
                    url: _updateDeliv.replace('123', deliv_id),
                    type: "POST",
                    data: json,
                    success: function(data){
                        if ('applied' in data){
                            wus = data['applied'];
                            while(wus.charAt(0) === ','){
                                wus = wus.substr(1);
                            }
                            alert(name + ' UPDATE APPLIED TO WORK UNITS: ' + wus);
                        }
                        if (data['success']=='False'){
                            alert('failure');
                        }
                        _subtabId = deliv_id;
                        $('#wuTabController li a[aria-expanded=true]').click();
                    }
                });
            })
            $(document).off('click', '.cancelDelivButton').on('click', '.cancelDelivButton', function(e){
                _subtabId = $(this).attr('id').substr(11);
                $('#wuTabController li a[aria-expanded=true]').click();
            })
            $(document).off('click', '.removeDelivButton').on('click', '.removeDelivButton', function(e){
                e.preventDefault();
                workUnitId = $(this).attr('id').substr(15);
                delivId = $( this ).parent().get(0).id.substr(6);
                removeWuUrl = _removeGenericDelivWu.replace('123', delivId);
                removeWuUrl = removeWuUrl.replace('456', workUnitId);
                checkUrl = _checkRemainingWu.replace('123', delivId);
                $.ajax({
                    url: checkUrl,
                    type: "GET",
                    success: function(data) {
                        if (data['warn']=='True'){
                            var cont = confirm("This is the last work unit associated with this Deliverable.  Removing the association will delete the Deliverable.  Continue?");
                            if (cont == true){
                                $.ajax({
                                    url: removeWuUrl,
                                    type: "POST",
                                    success: function(data){
                                        if (data['success']=='True'){
                                            _subtabId = delivId;
                                            $('#wuTabController li a[aria-expanded=true]').click();
                                        }
                                    }
                                });
                            }
                            else{
                                return false;
                            }
                        }
                        else{
                            $.ajax({
                                url: removeWuUrl,
                                type: "POST",
                                success: function(data){
                                    if (data['success']=='True'){
                                        _subtabId = delivId;
                                        $('#wuTabController li a[aria-expanded=true]').click();
                                    }
                                }
                            });
                        }
                    }
                });
            })
        },
	};	
}());		