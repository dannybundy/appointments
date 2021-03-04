$(".hide").hide();


$("#phone-info").hover(
	function(){
		$(".info").show();
	},
	function(){
		$(".info").hide();
	}
);


var radioCheckbox = function(checkboxClass) {
	$(document).on("click", checkboxClass, function() {

		$("#customer-form").hide();

		if (checkboxClass!=".appt-checkbox") {
			$("#appt-list").empty();
		}

		if ($(checkboxClass).is(":checked")) {
			$(checkboxClass).prop("checked", false);
			$(this).prop("checked", true);

			if (checkboxClass===".appt-checkbox") {
				$("#customer-form").show();
			}
		}

	});
}

radioCheckbox(".service-checkbox");
radioCheckbox(".connected-checkbox");
radioCheckbox(".appt-checkbox");


// Calendar
function enableDates(date, enabledDays) {
	var m = date.getMonth(), d = date.getDate();

	for (i = 0; i < enabledDays.length; i++) {
		enabledDay = enabledDays[i].getMonth()+1 + "-" + enabledDays[i].getDate();
		if( (m+1 + '-' + d) === enabledDay) {
			return [true];
		}
	}

	return [false];
}


function formatAMPM(date) {
	var hours = date.getHours();
	var minutes = date.getMinutes();
	var ampm = hours >= 12 ? 'PM' : 'AM';
	hours = hours % 12;
	hours = hours ? hours : 12; // the hour '0' should be '12'
	minutes = minutes < 10 ? '0'+minutes : minutes;
	var strTime = hours + ':' + minutes + ' ' + ampm;
	return strTime;
}


var servicePk = null;
var employeePk = null;

$(".service-checkbox").on('click', function() {
	$("#datepicker").hide();

	$(".connected-checkbox").prop("checked", false);
	$(".connected-checkbox").removeClass("chosen-list")
	$("#employee-list").empty();

	if ( $(this).prop("checked") ) {
		$(".service-checkbox").removeClass("chosen-service");
		$(this).addClass("chosen-service");
	}
	else {
		$(".service-checkbox").removeClass("chosen-service");
	}

	servicePk = $(".chosen-service").attr('id');
	if (!servicePk) {
		servicePk = null;
	}

	// Ajax
		ajaxUrl = $("#ajax-get-employees").attr('href')

		$.ajax({
			type:"POST",
			url:ajaxUrl,
			data: {'service_pk':servicePk,},

			success: function(response) {
				employeeArray = response['employeeArray']

				employeeInfoArray = [];
				for (employee of employeeArray) {
					employeeInst = jQuery.parseJSON(employee)[0];
					
					employeePk = employeeInst['pk'];
					employeeName = employeeInst['fields']['name'];
					
					employeeInfoArray.push([employeePk, employeeName]);
				}

				htmlContent = "";
				for (employeeInfo of employeeInfoArray) {
					htmlContent +=
						`
						<div class="col" align="center">
							<input type="checkbox" class="mb-2 connected-checkbox"
								id="${employeeInfo[0]}">
								${employeeInfo[1]}
							</input>
						</div>
						`
				}

				$("#employee-list").append(htmlContent)

			},


			error: function(response) {
				console.log(response['responseJSON']['error'])
			}
		});
	//Ajax

});


enabledDays = [];
$(document).on('click', ".connected-checkbox", function(){

	if ( $(this).prop("checked") ) {
		$("#datepicker").show();
		$(".connected-checkbox").removeClass("chosen-list");
		$(this).addClass("chosen-list");

		servicePk = $(".chosen-service").attr('id');
		if (!servicePk) {
			servicePk = null;
		}

		if ( !$(this).hasClass("all") ) {
			employeePk = $(".chosen-list").attr('id');
		} else {
			employeePk = null;
		}

		// Ajax
			ajaxUrl = $("#ajax-get-dates").attr('href')

			$.ajax({
				type:"POST",
				url:ajaxUrl,
				data: {
					'service_pk':servicePk,
					'employee_pk':employeePk,
				},

				success: function(response) {
					dateArray = response['dateArray']
					enabledDays = [];
					for (date of dateArray) {
						enabledDays.push(new Date(date));
					}
					$("#datepicker").datepicker("refresh");
				},

				error: function(response) {
					console.log(response['responseJSON']['error'])
				}
			});
		// Ajax

	}
	else {
		$("#datepicker").hide();
		$(".connected-checkbox").removeClass("chosen-list");
	}

});


$("#datepicker").datepicker({
	onSelect: function(date, instance) {
		$("#customer-form").hide();
		$("#appt-list").empty();

		// Ajax
			ajaxUrl = $("#ajax-get-appts").attr('href');

			$.ajax({
				type:"POST",
				url:ajaxUrl,
				data:{
					'employee_pk': employeePk,
					'date':date,
				},

				success: function(response) {
					apptListArray = response['apptListArray'];

					apptInfoArray = [];
					for (apptList of apptListArray) {
						tempArray = [];
						for (appt of apptList) {
							apptInst = jQuery.parseJSON(appt)[0];
							apptPk = apptInst['pk'];
							apptDate = new Date(apptInst['fields']['date']);

							apptTime = formatAMPM(apptDate);
							tempArray.push([apptPk, apptTime,]);
						}
						apptInfoArray.push(tempArray);
					}

					htmlArray = [];
					for (apptInfo of apptInfoArray) {
						htmlContent = "";
						for (appt of apptInfo) {
							htmlContent +=
								`
								<div class="center mw-120 border-l-grey border-round">
									<input type="checkbox" name="appt_pk" class="appt-checkbox mb-3"
										id="${appt[0]}" value="${appt[0]}">
									${appt[1]}
									</input>
								</div>
								<br>
								`
						}
						htmlArray.push(htmlContent);
					}


					$("#appt-list").append(
						`
						<div class="row center">

							<div class="col">
								<h4>Morning</h4>
								${htmlArray[0]}
							</div>

							<div class="col">
								<h4>Afternoon</h4>
								${htmlArray[1]}
							</div>

							<div class="col">
								<h4>Evening</h4>
								${htmlArray[2]}
							</div>

						</div>
						`
					);
					
				},
				error: function(response){
					console.log(response["responseJSON"]["error"]);
				}
			});
		// Ajax

	},
	beforeShowDay: function(date) {
		return enableDates(date, enabledDays)
	},

});


$("#appt-form").on("submit", function(e) {
	e.preventDefault();
	if (!$(this).hasClass("form-submitted")) {
		
		apptPk = $("input[name='appt_pk']:checked").val();
		jsonData = JSON.stringify($(this).serializeArray());

		$.ajax({
			type:"POST",
			url:window.location.href,
			data: {
				'service_pk':servicePk,
				'appt_pk': apptPk,
				'json_data':jsonData,
			},

			success: function(response) {
				phonenumberError = response['phonenumberError'];
				url = response['url'];

				if (url) {
					$(this).addClass("form-submitted");
					window.location.replace(url);
				} else {
					$("#phonenumber-error").text(phonenumberError);
				}
			},

			error: function(response) {
				$("#random-error").append(
					`<div class="alert alert-danger alert-dismissible
						fade show text-center" role="alert">
						An error has occured. The page is going to refresh.
					</div>`
					)
				setTimeout(refreshPage, 2000);

			}
		});
		
	}
});