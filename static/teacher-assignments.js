// Once DOM loads, get assignment list as JSON object using AJAX.
$(document).ready(function() {
    $.get("/list.json", setCurrentData);
});


// Get and store current data once before sorting and filtering it.
var currentData;

function setCurrentData(data) {
	currentData = data.list;
	filterData(currentData);
}


// Event listener on buttons for sorting and filtering
$( ".btn" ).click(function() {
    var id = $(this).attr('id');
    $(this).addClass('active');
    $(this).siblings().removeClass('active');
    filterData(currentData);
});


// Filter assignments by status.
function filterData(data) {
	
	var filter = $("#filtering .active").attr('id');

	if (filter === 'show-all') {
		sortData(data);
	} else {
		data = data.filter(function(el) { 
			return el.status === filter; })
		sortData(data);
	}
}


// Sort the array of objects from the JSON object by newest or due date.
function sortData(data) {

	var sort = $("#sorting .active").attr('id');

	if (sort === 'newest') {
		data.sort(function (a, b) {
		  if (a.ad < b.ad) {
		    return 1;
		  }
		  if (a.ad > b.ad) {
		    return -1;
		  }
		  // a must be equal to b
		  return 0;
		});
	} else if (sort === 'duedate') {
		data.sort(function (a, b) {
		  if (a.dd < b.dd) {
		    return 1;
		  }
		  if (a.dd > b.dd) {
		    return -1;
		  }
		  // a must be equal to b
		  return 0;
		});
	} 

	generateList(data);
}		


// Generate list of assignments ordered by newest as default
function generateList(assignmentList) {

	console.log(assignmentList);

	$(".assignments").empty();

	if (assignmentList.length === 0) {
			$(".assignments").prepend("<p class='text-center'>No tasks to display.</p>");

	} else {
		for (var assignment in assignmentList) {
		var a = assignmentList[assignment];

		$(".assignments").prepend(

			"<div class='row "+a.status+"' id='"+a.id+"'>\
  			<div class='col-lg-6 col-lg-offset-3 col-md-6 col-md-offset-3 col-sm-8 col-sm-offset-2 col-xs-10 col-xs-offset-1 info'>\
				<h3><a href='/teacher/"+tid+"/assignments/"+a.id+"'>"+a.title+"</a></h3>\
				<p><b>Due date: "+a.due_date+"</b></p>\
				<p>"+a.goal+"</p>\
				<p><i>Assigned to "+a.assigned_to+" on "+a.assigned_on+"</i></p><br>\
			</div></div>"

			);
		}
	}

	$("body").append("</div>");
}