var FUNCTIONS = FUNCTIONS || (function(){
	
	//property variables
	var _reviewId;
	var _workUnitId;
	var _rowsAdded;
	var _classificationsAdded;
	var _subtabId;
	var _classificationChecked;
	//object property urls
	var _review;
	var _workUnits;
	//Requirements-only VA table URLs (collection info)
	var _getVaTable;
	var _updateVaTable;
	var _deleteVaTable;
	var _getNextSva;
	var _svaExists;
	//Aggregated Wu Deliverable VA Table URLs
	var _getDelivVaTable;
	var _updateDelivVaTable;
	var _deleteDelivVaTable;
	//Error URLs
	var _addError;
	var _addErrorAggregatedWuDeliverable;
	var _deleteError;
	var _updateError;
	var _getError;
	var _getErrors;
	var _getErrorsAgg;
	var _updateErrors;
	var _updateErrorsAgg;
	var _populateErrorSubType;
	//Classifications Table Urls
	var _getClassificationsTable;
	var _deleteClassifications;
	var _updateClassifications;
	
	return{
		init: function(urls, vars){
			//passed-in variable values
			_reviewId = vars['reviewId'];
			_rowsAdded = 0;
			_classificationsAdded = 0;
			_classificationChecked = false;
			//passed-in URL values
			_review = urls['review'];
			_workUnits = urls['workUnits'];
			//Requirements-only VA table URLs (collection info)
			_getVaTable = urls['getVaTable'];
			_updateVaTable = urls['updateVaTable'];
			_deleteVaTable = urls['deleteVaTable'];
			_getNextSva = urls['getNextSva'];
			_svaExists = urls['svaExists'];
			//Aggregated WU Deliverable VA Table URLs
			_getDelivVaTable = urls['getDelivVaTable'];
			_updateDelivVaTable = urls['updateDelivVaTable'];
			_deleteDelivVaTable = urls['deleteDelivVaTable'];
			//Add Error URLs
			_addError = urls['addError'];
			_addErrorAggregatedWuDeliverable = urls['addErrorAggregatedWuDeliverable'];
			_deleteError = urls['deleteError'];
			_updateError = urls['updateError'];
			_getError = urls['getError'];
			_getErrors = urls['getErrors'];
			_getErrorsAgg = urls['getErrorsAgg'];
			_updateErrors = urls['updateErrors'];
			_updateErrorsAgg = urls['updateErrorsAgg'];
			_populateErrorSubType = urls['populateErrorSubType'];
			_deleteImages = urls['deleteImages'];
			//Classifications Table URLs
			_getClassificationsTable = urls['getClassificationsTable'];
			_deleteClassifications = urls['deleteClassifications'];
			_updateClassifications = urls['updateClassifications'];
		},
		
		//Functions to package forms for dispatch to server
		packageDelivForm: function(){
		    var kvpString = '"workUnits":"'
			$('#wuDelivMultiSelect :selected').each(function(i, selected){
				var selItem = $(selected).val().toString();
				var selId = selItem.substring(selItem.lastIndexOf(" ") + 1, selItem.length);
				kvpString += selId + ','
			});
			if (kvpString.substring(kvpString.length-1) == ','){
				kvpString = kvpString.slice(0,-1);
			}
			kvpString = kvpString + '"';
			json = JSON.stringify({
				'deliverableCategory': $('select[name=addDeliverableCategory]').val(),
				'description': $('#addDescription').val(),
				'quantity':$('#addQuantity').val(),
				'spatRef':$('#addSpatRef').val(),
				'reqPerContract': $('select[name=addReqPerContract]').val(),
				'reqPerSpec': $('select[name=addReqPerSpec]').val(),
				'delivered': $('select[name=addDelivered]').val(),
				'comment': $('#addComment').val(),
				'accepted': $('select[name=addAccepted]').val()
			})
			rmvBracket = json.slice(0,-1);
			finalJson = rmvBracket + ',' + kvpString + '}'
			return finalJson;
		},
		
		packageWorkUnitMultiSelect: function(multiSelectSelector){
			var kvpString = '"workUnits":"' 
			$(multiSelectSelector + ' :selected').each(function(i, selected){
				var selItem = $(selected).val().toString();	
				var selId = selItem.substring(selItem.lastIndexOf(" ") + 1, selItem.length);
				kvpString += selId + ','
			});
			if (kvpString.substring(kvpString.length-1) == ','){
				kvpString = kvpString.slice(0,-1);
			}
			kvpString = kvpString + '"';
			return kvpString;
		},
		
		packageEditVaForm: function(){
			formDict = {};
			if ($('#fvaReqChkptsEdit').val() == '' && $('#fvaReqValEdit').val() == ''){
				if ($('#vvaReqChkptsEdit').val() == '' && $('#vvaReqValEdit').val() == ''){
					if ($('#nvaReqChkptsEdit').val() == '' && $('#nvaReqValEdit').val() == ''){
						formDict['missingData'] = 'fva'; 
						return formDict
					}
				}
			}
			if ($('#cvaReqChkptsEdit').val() == '' && $('#cvaReqValEdit').val() == ''){
				if ($('#vvaReqChkptsEdit').val() == '' && $('#vvaReqValEdit').val() == ''){
					if ($('#nvaReqChkptsEdit').val() == '' && $('#nvaReqValEdit').val() == ''){
						formDict['missingData'] = 'cva'; 
						return formDict
					}
				}
			}
			if ($('#vvaReqChkptsEdit').val() == '' && $('#vvaReqValEdit').val() == ''){
				if ($('#fvaReqChkptsEdit').val() == '' && $('#fvaReqValEdit').val() == ''){
					if ($('#cvaReqChkptsEdit').val() == '' && $('#cvaReqValEdit').val() == ''){
						formDict['missingData'] = 'vva'; 
						return formDict
					}
				}
			}
			if ($('#nvaReqChkptsEdit').val() == '' && $('#nvaReqValEdit').val() == ''){
				if ($('#fvaReqChkptsEdit').val() == '' && $('#fvaReqValEdit').val() == ''){
					if ($('#cvaReqChkptsEdit').val() == '' && $('#cvaReqValEdit').val() == ''){
						formDict['missingData'] = 'vva'; 
						return formDict
					}
				}
			}
			formDict['fundChkpt'] = $('#fvaReqChkptsEdit').val();
			formDict['consChkpt'] = $('#cvaReqChkptsEdit').val();
			formDict['vegChkpt'] = $('#vvaReqChkptsEdit').val();
			formDict['nonvegChkpt'] = $('#nvaReqChkptsEdit').val();
			formDict['fundVal'] = $('#fvaReqValEdit').val();
			formDict['consVal'] = $('#cvaReqValEdit').val();
			formDict['vegVal'] = $('#vvaReqValEdit').val();
			formDict['nonvegVal'] = $('#nvaReqValEdit').val();
			
			formDict['repfundChkpt'] = $('#fvaRepChkptsEdit').val();
			formDict['repconsChkpt'] = $('#cvaRepChkptsEdit').val();
			formDict['repvegChkpt'] = $('#vvaRepChkptsEdit').val();
			formDict['repnonvegChkpt'] = $('#nvaRepChkptsEdit').val();
			formDict['repfundVal'] = $('#fvaRepValEdit').val();
			formDict['repconsVal'] = $('#cvaRepValEdit').val();
			formDict['repvegVal'] = $('#vvaRepValEdit').val();
			formDict['repnonvegVal'] = $('#nvaRepValEdit').val();
			
			formDict['testfundChkpt'] = $('#fvaTestChkptsEdit').val();
			formDict['testconsChkpt'] = $('#cvaTestChkptsEdit').val();
			formDict['testvegChkpt'] = $('#vvaTestChkptsEdit').val();
			formDict['testnonvegChkpt'] = $('#nvaTestChkptsEdit').val();
			formDict['testfundVal'] = $('#fvaTestValEdit').val();
			formDict['testconsVal'] = $('#cvaTestValEdit').val();
			formDict['testvegVal'] = $('#vvaTestValEdit').val();
			formDict['testnonvegVal'] = $('#nvaTestValEdit').val();
			
			var svaIds = [];
			var deleteIds = [];
			$('.vaReqTable tr').each(function(){
				rowId = $(this).attr('id');
				measureType = rowId.substr(0,3);

				if (measureType == 'sva'){
					svaId = rowId.substr(6);
					landcover = $('#svaLandcoverEdit' + svaId).val();
					if (landcover !== ''){
						landcover = landcover.trim();
					}
					svaChkpts = $('#svaReqChkptsEdit' + svaId).val();
					if (svaChkpts !== ''){
						svaChkpts = svaChkpts.trim();
					}
					svaVal = $('#svaReqValEdit' + svaId).val();
					if (svaVal !== ''){
						svaVal.trim();
					}
					
					svaRepChkpts = $('#svaRepChkptsEdit' + svaId).val();
					if (svaRepChkpts !== '' && svaRepChkpts != null){
						svaRepChkpts.trim();
					}
					svaRepVal = $('#svaRepValEdit' + svaId).val();
					if (svaRepVal !== '' && svaRepVal != null){
						svaRepVal.trim();
					}
					svaTestChkpts = $('#svaTestChkptsEdit' + svaId).val();
					if (svaTestChkpts !== '' && svaTestChkpts != null){
						svaTestChkpts.trim();
					}
					svaTestVal = $('#svaTestValEdit' + svaId).val();
					if (svaTestVal !== '' && svaTestVal != null){
						svaTestVal.trim();
					}
					
					if (landcover == '' && svaChkpts == '' && svaVal == ''){
						url = _svaExists.replace('123', svaId)
						$.ajax({
							url: url,
							async: false,
							type: "GET",
							success: function(data) {
								if (data['svaExists'] == 'True'){
									deleteIds.push(svaId)
								}
							}
						});
					}
					else{
						svaIds.push(svaId);
						formDict['suppLandcover' + svaId] = landcover;
						formDict['suppChkpts' + svaId] = svaChkpts;
						formDict['suppVal' + svaId] = svaVal;
						formDict['repSuppChkpts' + svaId] = svaRepChkpts;
						formDict['repSuppVal' + svaId] = svaRepVal;
						formDict['testSuppChkpts' + svaId] = svaTestChkpts;
						formDict['testSuppVal' + svaId] = svaTestVal;
					}
				};
			
			});
			formDict['deleteIds'] = deleteIds;
			formDict['svaIds'] = svaIds;
			return formDict;
		},
		
		packageErrorForm: function(id, file = null){
			var typeSelectorString = '#addSelectErrorType' + id +' option:selected';
			var subtypeSelector = '#addSelectErrorSubtype' + id +' option:selected';
			var descriptionSelector = '#addErrorDesc' + id;
			var imageSelector = '#addErrorImg' + id;
			var locSelector = '#addErrorLoc' + id;
			var resolvedSelectorString = '#addErrorResolved' + id + ' option:selected';
			
			//Location string validation
			locValue =  $(locSelector).val();
			locStrings = locValue.split('.');
			if (locStrings.length !== 3){
				alert('The location field value must be in the format "(d)ddmmss.ssss(d)ddmmss.ssss".  Please re-enter.')
				return false	
			}
			
			if (locStrings[0].length < 6 || locStrings[0].length >7){
				alert('The location field value must be in the format "(d)ddmmss.ssss(d)ddmmss.ssss".  Please re-enter.')
				return false				
			}

			if (locStrings[1].length < 10 || locStrings[1].length >11){
				alert('The location field value must be in the format "(d)ddmmss.ssss(d)ddmmss.ssss".  Please re-enter.')
				return false				
			}

			if (locStrings[2].length !== 4){
				alert('The location field value must be in the format "(d)ddmmss.ssss(d)ddmmss.ssss".  Please re-enter.')
				return false				
			}

			formdata = new FormData();
			formdata.append('type', $(typeSelectorString).val());
			if($(subtypeSelector).val()!='NONE'){
			    formdata.append('subtype', $(subtypeSelector).val());
			}
			else{
			    formdata.append('subtype', '');
			}
			formdata.append('description', $(descriptionSelector).val());
			formdata.append('loc', $(locSelector).val());
			if (file != null){
				formdata.append('image', file)
			}
			formdata.append('resolved',  $(resolvedSelectorString).val());
			return formdata;
		},

        packageErrorUpdateForm: function(id, file = null){
			var typeSelectorString = '#errorType' + id +' option:selected';
			var subtypeSelector = '#errorSubtype' + id +' option:selected';
			var descriptionSelector = '#errorDesc' + id;
			var imageSelector = '#addErrorImg' + id;
			var locSelector = '#errorLoc' + id;
			var resolvedSelectorString = '#errorResolved' + id + ' option:selected';
            formdata = new FormData();
			formdata.append('type', $(typeSelectorString).val());
			if($(subtypeSelector).val()!='NONE'){
			    formdata.append('subtype', $(subtypeSelector).val());
			}
			else{
			    formdata.append('subtype', '');
			}
			formdata.append('description', $(descriptionSelector).val());
			formdata.append('loc', $(locSelector).val());
			if (file != null){
				formdata.append('image', file)
			}
			formdata.append('resolved',  $(resolvedSelectorString).val());
			return formdata;
		},

        packageErrorTable: function(id){
            var statusSelectorString = '.errorStatus'+id;
            formData = {};
            $(statusSelectorString).each(function(){
                formData[$(this).attr('id').substr(11)] = $(this).val();
            })
            return formData;
        },

		packageClassificationsForm: function(){
		    formDict = {};
		    formDict['numNewRows'] = 0;
            if(_classificationsAdded){
                formDict['numNewRows'] = _classificationsAdded;
                $('.newClassification').each(function(){
                    var rowNum = $(this).attr('id').substr(20)
                        $(this).find('input').each(function(){
                            intype = $(this).attr('id').substr(17);
                            if (intype == 'Id' + rowNum){
                                formDict['newCID' + rowNum] = $(this).val();
                            }
                            if (intype == 'Type' + rowNum){
                                formDict['newCType' + rowNum] = $(this).val();
                            }
                        });
                    });
                }
            $('.classificationRow').each(function(){
                var cPK = $(this).attr('id').substr(17);
                $(this).find('input').each(function(){
                    intype = $(this).attr('id').substr(14);
                    if (intype == 'Id' + cPK){
                        formDict['cID' + cPK] = $(this).val();
                    }
                    if (intype == 'Type' + cPK){
                        formDict['cType' + cPK] = $(this).val();
                    }
                });
            });
            return formDict;
		},

		//Reformats Datetime values for consumption by Django/Postgres
		reformatInputDateTime: function(inputDateTime){
			var stripAmPm = inputDateTime.substr(0, inputDateTime.length-3);
			var amPm = inputDateTime.substr(-2, inputDateTime.length);
			var dateTimeArray = inputDateTime.split(' ');
			var date = dateTimeArray[0];
			var dateArray = date.split('/');
			var month = dateArray[0];
			var day = dateArray[1];
			var year = dateArray[2];
			var reformattedDate = year + '-' + month + '-' + day;
			var time = dateTimeArray[1];
			var timeArray = time.split(':');
			var hour = parseInt(timeArray[0]);
			var minutes = timeArray[1];
			var seconds = '00'
			if (amPm === 'PM'){
				if (hour !== 12){
					hour = hour + 12;
					hour = hour.toString();
				}
			}
			else{
				if (hour == 12){
					hour = "00";
				}
			}
			var reformattedTime = hour + ':' + minutes + ':' + seconds;
			var reformattedDateTime = reformattedDate + ' ' + reformattedTime;
			return reformattedDateTime
		},

		//Builds the tab controls for the collection info tab and for generic deliverables tabs,
		//which are sorted by work units.  Sets the tab click handlers for each case.
		buildWorkUnitSubtabs: function(tabSelector, tabFunction, reviewId, generic = false, genericCategory = null){
			var minVal;
			_rowsAdded = 0;
			$.ajax({
				url: _workUnits.replace('123', reviewId),
				type: "GET",
				success: function(data) {
					$(tabSelector).html(data['html']);
					if (generic == true){
						FUNCTIONS.setWuTabClickHandler(tabFunction, data, generic, genericCategory);
					}
					else{
						FUNCTIONS.setWuTabClickHandler(tabFunction, data)
					}
				}
			});
		},
					
		//Handles Work Unit tab clicks.  Determines the selected tab and uses a function that is passed in 
		//by the caller to build the tab's content
		setWuTabClickHandler: function(tabFunction, responseData, generic = false, genericCategory){
			minVal = responseData['minVal'];
			var previousSubtab = '';
			$('#wuTabObjects').on("click", "li", function (event) {
				event.preventDefault();
				// Prior to changing the active tab id, the current tab selector is stored in the 'previous' variable
				// so that its html may be reset to empty before loading the new tab's html.
				if (previousSubtab !== ''){
					$(previousSubtab).html('');
				}
				var subtabSelector = $(this).find('a').attr('href');
				previousSubtab = subtabSelector;
				//Set the active tab and get the 'active' work unit ID from the tab name
				$(subtabSelector).addClass('tab_pane active');
				workUnitId = subtabSelector.slice(15);		
				_workUnitId = workUnitId
				//A generic deliverable tab is the caller, this will be a function that identifies the deliverable 
				//category and builds the tab content specific to that category.
				if(generic == true){
					tabFunction(workUnitId, genericCategory, subtabSelector);
				}
				//Collection Info tab is the caller, this will be a function that builds the CI tab content
				else{
					tabFunction(workUnitId);
				}
			});
			//Show the work unit tab controls
			$('#workUnits').show();
			//If the _workUnitId variable is set (create/update operations), click the tab corresponding to the _workUnitId variable 
			if (_workUnitId){
				$('#wuTabObjects li a[href="#workUnitUpdate' + _workUnitId + '"]').click();
			}
			//If no _workUnitId value, select the tab corresponding to the minVal variable (leftmost tab in the view).
			else {
				$('#wuTabObjects li a[href="#workUnitUpdate' + minVal + '"]').click();
			}
		},
		
		//Gets the highest ID for existing SVA objects from the server, increments it by one and assigns
		//that ID to a new SVA row generated in JS.  This way, if updates to existing SVAs are combined
		//with the addition of new SVAs, the application can keep track of the object ID numbers to apply 
		//updates to. The deliv and callback parameters are used when the method is called by the 
		//'addDelivSvaRow' function.
		addSvaRow: function(tableSelector, edit = false, reqId = null, deliv = false, callback = null){
			_rowsAdded = _rowsAdded + 1;
			var newRowHtml = '';
			var svaId = '';
			var url = _getNextSva;
			$.ajax({
				url: url,
				type: "GET",
				success: function(data) {
					svaId = parseInt(data['svaId']) + _rowsAdded;
					newRowHtml = '<tr id = "svaRow' + svaId + '"><td>Supplemental VA</td>' + 
						'<td><input type="text" id="svaLandcoverEdit' + svaId + '" value = "" style = "width:100px"></td>' +
						'<td><input type="number" id="svaReqChkptsEdit' + svaId + '" value = "" style = "width:100px"></td>' +
						'<td><input type="number" id="svaReqValEdit' + svaId + '" value = "" style = "width:100px"></td >';
					if (deliv == false){
						$(tableSelector + ' tbody').append(newRowHtml);	
					}
					var returnVals = function(){
						var html = newRowHtml;
						var sva = svaId;
						return{
							html: html,
							sva: sva
						};
					};
					retVals = returnVals();
					if (callback){
						callback(tableSelector, retVals);
						return true;
					}
					else{
						var finalHtml = retVals.html;
						finalHtml += '</tr>';
						return finalHtml;
					}
				}
			});
			
		},
		
		//Used to add an SVA row to an aggregated wu deliverable VA table.  Calls the above 'addSvaRow' function and
		//passes in the callback function to add fields to the empty row for reported and tested values.
		addDelivSvaRow: function(tableSelector, edit = false, reqId = null){
			var callback = function(tableSelector, values){
				html = values.html;
				svaId = values.sva;
				html += '<td><input type="number" id="svaRepChkptsEdit' + svaId + '" value = "" style = "width:100px"></td >' +
						'<td><input type="number" id="svaRepValEdit' + svaId + '" value = "" style = "width:100px"></td>' +
						'<td><input type="number" id="svaTestChkptsEdit' + svaId + '" value = "" style = "width:100px"></td >' +
						'<td><input type="number" id="svaTestValEdit' + svaId + '" value = "" style = "width:100px"></td></tr>';
				$(tableSelector + ' tbody').append(html);
			}
			FUNCTIONS.addSvaRow(tableSelector, edit, reqId, deliv = true, callback);
			
		},

		//Handles VA table click events to Add an SVA row, reset the VA table to original values, update the VA table,
		//and delete the VA table.  Also handles the keyup event within the VA table fields in order to activate and
		//deactivate the reset/update buttons.
		setEditVaTableHandlers: function(deliv = false, demTabId = null, swathTabId = null, classifiedTabId = null, buildTabMethod = null){
			$('#resetVaReq').hide();
			$('#updateVaReq').hide();
			$(document).off('click', '#addSvaRowEdit').on('click', '#addSvaRowEdit', function (e){
				e.preventDefault();
				var tableId = '#req10Table';
				if (deliv == true){
					FUNCTIONS.addDelivSvaRow(tableId);
				}
				else{
					FUNCTIONS.addSvaRow(tableId);
				}
				$('#resetVaReq').show();
			});	
			$(document).off('keyup', '.vaReqTable input').on('keyup', '.vaReqTable input', function(e){
				e.preventDefault();
				$('#resetVaReq').show();
				$('#updateVaReq').show();
			});	
			$(document).off('click', '#resetVaReq').on('click', '#resetVaReq', function (e){
				e.preventDefault();
				var tabId;
				var url;
				if (demTabId){
					tabId = demTabId;
					url = _getDelivVaTable.replace('123', demTabId);
				}
				else if (swathTabId){
					tabId = swathTabId;
					url = _getDelivVaTable.replace('123', swathTabId);
				}
				else if (classifiedTabId){
					tabId = classifiedTabId;
					url = _getDelivVaTable.replace('123', classifiedTabId);
				}
				else{
                    vaReqId = $(this).parent().attr('id').slice(7)
                    url = _getVaTable.replace('123', vaReqId);
					$.ajax({
						url: url,
						type: "GET",
						success: function(data) {
							$('#vaTable'+vaReqId).html(data['html'])
							FUNCTIONS.setEditVaTableHandlers();
							return;
						}
					});
				}
				$.ajax({
					url: url,
					type: "GET",
					success: function(data) {
						$('#aggregatedWuDelivVaTable').html(data['html'])
						if (demTabId){FUNCTIONS.setEditVaTableHandlers(true, tabId, null, null, buildTabMethod);}
						if (swathTabId){FUNCTIONS.setEditVaTableHandlers(true, null, tabId, null, buildTabMethod);}
						if (classifiedTabId){FUNCTIONS.setEditVaTableHandlers(true, null, null, tabId, buildTabMethod);}
					}
				});	
				
			});	
			$(document).off('click', '#deleteVaReq').on('click', '#deleteVaReq', function (e){
				e.preventDefault();
				var tabId;
				var url;
				var cont = confirm("Confirm Deletion.");
				if (cont){
                    if (demTabId){
                        tabId = demTabId;
                        url = _deleteDelivVaTable.replace('123', demTabId);
                    }
                    else if (swathTabId){
                        tabId = swathTabId;
                        url = _deleteDelivVaTable.replace('123', swathTabId);
                    }
                    else if (classifiedTabId){
                        tabId = classifiedTabId;
                        url = _deleteDelivVaTable.replace('123', classifiedTabId);
                    }
                    else{
                        vaReqId = $(this).parent().attr('id').slice(7)
                        url = _deleteVaTable.replace('123', vaReqId);
                        $.ajax({
                            url: url,
                            type: "POST",
                            success: function(data) {
                                if (data['result'] == 'success'){
									VA_REQUIREMENTS.buildVARequirementsTab();
                                    return;
                                }
                            }
                        });
                    }
                    $.ajax({
                        url: url,
                        type: "POST",
                        success: function(data) {
                            if (data['result'] == 'success'){
                                buildTabMethod();
                                $('#aggregatedWuDelivLink' + tabId).trigger('click');
                            }
                        }
                    });
                }
                else{
                    return false;
                }
			});
			$(document).off('click', '#updateVaReq').on('click', '#updateVaReq', function(e){
				e.preventDefault();
				var tabId;
				var url;
				var jsonDict = FUNCTIONS.packageEditVaForm();
				if ('missingData' in jsonDict){
					alert('Data is missing from the VA Requirements table.  Please complete data entry and resubmit.' );
					return false;
				}
				json = JSON.stringify(jsonDict);
				if (demTabId){
					tabId = demTabId;
					url = _updateDelivVaTable.replace('123', demTabId);
				}
				else if (swathTabId){
					tabId = swathTabId;
					url = _updateDelivVaTable.replace('123', swathTabId);
				}
				else if (classifiedTabId){
					tabId = classifiedTabId;
					url = _updateDelivVaTable.replace('123', classifiedTabId);;
				}
				else{
				    vaReqId = $(this).parent().attr('id').slice(7)
					updateVaUrl = _updateVaTable.replace('123', vaReqId);
					$.ajax({
						url: updateVaUrl,
						data: json,
						type: "POST",
						success: function(data) {
							$('#vaTable'+vaReqId).html(data['html']);
							FUNCTIONS.setEditVaTableHandlers();
							$('#resetVaReq').hide();
							$('#updateVaReq').hide();
						}
					});	
					return true;
				}
				$.ajax({
					url: url,
					data: json,
					type: "POST",
					success: function(data) {
						$('#aggregatedWuDelivVaTable').html(data['html']);
						if (demTabId){FUNCTIONS.setEditVaTableHandlers(true, tabId, null, null, buildTabMethod);}
						if (swathTabId){FUNCTIONS.setEditVaTableHandlers(true, null, tabId, null, buildTabMethod);}
						if (classifiedTabId){FUNCTIONS.setEditVaTableHandlers(true, null, null, tabId, buildTabMethod);}
						$('#resetVaReq').hide();
						$('#updateVaReq').hide();
					}
				});	
			});
		},

		//Adds a row to the classification table, uses the _classificationsAdded variable to track the number of 
		//objects added before sending the update to the server.
		addClassification: function(tableSelector){
		    _classificationsAdded = _classificationsAdded + 1;
			var newClassificationHtml = '';
            newClassificationHtml = '<tr id = "newClassificationRow' + _classificationsAdded + '" class = "newClassification">' +
                '<td></td>' +
                '<td><input type="number" id="newClassificationId' + _classificationsAdded + '" value = ""></td>' +
                '<td><input type="text" id="newClassificationType' + _classificationsAdded + '" value = ""></td></tr>';
            $(tableSelector + ' tbody').append(newClassificationHtml);
		},

		//Handles button clicks for the Classifications table, including adding a new classification row, updating 
		//and resetting the table, and deleting the table. Also handles the key up event within the forms fields in
		//order to show the reset/update buttons.  Manages the check change event handler in order to show the delete
		//clasification button.
        setEditClassificationTableHandlers: function(){
            $('#resetClassifications').hide();
			$('#updateClassifications').hide();
			$('#deleteClassification').hide();
			_classificationsAdded = 0;
			$(document).off('click', '#addClassification').on('click', '#addClassification', function(e){
                e.preventDefault();
                var ctable = '#classificationsTable';
                FUNCTIONS.addClassification(ctable);
                var cHeader = document.getElementById("cHeader");
                cHeader.style.visibility = "visible";
                $('#resetClassifications').show();
            });
            $(document).off('keyup', '.cTable input').on('keyup', '.cTable input', function(e){
				e.preventDefault();
				$('#resetClassifications').show();
				$('#updateClassifications').show();
			});
			$(document).off('change','.classificationCheck').on('change', '.classificationCheck', function(e){
			    e.preventDefault();
			    _classificationChecked = false;
			    $('.classificationCheck').each(function(){
                    if($(this).is(':checked')) {
                        _classificationChecked = true;
                    }
                });
                if(_classificationChecked){
                    $('#deleteClassification').show();
                }
                else{
                    $('#deleteClassification').hide();
                }
			});
			$(document).off('click','#deleteClassification').on('click', '#deleteClassification', function(e){
			    e.preventDefault();
			    var jsonDict = {};
			    var classificationIds = [];
			    var cont = confirm("Confirm Deletion.");
			    if (cont){
                    $('.classificationCheck').each(function(){
                        if($(this).is(':checked')) {
                            var id = $(this).attr('id').substr(14);
                            classificationIds.push(id);
                        }
                    });
                    jsonDict['deleteIds']=classificationIds;
                    json = JSON.stringify(jsonDict);
                    $.ajax({
                        url: _deleteClassifications,
                        data: json,
                        type: "POST",
                        success: function(data) {
                            if (data['result'] == 'success'){
                                $.ajax({
                                url: _getClassificationsTable.replace('123', _reviewId),
                                type: "GET",
                                    success: function(data) {
                                        $('#classifications').html(data['html']);
                                        FUNCTIONS.setEditClassificationTableHandlers();
                                    }
                                });
                            }
                        }
                    });
                }
                else{
                    return false;
                }
			});
			$(document).off('click', '#resetClassifications').on('click', '#resetClassifications', function(e){
                e.preventDefault();
                $.ajax({
					url: _getClassificationsTable.replace('123', _reviewId),
					type: "GET",
					success: function(data) {
						$('#classifications').html(data['html']);
						FUNCTIONS.setEditClassificationTableHandlers();
					}
				});
            });
            $(document).off('click', '#updateClassifications').on('click', '#updateClassifications', function(e){
                e.preventDefault();
                var jsonDict = FUNCTIONS.packageClassificationsForm();
                json = JSON.stringify(jsonDict);
                $.ajax({
					url: _updateClassifications.replace('123', _reviewId),
					data: json,
					type: "POST",
					success: function(data) {
                        if (data['result'] == 'success'){
                            $.ajax({
                            url: _getClassificationsTable.replace('123', _reviewId),
                            type: "GET",
                                success: function(data) {
                                    $('#classifications').html(data['html']);
                                    FUNCTIONS.setEditClassificationTableHandlers();
                                }
                            });
						}
					}
				});
            });
        },

		//Callback wrapper for setErrorButtonHandlers to set the error buttons (add/submit/cancel submit) for each 
		//deliverable panel in a given generic deliverable tab.  
		createAddErrorCallback: function(id, addErrorButtonSelector, redirectUrl){
			return function(){
				var callback = true;
				var addErrorFormSelector = FUNCTIONS.setErrorButtonHandlers(id, callback, addErrorButtonSelector, redirectUrl);
				$(addErrorButtonSelector).hide();
				$(addErrorFormSelector).show();
			};
		},
		
		//Called within the callback wrapper in order to dynamically set add/submit/cancel error button handlers for each
		//deliverable in a generic deliverables panel.
		setErrorButtonHandlers: function(id, callback = false, addErrorButtonSelector = null, redirectUrl = null, dem = false, swath = false, classified = false){
			//If error is added to a generic, is the selector something other than '#addError' + id??
			if (addErrorButtonSelector == null){
				addErrorButtonSelector = '#addError' + id
			};
			var addErrorFormSelector = '#addErrorForm' + id
			var submitErrorBtnSelector = '#submitErrorBtn' + id
			var cancelErrorBtnSelector = '#cancelErrorBtn' + id
			
			if (addErrorButtonSelector == null){
				addErrorButtonSelector = '#addError' + id;
			}
			var urlSubmitError = ''
			var file = null;
			if (callback == false){
				$(document).off('click', addErrorButtonSelector).on('click', addErrorButtonSelector, function(e){
					$(addErrorButtonSelector).hide();
					$(addErrorFormSelector).show();
				});	
			}
			
			$(document).off('change', '.uploadErrImg').on('change', '.uploadErrImg', function(){
				file = this.files[0];		
			});
            var addErrorTypeSelector = '#addSelectErrorType' + id;
			$(document).off('change', addErrorTypeSelector).on('change', addErrorTypeSelector, function(e){
	            e.preventDefault();
                if(dem||swath||classified){
                    var id = addErrorTypeSelector.slice(19)
                    var addErrorSubtypeSelector = '#addSelectErrorSubtype' + id;
                    $(addErrorSubtypeSelector).empty();
                    var jsonDict = {}
                    if (dem){jsonDict['category']='1'}
                    if (swath){jsonDict['category']='2'}
                    if (classified){jsonDict['category']='3'}
                    jsonDict['errorType']=$(addErrorTypeSelector + ' option:selected').val();
                    var json = JSON.stringify(jsonDict);
                    $.ajax({
                        url: _populateErrorSubType,
                        type: "POST",
                        data: json,
                        success: function(data){
                            if(data['result']=='success'){
                                var subTypeString = data['subTypes'].toString();
                                var subTypes = subTypeString.split(',');
                                if(subTypes == '')
                                {
                                    $(addErrorSubtypeSelector).append('<option value = "">N/A</option>')
                                }
                                else
                                {
                                    $.each(subTypes, function(){
                                        val = this;
                                        $(addErrorSubtypeSelector).append('<option value = "' + val + '">' + val + '</option>')
                                    })
                                }
                            }
                        }
                    });
                }
   			});
			
			$(document).off('click', cancelErrorBtnSelector).on('click', cancelErrorBtnSelector, function (e){
				e.preventDefault();	
				$(addErrorFormSelector + ' input[type="text"]').val('');
				$(addErrorFormSelector + ' input[type="number"]').val('');
				var $input = $(".uploadErrImg");
				$input.wrap('<form>').closest('form').get(0).reset();
				$input.unwrap();
				$(addErrorButtonSelector).show();
				$(addErrorFormSelector).hide();		
			});	
			////
			//Error and DEM error VIEWS should be combined so this can be refactored
			////
			$(document).off('click', submitErrorBtnSelector).on('click', submitErrorBtnSelector, function (e){
				e.preventDefault();	
				if (file != null){
					formData = FUNCTIONS.packageErrorForm(id, file);
				}
				else{
					formData = FUNCTIONS.packageErrorForm(id);
				}
				if (callback == false){
					var urlSubmitError;
					if(dem == true){
						urlSubmitError = _addErrorAggregatedWuDeliverable.replace('123', id);
					}
					if(swath == true){
						urlSubmitError = _addErrorAggregatedWuDeliverable.replace('123', id);
					}
					if(classified == true){
						urlSubmitError = _addErrorAggregatedWuDeliverable.replace('123', id);
					}
					$.ajax({
						url: urlSubmitError,
						data: formData,
						processData: false,
						contentType: false,
						type: "POST",
						success: function(data) {
							if (data['success'] == 'True'){
								$('#aggregatedWuDelivLink' + id).trigger('click');
							}
						}
					});	
				}
				else{
					urlSubmitError = _addError.replace('123', id);
					$.ajax({
						url: urlSubmitError,
						data: formData,
						processData: false,
						contentType: false,
						type: "POST",
						success: function(data) {
							//click MAIN CATEGORY tab
							if (data['success'] == 'True'){
								$('#wuTabController li a[href="' + redirectUrl + '"]').click();
								_subtabId = data['delivId'];
								selector = '#collPanel' + _subtabId;
								FUNCTIONS.expandDeliverablePane(selector);
							}
						}
					});
				}
			});

			if (callback == true){
				return addErrorFormSelector;				
			}
		},

        //Handles button clicks for the delete and update buttons within Error Edit Modals. Also handles the change
        //event within the forms fields in order to show and hide the update button as necessary.
        setEditErrorButtonHandlers: function(id){
   			var file = null;
   			$(document).off('change', '.changeErrorImage').on('change', '.changeErrorImage', function(){
				file = this.files[0];
			});
            $(document).off('click', '.deleteErrorButton').on('click', '.deleteErrorButton', function(e){
                e.preventDefault();
                //Pull error number out of button ID
                error_id = $(this).attr('id').substr(11);
                var cont = confirm("Confirm Deletion.");
                if (cont){
                    $.ajax({
                        url: _deleteError.replace('123', error_id),
                        processData: false,
                        contentType: false,
                        type: "POST",
                        success: function(data) {
                            //close modal and reload error table if succeeded
                            if (data['success'] == 'True'){
                                $.ajax({
                                    url: _getErrors.replace('123', id),
                                    type: "GET",
                                    success: function(data) {
                                        var modal = document.getElementById('errorModal'+error_id);
                                        modal.style.display = "none";
                                        $('#errorstable'+id).html(data['html']);
                                        $('.errorTableButtons').hide();
                                        FUNCTIONS.setErrorTableHandlers(id);
                                    }
                                });
                            }
                        }
                    });
                }
                else{
                    return false;
                }
            });
            $(document).off('click', '.updateErrorButton').on('click', '.updateErrorButton', function(e){
                e.preventDefault();
                error_id = $(this).attr('id').substr(11);
                var formData = {}
                if (file != null){
					formData = FUNCTIONS.packageErrorUpdateForm(error_id, file);
				}
				else{
					formData = FUNCTIONS.packageErrorUpdateForm(error_id);
				}
                $.ajax({
                    url: _updateError.replace('123', error_id),
                    data: formData,
                    processData: false,
					contentType: false,
                    type: "POST",
                    success: function(data){
                        if (data['success'] == 'True'){
                            $.ajax({
                                    url: _getError.replace('123', error_id),
                                    type: "GET",
                                    success: function(data) {
                                        $('#errorTable'+error_id).html(data['html']);
                                        FUNCTIONS.updateErrorSubtypes(error_id);
                                        FUNCTIONS.setEditErrorButtonHandlers(id);
                                    }
                            });
                        }
                    }
                });
            });
			$(document).off('click', '.deleteImagesButton').on('click', '.deleteImagesButton', function(e){
                e.preventDefault();
                error_id = $(this).attr('id').substr(12);
                var imageids = [];
                $('.imgInputCheckbox').each(function(){
                    if($(this).prop('checked')&&($(this).attr('name')==error_id))
                    {
                        imageids.push($(this).attr('id').substr(3));
                    }
                });
                formDict = {};
                formDict['ids']=imageids;
                json = JSON.stringify(formDict);
                $.ajax({
                    url: _deleteImages,
                    data: json,
                    type: "POST",
                    success: function(data){
                        if (data['success'] == 'True'){
                            $.ajax({
                                    url: _getError.replace('123', error_id),
                                    type: "GET",
                                    success: function(data) {
                                        $('#errorTable'+error_id).html(data['html']);
                                        FUNCTIONS.setEditErrorButtonHandlers(id);
                                    }
                            });
                        }
                    }
                });
            });
            $(document).on('click', '.modalLink',function(e){
               e.preventDefault();
               var error_id = $(this).attr('id').substr(5);
               FUNCTIONS.updateErrorSubtypes(error_id);
            });
			$(document).off('change', '.errorTypeSelect').on('change', '.errorTypeSelect', function(e){
               e.preventDefault();
               var errorTypeSelector = '#' + $(this).attr('id');
               var error_id = $(this).attr('id').substr(9);
               var errorSubtypeSelector = '#errorSubtype' + error_id;
               $(errorSubtypeSelector).empty();
               var jsonDict = {}
               jsonDict['errorID']=error_id;
               jsonDict['errorType']=$(errorTypeSelector + ' option:selected').val();
               var json = JSON.stringify(jsonDict);
               $.ajax({
                   url: _populateErrorSubType,
                   type: "POST",
                   data: json,
                   success: function(data){
                       if(data['result']=='success'){
                           var subTypeString = data['subTypes'].toString();
                           var subTypes = subTypeString.split(',');
                           if(subTypes == '')
                           {
                               $(errorSubtypeSelector).append('<option value = "">N/A</option>')
                           }
                           else
                           {
                               $.each(subTypes, function(){
                                   val = this;
                                   $(errorSubtypeSelector).append('<option value = "' + val + '">' + val + '</option>')
                               })
                           }

                       }
                   }
               });
   			});
        },

        updateErrorSubtypes: function(id){
           var errorTypeSelector = '#errorType'+id;
           var errorSubtypeSelector = '#errorSubtype' + id;
           $(errorSubtypeSelector).empty();
           var jsonDict = {}
           jsonDict['errorID']=id;
           jsonDict['errorType']=$(errorTypeSelector + ' option:selected').val();
           var json = JSON.stringify(jsonDict);
           $.ajax({
               url: _populateErrorSubType,
               type: "POST",
               data: json,
               success: function(data){
                   if(data['result']=='success'){
                       var subTypeString = data['subTypes'].toString();
                       var subTypes = subTypeString.split(',');
                       if(subTypes == '')
                       {
                           $(errorSubtypeSelector).append('<option value = "">N/A</option>')
                       }
                       else
                       {
                           $.each(subTypes, function(){
                               val = this;
                               if(val == data['selected'])
                               {
                                   $(errorSubtypeSelector).append('<option value = "' + val + '" selected>' + val + '</option>')
                               }
                               else
                               {
                                   $(errorSubtypeSelector).append('<option value = "' + val + '">' + val + '</option>')
                               }
                           })
                       }

                   }
               }
           });
        },

        //Handles button clicks for Errors Tables, including opening edit modals, sorting by collumn header, as well as
        //update and cancel button clicks. Also handles the change event within the forms fields in order to show and hide
        //the update/cancel buttons as necessary.
        setErrorTableHandlers: function(id, category = null){
            var getErrorsUrl = ''
            var updateErrorsUrl = ''
            if(category == null){
                getErrorsUrl = _getErrors.replace('123', id)
                updateErrorsUrl = _updateErrors.replace('123', id)
            }
            else{
                var temp = _getErrorsAgg.replace('123', id)
                getErrorsUrl = temp.replace('456', category)
                var temp = _updateErrorsAgg.replace('123', id)
                updateErrorsUrl = temp.replace('456', category)
            }
            $(document).off('click', '.errorTableHeader').on('click', '.errorTableHeader', function(){
                            var table, rows, switching, i, x, y, shouldSwitch, dir, n, switchcount = 0;
                            table = document.getElementById("errorstable"+id);
                            n = $(this).attr('id');
                            switching = true;
                            dir = "asc";
                            while (switching) {
                                switching = false;
                                rows = table.getElementsByTagName("TR");
                                for (i = 1; i < (rows.length - 1); i++) {
                                    shouldSwitch = false;
                                    x = rows[i].getElementsByTagName("TD")[n];
                                    y = rows[i + 1].getElementsByTagName("TD")[n];
                                    if(n==0){
                                        if (dir == "asc") {
                                            if (parseInt(x.innerHTML) > parseInt(y.innerHTML)) {
                                                shouldSwitch= true;
                                                break;
                                            }
                                        }
                                        else if (dir == "desc") {
                                            if (parseInt(x.innerHTML) < parseInt(y.innerHTML)) {
                                                shouldSwitch= true;
                                                break;
                                            }
                                        }
                                    }
                                    else{
                                        if (dir == "asc") {
                                            if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
                                                shouldSwitch= true;
                                                break;
                                            }
                                        }
                                        else if (dir == "desc") {
                                            if (x.innerHTML.toLowerCase() < y.innerHTML.toLowerCase()) {
                                                shouldSwitch= true;
                                                break;
                                            }
                                        }
                                    }
                                }
                                if (shouldSwitch) {
                                    rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                                    switching = true;
                                    switchcount ++;
                                }
                                else {
                                    if (switchcount == 0 && dir == "asc") {
                                        dir = "desc";
                                        switching = true;
                                    }
                                }
                            }
                        });
            $(document).off('click', '.modalLink').on('click', '.modalLink', function(){
                            modalID = $(this).attr('id').substr(5);
                            modalSelector = 'errorModal' + modalID;
                            var modal = document.getElementById(modalSelector);
                            var span = document.getElementsByClassName("closeModal");
                            modal.style.display = "block";
                            $(document).off('click', '.closeModal').on('click','.closeModal', function(){
                                modal.style.display = "none";
                                $.ajax({
                                    url: getErrorsUrl,
                                    type: "GET",
                                    success: function(data) {
                                        $('#errorstable'+id).html(data['html']);
                                        $('.errorTableButtons').hide();
                                        FUNCTIONS.setErrorTableHandlers(id, category);
                                    }
				                });
                            });
                            window.onclick = function(event){
                                if (event.target == modal){
                                    modal.style.display = "none";
                                    $.ajax({
                                    url: getErrorsUrl,
                                    type: "GET",
                                    success: function(data) {
                                            $('#errorstable'+id).html(data['html']);
                                            $('.errorTableButtons').hide();
                                            FUNCTIONS.setErrorTableHandlers(id, category);
                                        }
				                    });
				                }
                            }
                        });
            $(document).off('change', '.errortable select').on('change', '.errortable select', function(e){
				e.preventDefault();
				$('.errorTableButtons').show();
			});
			$(document).off('click', '#cancelUpdate'+id).on('click', '#cancelUpdate'+id, function(e){
                e.preventDefault();
                $.ajax({
					url: getErrorsUrl,
					type: "GET",
					success: function(data) {
						$('#errorstable'+id).html(data['html']);
						$('.errorTableButtons').hide();
						FUNCTIONS.setErrorTableHandlers(id, category);
					}
				});
            });
            $(document).off('click', '#updateErrors'+id).on('click', '#updateErrors'+id, function(e){
                e.preventDefault();
                var formData = FUNCTIONS.packageErrorTable(id);
                json = JSON.stringify(formData);
                $.ajax({
					url: updateErrorsUrl,
					data: json,
					type: "POST",
					success: function(data) {
					    if (data['result'] == 'success'){
                            $.ajax({
                            url: getErrorsUrl.replace('123', id),
                            type: "GET",
                                success: function(data) {
                                    $('#errorstable'+id).html(data['html']);
                                    $('.errorTableButtons').hide();
                                    FUNCTIONS.setErrorTableHandlers(id, category);
                                }
                            });
					    }
					}
				});
            });
        },

		//Expands a specified (by the selector parameter) generic deliverable pane after some action
		//(add deliverable, add/delete error) is taken on the deliverable.
		expandDeliverablePane: function(selector){
			if ($(selector).length){
				$(selector).parents('.panel').find('.panel-body').show();
				$(selector).removeClass('panel-collapsed');
				$(selector).find('i').removeClass('glyphicon-chevron-down').addClass('glyphicon-chevron-up');	
			}
			else{
				setTimeout(function(){
					FUNCTIONS.expandDeliverablePane(selector);
				}, 50);
			}	
		},	
		
		//Method used to set the _rowsAdded variable (generally to reset it to zero) when a view
		//with a VA table is displayed to the user.
		setRowsAdded: function(numberRows){
			_rowsAdded = numberRows;
		}
		
	};
	
}());