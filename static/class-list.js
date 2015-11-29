// clicking on button reveals that form
$( ".form-buttons" ).click(function() {
    var form = $(this).attr('id');
    $('.'+form+'.content').slideToggle();
    $(this).siblings().each( function() { $('.'+this.id+'.content').hide();} );
});

// for AJAX version of flash messages
function showConfirmation(message) {

    $("#flash").empty();
    $("#flash").slideDown();
    $("#flash").html(message);
    setTimeout(function(){
        $("#flash").slideUp();
    }, 5000);
}

// Event listener for delete class buttons
$("button.delete_class").on("click", deleteClass);

// Populates modal confirmation dialog, deletes class from db using AJAX post request, updates the DOM
function deleteClass(evt) {
  evt.preventDefault();
  var classid = $(this).attr('data-classid');
  var formValues = {
    'class_id' : $(this).attr('data-classid')
  };
  $(".modal-body").text('Are you sure you want to delete this class? The students in this class will no longer have access to it.')
  $("#remove").on("click", function() {
    $.post("/delete_class", formValues, showConfirmation);
    $("li#c"+classid).remove();
    });
}

// Event listener for remove student buttons
$("button.remove_student").on("click", removeStudent);

// Populates modal confirmation dialog, removes student from that class in the db using AJAX, updates the DOM
function removeStudent(evt) {
  evt.preventDefault();

  var studentid = $(this).attr('data-studentid');
  var classid = $(this).attr('data-classid');
  var formValues = {
    'class_id' : $(this).attr('data-classid'),
    'user_id' : $(this).attr('data-studentid')
  };

  $(".modal-body").text('Are you sure you want to remove this student from your class? This will not delete the student\'s account.')
  $("#remove").on("click", function() {
    $.post("/remove_student", formValues, showConfirmation);
    console.log(studentid);
    $("ul#class"+classid+" li#s"+studentid).remove();
  });
}


