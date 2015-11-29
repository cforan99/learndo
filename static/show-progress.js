// Polling every 5 seconds to see if a student progress has been updated in db.
// If the AJAX call returns new data, then only the row for those students will be regenerated.
(function pollStudentProgress(){
  if (className !== "None") {
	setTimeout(function(){
	  // AJAX request 
	  $.get("/progress/"+taskId+".json", function(data){
	  	
	  	if (data !== "None") {

	  		for (var s in data) {

	  			$("#"+s).empty();
	  			var a = data[s];

	  			console.log(a);

	  			$("#"+s).append("<td class='name'>"+a.first+" "+a.last+"</td>");
				
				if (a.completed !== null) {
					$("#"+s).append("<td class='completed'>Done</td>\
		  				<td class='timestamp'>Completed: "+a.completed+"</td>");
				} else if (a.overdue !== null) {
					$("#"+s).append("<td class='overdue'>Overdue</td>");
					if (a.viewed !== null) {
						$("#"+s).append("<td class='timestamp'>Last Viewed: "+a.viewed+"</td>");
					} else {
						$("#"+s).append("<td class='timestamp'>Not yet viewed</td>");
					}
				} else if (a.viewed !== null) {
					$("#"+s).append("<td class='viewed'>In progress</td>\
		  				<td class='timestamp'>Last Viewed: "+a.viewed+"</td>");
				} else {
					$("#"+s).append("<td class='inactive'>Not viewed</td>\
		  				<td class='timestamp'>Assigned on: "+a.assigned+"</td>");
				}
			}

	  		console.log("Change");

	  	} else {

			console.log("No change");

		}
	  
	    pollStudentProgress();

	  });
	}, 5000);
  }
})();

// Sort table columns in ascending and descending order
// from TinySort's table sorting example at http://tinysort.sjeiti.com/
if (className !== "None") {
	var table = document.getElementById('xtable')
	    ,tableHead = table.querySelector('thead')
	    ,tableHeaders = tableHead.querySelectorAll('th')
	    ,tableBody = table.querySelector('tbody')
	;
	tableHead.addEventListener('click',function(e){
	    var tableHeader = e.target
	        ,textContent = tableHeader.textContent
	        ,tableHeaderIndex,isAscending,order
	    ;
	    if (textContent!=='add row') {
	        while (tableHeader.nodeName!=='TH') {
	            tableHeader = tableHeader.parentNode;
	        }
	        tableHeaderIndex = Array.prototype.indexOf.call(tableHeaders,tableHeader);
	        isAscending = tableHeader.getAttribute('data-order')==='asc';
	        order = isAscending?'desc':'asc';
	        tableHeader.setAttribute('data-order',order);
	        tinysort(
	            tableBody.querySelectorAll('tr')
	            ,{
	                selector:'td:nth-child('+(tableHeaderIndex+1)+')'
	                ,order: order
	            }
	        );
	    }
	});
}
