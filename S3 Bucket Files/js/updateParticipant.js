$(document).ready(function() {

  // Handle form submission.
  $("#yobutton").click(function(e) {
    $('#yobutton').text('Submit');

    //User inputted variables
    var attendeeID = $("#attendeeid").val(),
        currentTeam = $("#currentteamid").val(),
        newTeam = $("#newteamid").val(),
        optTimestamp = undefined,
        utcSeconds = Date.now() / 1000,
        timestamp = new Date(0);


    e.preventDefault();

    if (attendeeID == "") {
      $('#form-response').html('<div class="mt-3 alert alert-danger" role="alert">Please enter the participants personal ID!</div>');
    } else if (currentTeam == "") {
      $('#form-response').html('<div class="mt-3 alert alert-danger" role="alert">Please enter the participants current team number.</div>');
    } else if (newTeam == "") {
      $('#form-response').html('<div class="mt-3 alert alert-danger" role="alert">Please enter the participants new team number.</div>');
    } else {
      $('#yobutton').html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>  Submitting the team update</button>');

      timestamp.setUTCSeconds(utcSeconds);

      var data = JSON.stringify({
        'id': attendeeID,
        'currentTeam': currentTeam,
        'newTeam': newTeam,
        'optTimestamp': timestamp.toString()
      });

      $.ajax({
        type: 'POST',
        url: 'Api_Gateway_Endpoint',
        dataType: "json",
        crossDomain: "true",
        contentType: "application/json; charset=utf-8",
        data: data,
        success: function(res) {
          // $('#form-response').html('<div class="mt-3 alert alert-success" role="alert"><p>Team update sent successfully. Participant should receive an email with their new team information.</p></div>');
          console.log(res)
          $('#form-response').html('<div class="mt-3 alert alert-success" role="alert"><p>'+res+'</p></div>')
          $('#yobutton').text('Submit next participant');
        },
        error: function(jqxhr, status, exception) {
          console.log(jqxhr)
          console.log(status)
          console.log(exception)
          $('#form-response').html('<div class="mt-3 alert alert-danger" role="alert">An error occurred. Please try again later.</div>');
          $('#yobutton').prop('disabled', false);
        }
      });
    }
  });
});
