var AGGREGATE_WU_DELIV =  AGGREGATE_WU_DELIV || (function(){
	//object property URLs
	var _review;
	var _deleteError;
	//Aggregated WU URLs
	var _checkRemainingWorkUnits;
	var _removeDelivFromWu;
	var _createAggregatedWuDeliverable;
	var _aggregatedWuDeliverableTab;
	var _aggregatedWuDeliverableTabs;
	var _deleteAggregatedWuDeliverable;
	var _getDelivProjectSpec;
	var _demForm;
	var _swathForm;
	var _classifiedForm;

	//object property variables
	var _reviewId;
	var _tabId;
	var _rowsAdded;
	
	return{
		//Initialization function depends on instantiated FUNCTIONS object
		init: function(urls, vars){
			if (FUNCTIONS){
				//Passed-in URLs
				_review = urls["review"];
				_deleteError = urls["deleteError"];
				_checkRemainingWorkUnits = urls['checkRemainingWorkUnits'];
				_removeDelivFromWu = urls['removeDelivFromWu'];
				_createAggregatedWuDeliverable = urls['createAggregatedWuDeliv'];
				_aggregatedWuDeliverableTab = urls['aggregatedWuDeliverableTab'];
				_aggregatedWuDeliverableTabs = urls['aggregatedWuDeliverableTabs'];
				_deleteAggregatedWuDeliverable = urls['deleteAggregatedWuDeliverable'];
				_getDelivProjectSpec = urls['getDelivProjectSpec'];
				_demForm = urls['demForm'];
				_swathForm = urls['swathForm'];
				_classifiedForm = urls['classifiedForm'];
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
		
		//Functions to package forms for dispatch to server
		packageDemForm: function(){
			var kvpString = '"workUnits":"';
			if($('#wuDemSelect').length){
				var initialWu = $('#wuDemSelect :selected').val().toString();
				
				if(initialWu != ''){
					var selId = initialWu.substring(initialWu.lastIndexOf(" ") + 1, initialWu.length);
					kvpString += selId.toString() + ',';
				}
			}
			else{
				$('#wuCiMultiSelect :selected').each(function(i, selected){
					var selItem = $(selected).val().toString();	
					var selId = selItem.substring(selItem.lastIndexOf(" ") + 1, selItem.length);
					kvpString += selId + ','
				});
			}
			if (kvpString.substring(kvpString.length-1) == ','){
				kvpString = kvpString.slice(0,-1);
			}
			kvpString = kvpString + '"';
			var json = JSON.stringify({
				'description':$('#demDesc').val(),
				'quantity':$('#quantity').val(),
				'spatRef':$('#spatRef').val(),
				'reqPerContract': $('select[name=reqPerContract]').val(),
				'reqPerSpec': $('select[name=reqPerSpec]').val(),
				//'resolution': $('#resolution').val(),
				//'resUnits': $('#resUnits').val(),
				'pixelType': $('#pixelType').val(),
				'interpolation': $('#interpolation').val(),
				'delivered': $('select[name=delivered]').val(),
				'accepted': $('select[name=accepted]').val(),
			})
			var rmvBracket = json.slice(0,-1);
			var finalJson = rmvBracket + ',' + kvpString + '}'
			return finalJson;
		},

		packageSwathForm: function(){
			var kvpString = '"workUnits":"';
			if($('#wuSwathSelect').length){
				var initialWu = $('#wuSwathSelect :selected').val().toString();
				if(initialWu != ''){
					var selId = initialWu.substring(initialWu.lastIndexOf(" ") + 1, initialWu.length);
					kvpString += selId.toString() + ',';
				}
			}
			else{
				$('#wuCiMultiSelect :selected').each(function(i, selected){
					var selItem = $(selected).val().toString();	
					var selId = selItem.substring(selItem.lastIndexOf(" ") + 1, selItem.length);
					kvpString += selId + ','
				});
			}
			if (kvpString.substring(kvpString.length-1) == ','){
				kvpString = kvpString.slice(0,-1);
			}
			kvpString = kvpString + '"';
			var json = JSON.stringify({
				'description':$('#swathDesc').val(),
				'quantity':$('#quantity').val(),
				'spatRef':$('#spatRef').val(),
				'reqPerContract': $('select[name=reqPerContract]').val(),
				'reqPerSpec': $('select[name=reqPerSpec]').val(),
				'swathPCVS': $('#swathPCVS').val(),
				'prdf': $('#prdf').val(),
				'requiredInterswath': $('#requiredInterswath').val(),
				'recordedInterswath': $('#recordedInterswath').val(),
				'testedInterswath': $('#testedInterswath').val(),
				'delivered': $('select[name=delivered]').val(),
				'accepted': $('select[name=accepted]').val(),
			})
			var rmvBracket = json.slice(0,-1);
			var finalJson = rmvBracket + ',' + kvpString + '}'
			return finalJson;
		},

		packageClassifiedForm: function(){
			var kvpString = '"workUnits":"';
			if($('#wuClassifiedSelect').length){
				var initialWu = $('#wuClassifiedSelect :selected').val().toString();
				if(initialWu != ''){
					var selId = initialWu.substring(initialWu.lastIndexOf(" ") + 1, initialWu.length);
					kvpString += selId.toString() + ',';
				}
			}
			else{
				$('#wuCiMultiSelect :selected').each(function(i, selected){
					var selItem = $(selected).val().toString();	
					var selId = selItem.substring(selItem.lastIndexOf(" ") + 1, selItem.length);
					kvpString += selId + ','
				});
			}
			if (kvpString.substring(kvpString.length-1) == ','){
				kvpString = kvpString.slice(0,-1);
			}
			kvpString = kvpString + '"';
			var json = JSON.stringify({
				'description':$('#classDesc').val(),
				'quantity':$('#quantity').val(),
				'spatRef':$('#spatRef').val(),
				'reqPerContract': $('select[name=reqPerContract]').val(),
				'reqPerSpec': $('select[name=reqPerSpec]').val(),
				'classPCVS': $('#classPCVS').val(),
				'prdf': $('#prdf').val(),
				'delivered': $('select[name=delivered]').val(),
				'accepted': $('select[name=accepted]').val(),
			})
			var rmvBracket = json.slice(0,-1);
			var finalJson = rmvBracket + ',' + kvpString + '}'
			return finalJson;
		},
		
		//Functions to enable and disable deliverable update/cancel update buttons based on form input states
		editButtonsEnable: function(){
			$('#updateAggregatedWuDeliv').prop('disabled', false);
			$('#updateAggregatedWuDeliv').css('opacity', 1); 
			$('#cancelUpdateAggregatedWuDeliv').prop('disabled', false);
			$('#cancelUpdateAggregatedWuDeliv').css('opacity', 1); 
		},
		
		editButtonsDisable: function(){
			$('#updateAggregatedWuDeliv').prop('disabled', true);
			$('#updateAggregatedWuDeliv').css('opacity', 0.5); 
			$('#cancelUpdateAggregatedWuDeliv').prop('disabled', true);
			$('#cancelUpdateAggregatedWuDeliv').css('opacity', 0.5); 
		},
		
		//Sets handlers for changes to various types of form inputs, which in turn enable and disable the update/cancel update buttons
		setUpdateFormInputHandlers: function(){
			AGGREGATE_WU_DELIV.editButtonsDisable();									
			$(document).off('keyup', '#aggregatedWuDeliv input[type="text"]').on('keyup', '#aggregatedWuDeliv input[type="text"]', function() {
				if($(this).val() != '') {
					AGGREGATE_WU_DELIV.editButtonsEnable();
				}
			});		
			$(document).off('change','#aggregatedWuDeliv .number').on('change', '#aggregatedWuDeliv .number' , function() {		
				AGGREGATE_WU_DELIV.editButtonsEnable();
			});		
			$(document).off('change', "#wuCiMultiSelect").on('change', "#wuCiMultiSelect", function(e){		
				AGGREGATE_WU_DELIV.editButtonsEnable();
			});
		},
		
		//Calback function to remove a deliverable from a work unit.  Will warn user if the deliverable is being removed from the
		//last associated work unit (that the deliverable itself must be deleted with no remaining associations).
		createRemoveDelivCallback: function(workUnitId, removeWuSelector, demTabId = null, swathTabId = null, classifiedTabId = null){
			return function(){
				var tabId;
				var url;
				var removeUrl;
				var name;
				if (demTabId != null){
					tabId = demTabId;
					url = _checkRemainingWorkUnits.replace('123', demTabId);
					preUrl = _removeDelivFromWu.replace('123', workUnitId);
					removeUrl = preUrl.replace('456','1');
					name = 'DEM';
				}
				if (swathTabId != null){
					tabId = swathTabId;
					url = _checkRemainingWorkUnits.replace('123', swathTabId);
					preUrl = _removeDelivFromWu.replace('123', workUnitId);
					removeUrl = preUrl.replace('456','2');
					name = 'Swath';
				}
				if (classifiedTabId != null){
					tabId = classifiedTabId;
					url = _checkRemainingWorkUnits.replace('123', classifiedTabId);
					preUrl = _removeDelivFromWu.replace('123', workUnitId);
					removeUrl = preUrl.replace('456','3');
					name = 'Classified';
				}
				$.ajax({
					url: url,
					type: "GET",
					success: function(data) {
						if (data['warn']=='True'){
							var cont = confirm("This is the last work unit associated with this " + name + ".  Removing the association will delete the " + name + ".  Continue?");
							if (cont == true){
								$.ajax({
									url: removeUrl,
									type: "POST",
									success: function(data) {
										if(demTabId){
											AGGREGATE_WU_DELIV.buildDelivSubtabs(dem = true);
										}
										if(swathTabId){
											AGGREGATE_WU_DELIV.buildDelivSubtabs(null, swath = true, null);
										}
										if(classifiedTabId){
											AGGREGATE_WU_DELIV.buildDelivSubtabs(null, null, classified = true);
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
								url: removeUrl,
								type: "POST",
								success: function(data) {
									_tabId = tabId;
									if(demTabId){
										AGGREGATE_WU_DELIV.buildDelivSubtabs(dem = true);
									}
									if(swathTabId){
										AGGREGATE_WU_DELIV.buildDelivSubtabs(null, swath = true, null);
									}
									if(classifiedTabId){
										AGGREGATE_WU_DELIV.buildDelivSubtabs(null, null, classified = true);
									}
								}
							});
						}
					}
				});
			};
		},
		
		//Sets the button handlers to remove a deliverable from an associated work unit.  Uses the callback function 'createRemoveDelivCallback'
		//since the list of associated work units (and the remove buttons) is created dynamically.
		setRemoveDelivCallbackHandlers: function(demTabId = null, swathTabId = null, classifiedTabId = null){
			$('#wuSameInfo tr').each(function(){
				var workUnitId = $(this).attr('id');
				var removeWuSelector = '#removeWu' + workUnitId;
				if(demTabId != null){
					$(document).off('click', removeWuSelector).on('click', removeWuSelector, AGGREGATE_WU_DELIV.createRemoveDelivCallback(workUnitId, removeWuSelector, demTabId));
				}
				if(swathTabId != null){
					$(document).off('click', removeWuSelector).on('click', removeWuSelector, AGGREGATE_WU_DELIV.createRemoveDelivCallback(workUnitId, removeWuSelector, null, swathTabId, null));
				}
				if(classifiedTabId != null){
					$(document).off('click', removeWuSelector).on('click', removeWuSelector, AGGREGATE_WU_DELIV.createRemoveDelivCallback(workUnitId, removeWuSelector, null, null, classifiedTabId));
				}
			})
		},
		
		//Sets button handlers to a) show the 'add' form for a deliverable type and b) add or cancel addition of a deliverable
		setAddDelivButtonHandlers: function(dem = false, swath = false, classified = false){
			var formUrl;
			var createUrl;
			var selector;
			var name;
			var preCreateUrl =  _createAggregatedWuDeliverable.replace('123', _reviewId);
			//Set deliverable type-specific variables
			if(dem == true){
				formUrl = _demForm.replace('123', _reviewId);
				createUrl = preCreateUrl.replace('456', '1');
				selector = '#demInfo';
				name = 'DEM'
			}
			else if(swath == true){
				formUrl = _swathForm.replace('123', _reviewId);
				createUrl = preCreateUrl.replace('456', '2')
				selector = '#swath';
				name = 'Swath';
			}
			else if(classified == true){
				formUrl = _classifiedForm.replace('123', _reviewId);
				createUrl = preCreateUrl.replace('456', '3')
				selector = '#classified';
				name = 'Classified';
			}
			//Button click handlers
			$(document).off('click', '#addAggregatedWuDelivButton').on('click', '#addAggregatedWuDelivButton', function (e){
				e.preventDefault();
				$.ajax({
					url: formUrl,
					type: "GET",
					success: function(data) {
						var formHtml = data;
						var submitCi = '<input id = "createAggregatedWuDeliv" type=button class="btn-default" value="Submit">';
						var cancelCi = '<input id = "cancelCreateAggregatedWuDeliv" type=button class="btn-default" value="Cancel">';
						var html = formHtml + submitCi + cancelCi + '<br><br></div></div></div></div>';
						$(selector).html(html);
					}
				});
			});
			$(document).off('click', '#createAggregatedWuDeliv').on('click', '#createAggregatedWuDeliv', function (e){
				e.preventDefault();
				var json;
				if(dem == true){json = AGGREGATE_WU_DELIV.packageDemForm();}
				if(swath == true){json = AGGREGATE_WU_DELIV.packageSwathForm();}
				if(classified == true){json = AGGREGATE_WU_DELIV.packageClassifiedForm();}	
				$.ajax({
					url: createUrl,
					type: "POST",
					data: json,
					success: function(data) {
						alert(name + ' APPLIED TO WORK UNITS: ' + data['applied']);
						_tabId = data['tabId'];
						if (dem == true){
							AGGREGATE_WU_DELIV.buildDelivSubtabs(dem = true);
						}
						if (swath == true){
							AGGREGATE_WU_DELIV.buildDelivSubtabs(false, swath = true, false);
						}
						if (classified == true){
							AGGREGATE_WU_DELIV.buildDelivSubtabs(false, false, classified = true);
						}
					}
				})
			});
			$(document).off('click', '#cancelCreateAggregatedWuDeliv').on('click', '#cancelCreateAggregatedWuDeliv', function (e){
				if (dem == true){
					AGGREGATE_WU_DELIV.buildDelivSubtabs(dem = true);
				}
				if (swath == true){
					AGGREGATE_WU_DELIV.buildDelivSubtabs(false, swath = true, false);
				}
				if (classified == true){
					AGGREGATE_WU_DELIV.buildDelivSubtabs(false, false, classified = true);
				}
			});
		},
		
		//Sets handlers for the deliverable-related buttons present on the detail page of an existing deliverable to update, cancel and
		//delete the deliverable or add a VA table if none is present
		setUpdateDelivButtonHandlers: function(demTabId = null, swathTabId = null, classifiedTabId = null){
			var tabId;
			var catUrl;
			var deleteUrl;
			var projectSpecUrl;
			var name;
			//Initialize deliverable type-specific variables
			if (demTabId != null){	
				tabId = demTabId;
				tabUrl = _aggregatedWuDeliverableTab.replace('123', demTabId);
				catUrl = tabUrl.replace('789', '1');
				preDeleteUrl = _deleteAggregatedWuDeliverable.replace("123", demTabId);
				deleteUrl = preDeleteUrl.replace('456', '1');
				projectSpecUrl = _getDelivProjectSpec.replace('123', demTabId);
				name = 'DEM';
			}
			if (swathTabId != null){
				tabId = swathTabId;
				tabUrl = _aggregatedWuDeliverableTab.replace('123', swathTabId);
				catUrl = tabUrl.replace('789', '2');
				preDeleteUrl = _deleteAggregatedWuDeliverable.replace("123", swathTabId);
				deleteUrl = preDeleteUrl.replace('456', '2');
				projectSpecUrl = _getDelivProjectSpec.replace('123', swathTabId);
				name = 'Swath';
			}
			if (classifiedTabId != null){			
				tabId = classifiedTabId;
				tabUrl = _aggregatedWuDeliverableTab.replace('123', classifiedTabId);
				catUrl = tabUrl.replace('789', '3');
				preDeleteUrl = _deleteAggregatedWuDeliverable.replace("123", classifiedTabId);
				deleteUrl = preDeleteUrl.replace('456', '3');
				projectSpecUrl = _getDelivProjectSpec.replace('123', classifiedTabId);
				name = 'Classified';
			}
			//Button click handlers
			$(document).off('click','#updateAggregatedWuDeliv').on('click', '#updateAggregatedWuDeliv', function (e){
				e.preventDefault();
				var json;
				if (demTabId != null){json = AGGREGATE_WU_DELIV.packageDemForm();}
				if (swathTabId != null){json = AGGREGATE_WU_DELIV.packageSwathForm();}	
				if (classifiedTabId != null){json = AGGREGATE_WU_DELIV.packageClassifiedForm();}
				$.ajax({
					url: catUrl.replace('456', _reviewId),
					type: 'POST',
					data: json,
					success: function(data) {
						if ('applied' in data){
							wus = data['applied'];
							while(wus.charAt(0) === ','){
								wus = wus.substr(1);
							}
							alert(name + ' UPDATE APPLIED TO WORK UNITS: ' + wus);
						}
						updateSelector = '#aggregatedWuDelivUpdate' + tabId;
						$(updateSelector).html(data['html']);
						if ((data['vaRequirement']) && (data['vaRequirement'] == 'False')){
							$('#noVaData').show();
						}
						_tabId = tabId;
						if(demTabId){
							AGGREGATE_WU_DELIV.buildDelivSubtabs(dem = true);
						}
						if(swathTabId){
							AGGREGATE_WU_DELIV.buildDelivSubtabs(false, swath = true, false);
						}
						if(classifiedTabId){
							AGGREGATE_WU_DELIV.buildDelivSubtabs(false, false, classified = true);
						}
					}
				});
			});
			$(document).off('click', '#cancelUpdateAggregatedWuDeliv').on('click', '#cancelUpdateAggregatedWuDeliv', function (e){
				e.preventDefault();
				$('#aggregatedWuDelivLink' + tabId).trigger('click');
			});
			$(document).off('click', '#deleteAggregatedWuDeliv').on('click', '#deleteAggregatedWuDeliv', function (e){
				e.preventDefault();
				var cont = confirm("Confirm Deletion.");
				if (cont){
                    $.ajax({
                        url: deleteUrl,
                        type: 'POST',
                        success: function(data) {
                            if (data['success'] != ''){
                                if(demTabId){
                                    AGGREGATE_WU_DELIV.buildDelivSubtabs(dem = true, false, false);
                                }
                                if(swathTabId){
                                    AGGREGATE_WU_DELIV.buildDelivSubtabs(false, swath = true, false);
                                }
                                if(classifiedTabId){
                                    AGGREGATE_WU_DELIV.buildDelivSubtabs(false, false, classified = true);
                                }
                            }
                        }
                    });
                }
                else{
                    return false;
                }
			});
		},
		
		//Called by the DEM object's 'buildDemSubtabHandlers' method to build the deliverable subtab controls, determine the tab and corresponding
		//content that should be shown to the user, builds that content, sets appropriate button click handlers and displays the content.
		buildDelivSubtabs: function(dem = false, swath = false, classified = false){
			//Reset SVA 'rows added' counter to 0
			FUNCTIONS.setRowsAdded(0);
			//Function vars
			var tabSelector;
			var deliverablesDivSelector = '#aggregatedWuDeliverables';
			var deliverableTabsUrl = _aggregatedWuDeliverableTabs.replace('123', _reviewId);
			var catUrl;
			var formUrl;
			var preDeleteErrorUrl;
			var deleteErrorUrl;
			var minVal;
			var ids = null;
			//Initialize deliverable type-specific variables
			if (dem == true){
				$('#breaklines').html('');
				tabSelector = '#demInfo';
				catUrl = deliverableTabsUrl.replace('456', '1');
				formUrl = _demForm.replace('123', _reviewId)
				preDeleteErrorUrl = _deleteError.replace('456','1');
			}
			if (swath == true){
				$('#classified').html('');
				tabSelector = '#swath';
				catUrl = deliverableTabsUrl.replace('456', '2');
				formUrl = _swathForm.replace('123', _reviewId);
				preDeleteErrorUrl = _deleteError.replace('456','2');
			}
			if (classified == true){
				$('#swath').html('');
				tabSelector = '#classified';
				catUrl = deliverableTabsUrl.replace('456', '3');
				formUrl = _classifiedForm.replace('123', _reviewId);
				preDeleteErrorUrl = _deleteError.replace('456','3');
			}
			//Builds the html for the tab objects and content area
			$.ajax({
				url: catUrl,
				type:'GET',
				success: function(data){
					$(tabSelector).html(data['html'])
					//Check for a 'minVal', the lowest tab ID value returned, the existence of which indicates
					//that deliverables/tabs of this type exist.  If no minval exists, the 'add' form is shown.
					var minVal;
					if (data['minVal']){
						minVal = data['minVal']
					}
					if (minVal != null){
						var previousSubtab = '';
						//Deliverable tabs click handler
						$('#aggregatedWuDelivTabObjects').on("click", "li", function (event) {
							event.preventDefault();
							if (previousSubtab !== ''){
								$(previousSubtab).html('');							
							}
							var subtabSelector = $(this).find('a').attr('href');
							previousSubtab = subtabSelector;
							//If the tab clicked is the 'add deliverable' tab, get the type-specific form, add its buttons
							//and set the button click handlers
							if (subtabSelector == '#aggregatedWuDelivAdd'){
								$.ajax({
									url: formUrl,
									type: "GET",
									success: function(data){
										var formHtml = data;
										var submitCi = '<input id = "createAggregatedWuDeliv" type=button class="btn-default" value="Submit">'
										var cancelCi = '<input id = "cancelCreateAggregatedWuDeliv" type=button class="btn-default" value="Cancel">'
										var html = formHtml + submitCi + cancelCi + '<br><br></div></div></div></div>';
										$('#aggregatedWuDelivAdd').html(html);
										if (dem == true){
											AGGREGATE_WU_DELIV.setAddDelivButtonHandlers(dem = true);
										}
										if (swath == true){
											AGGREGATE_WU_DELIV.setAddDelivButtonHandlers(false, true, false);
										}
										if (classified == true){
											AGGREGATE_WU_DELIV.setAddDelivButtonHandlers(false, false, true);
										}
									}
									
								});										
							}
							//If the tab clicked is not the 'add deliverable' tab, build the deliverable tab html
							//content and set handlers for updating the deliverable, the VA table, and deletion of
							//errors.
							else{
								var tabUrl;
								var tabId = subtabSelector.slice(24);
								var tabUrl =_aggregatedWuDeliverableTab.replace('123', tabId);
								var catUrl;
								$(subtabSelector).addClass('tab_pane active');
								if (dem == true){
									catUrl = tabUrl.replace('789', '1');
									
								}
								if (swath == true){
									catUrl = tabUrl.replace('789', '2');
								}
								if (classified == true){
									catUrl = tabUrl.replace('789', '3');
								}
								$.ajax({
									url: catUrl.replace('456', _reviewId),
									type: "GET",
									success: function(data) {
										var selector = '#aggregatedWuDelivUpdate' + tabId
										$(selector).html(data['html']);
										if (data['noVa']=='True'){
											$('#noVaData').show();										
										}
										if (dem == true){
											AGGREGATE_WU_DELIV.setUpdateDelivButtonHandlers(demTabId = tabId);
											AGGREGATE_WU_DELIV.setRemoveDelivCallbackHandlers(demTabId = tabId);
											AGGREGATE_WU_DELIV.setUpdateFormInputHandlers();
											FUNCTIONS.setEditVaTableHandlers(deliv = true, demTabId = tabId, swathTabId = null, classifiedTabId = null, buildTabMethod = AGGREGATE_WU_DELIV.buildDelivSubtabs);
											FUNCTIONS.setErrorButtonHandlers(tabId, false, null, null, true, false, false);
										    FUNCTIONS.setErrorTableHandlers(tabId, 1);
                                            FUNCTIONS.setEditErrorButtonHandlers(tabId, 1);
										}
										if (swath == true){
											AGGREGATE_WU_DELIV.setUpdateDelivButtonHandlers(null, tabId, null);
											AGGREGATE_WU_DELIV.setRemoveDelivCallbackHandlers(null, swathTabId = tabId, null);
											AGGREGATE_WU_DELIV.setUpdateFormInputHandlers();
											FUNCTIONS.setEditVaTableHandlers(deliv = true, demTabId = null, swathTabId = tabId, classifiedTabId = null, buildTabMethod = AGGREGATE_WU_DELIV.buildDelivSubtabs);
											FUNCTIONS.setErrorButtonHandlers(tabId, false, null, null, false, true, false);
										    FUNCTIONS.setErrorTableHandlers(tabId, 2);
                                            FUNCTIONS.setEditErrorButtonHandlers(tabId, 2);
										}
										if (classified == true){
										    FUNCTIONS.setEditClassificationTableHandlers();
											AGGREGATE_WU_DELIV.setUpdateDelivButtonHandlers(null, null, tabId);
											AGGREGATE_WU_DELIV.setRemoveDelivCallbackHandlers(null, null, classifiedTabId = tabId);
											AGGREGATE_WU_DELIV.setUpdateFormInputHandlers();
											FUNCTIONS.setEditVaTableHandlers(deliv = true, demTabId = null, swathTabId = null, classifiedTabId = tabId, buildTabMethod = AGGREGATE_WU_DELIV.buildDelivSubtabs);
											FUNCTIONS.setErrorButtonHandlers(tabId, false, null, null, false, false, true)
										    FUNCTIONS.setErrorTableHandlers(tabId, 3);
                                            FUNCTIONS.setEditErrorButtonHandlers(tabId, 3);
										}
										
										$(document).off('click', '.deleteErrorButton').on('click', '.deleteErrorButton', function(e){
											e.preventDefault();
											//Pull error number out of button ID
											error_id = $(this).attr('id').substr(11);
											var cont = confirm("Confirm Deletion.");
											if (cont){
                                                $.ajax({
                                                    url: preDeleteErrorUrl.replace('123', error_id),
                                                    processData: false,
                                                    contentType: false,
                                                    type: "POST",
                                                    success: function(data) {
                                                        //refresh if succeeded
                                                        if (data['success'] == 'True'){
                                                            $('#aggregatedWuDelivLink' + tabId).trigger('click');
                                                        }
                                                    }
                                                });
											}
											else{
											    return false;
											}
										})
										//Show the subtab CONTENT
										$(tabSelector).show();
									}
								});
							}
						});
					}
					//There are no deliverables yet, set the 'add form' button handlers.
					else{
						if (dem == true){
							AGGREGATE_WU_DELIV.setAddDelivButtonHandlers(true, false, false);
						}
						if (swath == true){
							AGGREGATE_WU_DELIV.setAddDelivButtonHandlers(false, true, false);
						}
						if (classified == true){
							AGGREGATE_WU_DELIV.setAddDelivButtonHandlers(false, false, true);
						}				
					}
					//If there's a tab ID (an update operation has been performed), click the corresponding deliverable subtab
					if (_tabId && _tabId != ''){
						$('#aggregatedWuDelivTabObjects li a[href="#aggregatedWuDelivUpdate' + _tabId + '"]').click();
						_tabId = '';
					}
					//If there's no tab ID (main tab clicked, deliverable deleted), click the tab with the lowest ID value (furthest left on display)
					else{
						$('#aggregatedWuDelivTabObjects li a[href="#aggregatedWuDelivUpdate' + minVal + '"]').click();
					}
					// Show all subtab controls
					$(deliverablesDivSelector).show();	
							
				}
			});			
		},
	};	
}());		