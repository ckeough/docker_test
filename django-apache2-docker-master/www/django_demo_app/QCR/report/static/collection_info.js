var COLLECTION_INFO = COLLECTION_INFO || (function(){
	//Object property URLs
	var _review;
	var _collectionInfo;
	var _ciForm;
	var _removeCollInfo;
	var _deleteCollInfo;
	var _checkRelatedWus;
	var _getProjectSpec;
	var _addVaTable;
	//Object property vars
	var _reviewId;
	
	return{
		//Initialization function depends on instantiated FUNCTIONS object
		init: function(urls, variables){
			if (FUNCTIONS){
				//Passed-in URLS
				_review = urls['review'];
				_collectionInfo = urls['collectionInfo'];				
				_ciForm = urls['ciForm'];
				_removeCollInfo = urls['removeCollInfo'];
				_deleteCollInfo = urls['deleteCollInfo'];
				_checkRelatedWus = urls['checkRelatedWus'];
				_getProjectSpec = urls['getProjectSpec'];
				_addVaTable = urls['addVaTable'];
				//Passed-in Variables
				_reviewId = variables['reviewId'];
			}
			else{
				alert('FATAL ERROR: \nQC REPORT FUNCTIONS OBJECT NOT INITIALIZED');
				url = _review.replace('123', _reviewId);
				location.href = url;
				//LOG ME!!
			}
		},
		
		//Functions to package forms for dispatch to server
		packageCiForm: function(){
			var collStartTextValue = $('#collStartText').val();
			if(collStartTextValue){
                var collStartTime = FUNCTIONS.reformatInputDateTime(collStartTextValue);
			}
			else collStartTime = null;
			var collEndTextValue = $('#collEndText').val();
			if(collEndTextValue){
			    var collEndTime = FUNCTIONS.reformatInputDateTime(collEndTextValue);
			}
			else collEndTime = null;
			var kvpString = FUNCTIONS.packageWorkUnitMultiSelect('#wuCiMultiSelect')
			var json = JSON.stringify({
				'areaExtent': $('#areaExtent').val(),
				'collStart': collStartTime,
				'collEnd': collEndTime,
				'tileSize': $('#tileSize').val(), 
				'tsUnits': $('select[name=selectTsUnits]').val(),
				'demRes': $('#demRes').val(),
				'demResUnits': $('select[name=selectDemResUnits]').val(),
				'horSrs': $('#horSrs').val(),
				'horEpsg':$('#horEpsg').val(),
				'vertSrs': $('#vertSrs').val(),
				'vertEpsg':$('#vertEpsg').val(),
				'qualLevel': $('select[name=qualLevel]').val(),
				'lasVersion': $('#lasVersion').val(),			
				'configNps': $('#configNps').val(),
				'configNpsUnits': $('select[name=selectConfigNpsUnits]').val(),
				'configAnps': $('#configAnps').val(),
				'configAnpsUnits': $('select[name=selectConfigAnpsUnits]').val(),			
				'configAnpsMethod': $('#configAnpsMethod').val(),			
				'hydroTreatment': $('select[name=selectHydroTreatment]').val(),
				'sensorType': $('select[name=sensorType]').val(),
				'sensorUsed': $('select[name=sensorUsed]').val(),
				'scanAngle': $('#scanAngle').val()
			})
			var rmvBracket = json.slice(0,-1);
			var finalJson = rmvBracket + ',' + kvpString + '}'
			return finalJson;
		},

		packageAddVaForm: function(){
			formDict = {};
			if ($('#fvaReqChkpts').val() == '' && $('#fvaReqVal').val() == ''){
				if ($('#vvaReqChkpts').val() == '' && $('#vvaReqVal').val() == ''){
					if ($('#nvaReqChkpts').val() == '' && $('#nvaReqVal').val() == ''){
						formDict['missingData'] = 'True'; 
						return formDict;
					}
				}
			};
			if ($('#cvaReqChkpts').val() == '' && $('#cvaReqVal').val() == ''){
				if ($('#vvaReqChkpts').val() == '' && $('#vvaReqVal').val() == ''){
					if ($('#nvaReqChkpts').val() == '' && $('#nvaReqVal').val() == ''){
						formDict['missingData'] = 'True'; 
						return formDict;
					}
				}
			};
			if ($('#vvaReqChkpts').val() == '' && $('#vvaReqVal').val() == ''){
				if ($('#fvaReqChkpts').val() == '' && $('#fvaReqVal').val() == ''){
					if ($('#cvaReqChkpts').val() == '' && $('#cvaReqVal').val() == ''){
						formDict['missingData'] = 'True'; 
						return formDict;
					}
				}
			};
			if ($('#nvaReqChkpts').val() == '' && $('#nvaReqVal').val() == ''){
				if ($('#fvaReqChkpts').val() == '' && $('#fvaReqVal').val() == ''){
					if ($('#cvaReqChkpts').val() == '' && $('#cvaReqVal').val() == ''){
						formDict['missingData'] = 'True'; 
						return formDict;
					}
				}
			};
			formDict['fundChkpt'] = $('#fvaReqChkpts').val();
			formDict['consChkpt'] = $('#cvaReqChkpts').val();
			formDict['vegChkpt'] = $('#vvaReqChkpts').val();
			formDict['nonvegChkpt'] = $('#nvaReqChkpts').val();
			formDict['fundVal'] = $('#fvaReqVal').val();
			formDict['consVal'] = $('#cvaReqVal').val();
			formDict['vegVal'] = $('#vvaReqVal').val();
			formDict['nonvegVal'] = $('#nvaReqVal').val();
			
			svaIds = [];
			$('#addReq10Table tr').each(function(){
				rowId = $(this).attr('id');
				measureType = rowId.substr(0,3);
				if (measureType == 'sva'){
					svaId = rowId.substr(6);
					landcover = $('#svaLandcoverEdit' + svaId).val();
					if (landcover !== ''){
						landcover = landcover.trim();
					}
					svaChkpts = $('#svaReqChkptsEdit' + svaId).val();
					if (svaChkpts !== '' && svaChkpts !== null){
						svaChkpts = svaChkpts.trim();
					}
					svaVal = $('#svaReqValEdit' + svaId).val();
					if (svaVal !== '' && svaVal != null){
						svaVal.trim();
					}
					if (landcover == '' && svaChkpts == '' && svaVal == ''){
						return true;
					}
					else{
						svaIds.push(svaId);
						formDict['suppLandcover' + svaId] = landcover;
						formDict['suppChkpts' + svaId] = svaChkpts;
						formDict['suppVal' + svaId] = svaVal;
					}
				};				
			});
			formDict['svaIds'] = svaIds;
			return formDict;
		},
		
		//Functions to enable/disable update and cancel buttons on 'Update' form
		ciEditButtonsEnable: function(){
			$('#updateCollectionInfo').prop('disabled', false);
			$('#updateCollectionInfo').css('opacity', 1); 
			$('#cancelUpdateCollectionInfo').prop('disabled', false);
			$('#cancelUpdateCollectionInfo').css('opacity', 1); 	
		},
		
		ciEditButtonsDisable: function(){
			$('#updateCollectionInfo').prop('disabled', true);
			$('#updateCollectionInfo').css('opacity', 0.5);
			$('#cancelUpdateCollectionInfo').prop('disabled', true);
			$('#cancelUpdateCollectionInfo').css('opacity', 0.5);	
		},		
			
		//Calls the FUNCTIONS.buildWorkUnitSubtabs method to build all of the work unit subtab
		//controls and passes in the 'buildCiSubtab' method to render the actual tab content
		buildCollectionInfoTab: function(){
			FUNCTIONS.buildWorkUnitSubtabs('#collInfo', COLLECTION_INFO.buildCiSubtab, _reviewId);
		},
		
		//Builds the actual collection info tab content.  The html returned from the view will be an 'add' form
		//if no collection info exists for the WU, or will be the collection info/VA detail if collection info 
		//exists. Both sets of button handlers are set here to handle either case.
		buildCiSubtab: function(workUnitId){
			$.ajax({
				url: _collectionInfo.replace('123', workUnitId),
				type: "GET",
				success: function(data) {
					updateWuSelector = '#workUnitUpdate' + workUnitId;
					//Set the Collection Info/Va Work Unit tab's HTML
					$(updateWuSelector).html(data['html']);
					if ((data['vaRequirement']) && (data['vaRequirement'] == 'False')){
						$('#noVaData').show();
					}
					//Set the add ci/delete wu controls for the add collection info form
					COLLECTION_INFO.setAddCollInfoButtonHandlers(workUnitId);
					//Set initial ci update button states, form input event listeners, and button click handlers
					COLLECTION_INFO.setUpdateCollInfoFormInputHandlers();
					COLLECTION_INFO.setUpdateCollInfoButtonHandlers(workUnitId);
					COLLECTION_INFO.setAddVaTableHandlers(workUnitId);
					FUNCTIONS.setEditVaTableHandlers();
				}
			});	
		},
		
		//'Add Collection Info' form button click handlers.  Shows the add form when user clicks the 'add' button, 
		//and sets handlers for create and cancel create.
		setAddCollInfoButtonHandlers: function(workUnitId){
			$(document).off('click', '#addCollInfo').on('click', '#addCollInfo', function (e){
				e.preventDefault();
				$.ajax({
					url: _ciForm + workUnitId,
					type: "GET",
					success: function(data) {
						var formHtml = data;
						var submitCi = '<input id = "createCi" type=button class="btn-default" value="Submit">'
						var cancelCi = '<input id = "cancelCreateCi" type=button class="btn-default" value="Cancel">'
						var html = formHtml + submitCi + cancelCi + '<br><br></div></div></div></div>';
						$('#workUnitUpdate' + workUnitId).html(html);
						
						
					}
				});										
			});				
			$(document).off('click', '#createCi').on('click', '#createCi', function (e){
				json = COLLECTION_INFO.packageCiForm();
				e.preventDefault();
				$.ajax({
					url: _collectionInfo.replace('123', workUnitId),
					type: "POST",
					data: json,
					success: function(data) {
						alert('COLLECTION INFO APPLIED TO WORK UNITS: ' + data['applied']);
						$('#wuLink' + workUnitId).trigger('click');								
					}
				})											
			});
			$(document).off('click', '#cancelCreateCi').on('click', '#cancelCreateCi', function (e){
				$('#wuLink' + workUnitId).trigger('click');
			});	
		},
		
		//Handles button clicks related to the update, removal or deletion of collection info, and the 'add VA requirements'
		//button, which displays the add VA requirements table.
		setUpdateCollInfoButtonHandlers: function(workUnitId){		
			$(document).off('click','#updateCollectionInfo').on('click', '#updateCollectionInfo', function (e){
				e.preventDefault();
				var updateCiJson = COLLECTION_INFO.packageCiForm();
				var jsonData = updateCiJson;

				$.ajax({
					url: _collectionInfo.replace('123', workUnitId),
					type: 'POST',
					data: jsonData, 
					success: function(data) {
						alert(data['success']);	
						if ('applied' in data){
							wus = data['applied'];
							while(wus.charAt(0) === ','){
								wus = wus.substr(1);
							}
							alert('COLLECTION INFO UPDATE APPLIED TO WORK UNITS: ' + wus);
						}
						updateWuSelector = '#workUnitUpdate' + workUnitId;
						//Set the Collection Info/Va Work Unit tab's HTML
						$(updateWuSelector).html(data['html']);
						if ((data['vaRequirement']) && (data['vaRequirement'] == 'False')){
							$('#noVaData').show();										
						}
						//Set the add ci/delete wu controls for the add collection info form
						COLLECTION_INFO.setAddCollInfoButtonHandlers(workUnitId);
						//Set initial ci update button states, form input event listeners, and button click handlers
						COLLECTION_INFO.setUpdateCollInfoButtonHandlers(workUnitId);
						COLLECTION_INFO.setUpdateCollInfoFormInputHandlers();
						COLLECTION_INFO.setAddVaTableHandlers(workUnitId);
						FUNCTIONS.setEditVaTableHandlers();
					}
				});
			});		
			$(document).off('click', '#cancelUpdateCollectionInfo').on('click', '#cancelUpdateCollectionInfo', function (e){
				e.preventDefault();
				$('#wuLink' + workUnitId).trigger('click');
			});	
			$(document).off('click', '#deleteCollectionInfo').on('click', '#deleteCollectionInfo', function (e){
				e.preventDefault();
				var cont = confirm("Confirm Deletion.");
				if (cont){
                    $.ajax({
                        url: _deleteCollInfo.replace("123", workUnitId),
                        type: 'POST',
                        success: function(data) {
                            if (data['success'] != ''){
                                $('#wuLink' + workUnitId).trigger('click');
                            }
                        }
                    });
				}
				else{
				    return false;
				}
			});													
			$(document).off('click', '#removeCollectionInfo').on('click', '#removeCollectionInfo', function (e){
				e.preventDefault();
				$.ajax({
					url: _checkRelatedWus.replace('123', workUnitId),
					type: 'GET',
					success: function(data) {											
						if (data['warn']=='true'){
							var cont = confirm("This is the last work unit associated with this set of Collection Information.  Removing the association will delete the CollectionInformation.  Continue?");
							if (cont == true){
								$.ajax({
									url: _removeCollInfo.replace('123', workUnitId),
									type: 'POST',
									success: function(data) {											
										if (data['success'] != ''){
											$('#wuLink' + workUnitId).trigger('click');
										};
									}
								});
							}
							else{
								return false;
							}
						}
						else{
							$.ajax({
								url: _removeCollInfo.replace('123', workUnitId),
								type: 'POST',
								success: function(data) {											
									if (data['success'] != ''){
										$('#wuLink' + workUnitId).trigger('click');
									};
								}
							});
						}
					}
				});
			});	
			
			$(document).off('click','#addVaRequirements').on('click', '#addVaRequirements', function (e){
				e.preventDefault();
				$.ajax({
					url: _getProjectSpec.replace('123', workUnitId),
					type: 'GET',
					success: function(data) {
						var div = '#addReq' + data['spec'];
						$('#noVaData').hide();
						$('.addReqs').show();
						$(div).show();
					}
				});								
			});	
		},
		
		//'Update' form field/select event handlers (to activate/deactivate update related buttons)
		setUpdateCollInfoFormInputHandlers: function(updateWuSelector){
			COLLECTION_INFO.ciEditButtonsDisable();									
			$(document).off('keyup', '#collectionInfoTable input[type="text"]').on('keyup', '#collectionInfoTable input[type="text"]', function() {
				if($(this).val() != '') {
					COLLECTION_INFO.ciEditButtonsEnable();
				}
			});	
			$(document).off('change', '#collectionInfoTable select').on('change', '#collectionInfoTable select', function() {
				COLLECTION_INFO.ciEditButtonsEnable();
			});	
			$(document).off('change','#collectionInfoTable .number').on('change', '#collectionInfoTable .number' , function() {		
				COLLECTION_INFO.ciEditButtonsEnable();
			});		
			$(document).off('change', "#wuCiMultiSelect").on('change', "#wuCiMultiSelect", function(e){		
				COLLECTION_INFO.ciEditButtonsEnable();
			});
		},
				
		//Button handlers for 'Add' VA table form (add/cancel/add sva row)
		setAddVaTableHandlers: function(workUnitId){
			$(document).off('click', '#addVaTableBtn').on('click', '#addVaTableBtn', function (e){
				e.preventDefault();
				var jsonDict = COLLECTION_INFO.packageAddVaForm();
				if ('missingData' in jsonDict){
					alert('Data is missing from the VA Requirements table.  Please complete data entry and resubmit.\n\n**SVA measure rows may be left blank**' );
					return false;
				};				
				var json = JSON.stringify(jsonDict);
				var url = _addVaTable.replace('123', workUnitId);
				$.ajax({
					url: url,
					type: "POST",
					data: json,
					success: function(data) {
						$('#collInfoVaTable').html(data['html'])
						$('.addReqs').hide();
						$('.addReq').hide();
						$('.addVaReqTable').find("input").val("");
						$('#resetVaReq').hide();
						$('#updateVaReq').hide();
					}
				});							
			});		
			$(document).off('click', '#cancelVaTableBtn').on('click', '#cancelVaTableBtn', function (e){
				e.preventDefault();
				$('.addVaReqTable').find("input").val("");
				$('#addReq10Table tr').each(function(){
					rowId = $(this).attr('id');
					measureType = rowId.substr(0,3);
					if (measureType == 'sva'){
						$('#' + rowId).remove();
					};
				});
				$('.addReqs').hide();
				$('.addReq').hide();
				$('#noVaData').show();
			});	
			$(document).off('click', '#addSvaRow').on('click', '#addSvaRow', function (e){
				e.preventDefault();
				var tableId = '#addReq10Table';
				FUNCTIONS.addSvaRow(tableId);
			});			
		},
	
	};	
}());