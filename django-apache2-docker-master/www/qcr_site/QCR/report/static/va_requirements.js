var VA_REQUIREMENTS = VA_REQUIREMENTS || (function(){
	//Object property URLs
	var _review;
	var _vaReqSubtabs;
	var _addVaReqForm;
	var _createVaReq;
	var _vaReqTab;
	var _linkVaWus;
	var _checkRemainingWus;
	var _removeVaReq;
	//Object property vars
	var _reviewId;
	var _tabId;

	return{
		//Initialization function depends on instantiated FUNCTIONS object
		init: function(urls, variables){
			if (FUNCTIONS){
				//Passed-in URLS
				_review = urls['review'];
				_vaReqSubtabs = urls['vaReqSubtabs'];
				_addVaReqForm = urls['addVaReqForm'];
				_createVaReq = urls['createVaReq'];
				_vaReqTab = urls['vaReqTab'];
				_linkVaWus = urls['linkVaWus'];
				_checkRemainingWus = urls['checkRemainingWus'];
				_removeVaReq = urls['removeVaReq'];
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

        packageWuMultiSelect: function(){
            var wus = '';
            $('#wuMultiSelect :selected').each(function(i, selected){
                var selItem = $(selected).val().toString();
                var selId = selItem.substring(selItem.lastIndexOf(" ") + 1, selItem.length);
                wus += selId + ',';
            });
            if (wus.substring(wus.length-1) == ','){
                wus = wus.slice(0,-1);
            }
            json = JSON.stringify(wus)
            return json;
        },

        buildVARequirementsTab(){
            $.ajax({
				url: _vaReqSubtabs.replace('123', _reviewId),
				type: "GET",
				success: function(data) {
					$('#vaReqs').html(data['html']);
					var minVal;
					if (data['minVal']){
						minVal = data['minVal']
					}
					var previousSubtab = '';
					$('#vaRequirementsTabObjects').on("click", "li", function (event) {
					    event.preventDefault();
					    if (previousSubtab !== ''){
					        $(previousSubtab).html('');
					    }
					    var subtabSelector = $(this).find('a').attr('href');
					    previousSubtab = subtabSelector;
					    if(subtabSelector == '#vaRequirementAdd'){
					        $.ajax({
					            url: _addVaReqForm.replace('123', _reviewId),
					            type: "GET",
					            success: function(data){
					                $('#vaRequirementAdd').html(data);
					                $('#createVaReq').on("click", function (event){
					                    event.preventDefault();
					                    var initialWu = $('#wuVaReqSelect :selected').val().toString().substr(10);
					                    $.ajax({
					                        url: _createVaReq.replace('123', initialWu),
					                        type: "POST",
					                        success: function(data){
                                                _tabId = data['tabId'];
                                                VA_REQUIREMENTS.buildVARequirementsTab();
					                        }
					                    });
					                });
					            }
					        });
					    }
					    else{
					        var tabId = subtabSelector.slice(20);
					        $(subtabSelector).addClass('tab_pane active');
					        $.ajax({
					            url: _vaReqTab.replace('123', tabId),
					            type: "GET",
					            success: function(data) {
                                    $(subtabSelector).html(data);
                                    VA_REQUIREMENTS.setUpdateWorkUnitInputHandlers(tabId);
                                    FUNCTIONS.setEditVaTableHandlers();
					            }
					        });
					    }
					});
					if (_tabId && _tabId != ''){
                        $('#vaRequirementsTabObjects li a[href="#vaRequirementUpdate' + _tabId + '"]').click();
                        _tabId = '';
                    }
                    else if(minVal){
                        $('#vaRequirementsTabObjects li a[href="#vaRequirementUpdate' + minVal + '"]').click();
                    }
                    else{
                        $('#vaRequirementsTabObjects li a[href="#vaRequirementAdd"]').click();
                        _tabId = '';
                    }
					$("#vaRequirements").show();
				}
			});
        },

		//'Update' form field/select event handlers (to activate/deactivate update related buttons)
		setUpdateWorkUnitInputHandlers: function(vaReqId){
			$('#updateLinkedWus').hide();
			$(document).off('change', "#wuMultiSelect").on('change', "#wuMultiSelect", function(e){
			    $('#updateLinkedWus').show();
			});
			$(document).off('click', '#updateLinkedWus').on('click', "#updateLinkedWus", function(e){
			    e.preventDefault();
			    json = VA_REQUIREMENTS.packageWuMultiSelect();
			    $.ajax({
			        url: _linkVaWus.replace('123', vaReqId),
			        data: json,
			        type: "POST",
			        success: function(data){
			            if(data['result'] == 'success'){
			                alert('VA REQUIREMENT APPLIED TO WORK UNITS: ' + data['applied'])
			                _tabId = vaReqId;
			                VA_REQUIREMENTS.buildVARequirementsTab();
			            }
			        }
			    });
			});
			$('#wuSameInfo tr').each(function(){
				var workUnitId = $(this).attr('id');
				var removeWuSelector = '#removeWu' + workUnitId;
				$(document).off('click', removeWuSelector).on('click', removeWuSelector, function(e){
				    $.ajax({
                        url: _checkRemainingWus.replace('123', vaReqId),
                        type: "GET",
                        success: function(data) {
                            if (data['warn']=='True'){
                                var cont = confirm("This is the last work unit associated with this VA Requirement. Removing the link will delete the VA Requirement. Continue?");
                                if (cont == true){
                                    $.ajax({
                                        url: _removeVaReq.replace('123', workUnitId),
                                        type: "POST",
                                        success: function(data){
                                            VA_REQUIREMENTS.buildVARequirementsTab();
                                        }
                                    });
                                }
                            }
                            else {
                                $.ajax({
                                    url: _removeVaReq.replace('123', workUnitId),
                                    type: "POST",
                                    success: function(data){
                                        _tabId = vaReqId;
                                        VA_REQUIREMENTS.buildVARequirementsTab();
                                    }
                                });
                            }
                        }
				    });
				});
			})
		},
	};
}());