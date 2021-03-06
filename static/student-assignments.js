// Get intitial assignment list
$(document).ready(function() {
    $.get("/list.json", setCurrentData);
});

// Get and store current data

var currentData;
var currentDataIds = [];

function listAssignmentIds(dataArray) {
	var idList = [];
	for (assignment in dataArray) {
		idList.push(dataArray[assignment]['id']);
	}
	idList.sort();
	console.log(idList);
	return idList;
} 

function setCurrentData(data) {
	currentData = data.list;
	currentDataIds = listAssignmentIds(currentData)
	sortData(currentData);
}

// Showing the selected sort/filter option
$( ".btn" ).click(function() {
    var id = $(this).attr('id');
    $(this).addClass('active');
    $(this).siblings().removeClass('active');
    filterData(currentData);
});


// Shows assignments with the same status as this id of the button that was clicked.
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


// After filtered, the data can be sorted by newest assignment or due date.
function sortData(data) {

	var sort = $("#sorting .active").attr('id');

	if (sort === 'newest') {
		data.sort(function (a, b) {
		  if (a.ad > b.ad) {
		    return 1;
		  }
		  if (a.ad < b.ad) {
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


// Generate list of assignments after the CurrentData has been filtered and sorted.
function generateList(assignmentList) {

	console.log(assignmentList);

	$(".assignments").empty();

	if (assignmentList.length == 0) {
			$(".assignments").prepend("<p class='text-center'>No tasks to display.</p>");

	} else {
		for (assignment in assignmentList) {
		a = assignmentList[assignment];

		$(".assignments").prepend(

			"<div class='row "+a.status+"' id='"+a.id+"'>\
  			<div class='col-lg-6 col-lg-offset-3 col-md-6 col-md-offset-3 col-sm-8 col-sm-offset-2 col-xs-10 col-xs-offset-1 info'>\
				<h3><a href='/student/"+sid+"/assignments/"+a.id+"'>"+a.title+"</a></h3>\
				<p><b>Due date: "+a.due_date+"</b></p>\
				<p>"+a.goal+"</p>\
				<p><i>Assigned by "+a.assigned_by+" on "+a.assigned_on+"</i></p><br>\
			</div></div>"

			);
		}
	}

	$("body").append("</div>");
}


// Polling to see if a new assignment has been added for this student in the db.
(function pollNewAsssignments(){
  if ($("#newest").hasClass("active")) {
	setTimeout(function(){
	  // AJAX request 
	  $.get("/list.json", function(data){

	  	var newestData = data.list;
	  	newestDataIds = listAssignmentIds(newestData)
	  	
	  	if (newestDataIds.join() != currentDataIds.join()) {
	  		currentData = newestData;
	  		currentDataIds = newestDataIds;
	  		sortData(currentData);
	  		console.log("Change");
	  	} else {
			console.log("No change");
		}
	  
	    pollNewAsssignments();

	  });
	}, 5000);
  }
})();