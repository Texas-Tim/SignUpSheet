$(document).ready(function() {

  // Handle form submission.
  $("#yobutton").click(function(e) {
    $('#yobutton').text('Submit');

    //User inputted variables
    var firstName = $("#firstnameid").val(),
        lastName = $("#lastnameid").val(),
        email = $("#emailid").val(),
        emailConfirm = $("#emailidconfirm").val(),
        customer = $("#companyid").val(),
        location = $("#locationid").val(),
        job_function = $("#jobid").val(),
        experience = $('#experienceid').val(),
        virtual = $('#virtualid').val(),
        optTimestamp = undefined,
        utcSeconds = Date.now() / 1000,
        timestamp = new Date(0);


    e.preventDefault();

    if (firstName == "") {
      $('#form-response').html('<div class="mt-3 alert alert-danger" role="alert">Please enter your first name.</div>');
    } else if (lastName == "") {
      $('#form-response').html('<div class="mt-3 alert alert-danger" role="alert">Please enter your last name.</div>');
    } else if (email == "") {
      $('#form-response').html('<div class="mt-3 alert alert-danger" role="alert">Please enter a valid email.</div>');
    } else if (emailConfirm == "") {
      $('#form-response').html('<div class="mt-3 alert alert-danger" role="alert">Please enter a valid email.</div>');
    } else if (emailConfirm != email) {
      $('#form-response').html('<div class="mt-3 alert alert-danger" role="alert">Please check that your email entries are the same!</div>');
    } else if (customer == "") {
      $('#form-response').html('<div class="mt-3 alert alert-danger" role="alert">Please enter your company name.</div>');
    } else if (location == "") {
      $('#form-response').html('<div class="mt-3 alert alert-danger" role="alert">Please enter your location.</div>');
    } else if (job_function == "") {
      $('#form-response').html('<div class="mt-3 alert alert-danger" role="alert">Please enter your job function.</div>');
    } else if (experience == "empty") {
      $('#form-response').html('<div class="mt-3 alert alert-danger" role="alert">Please enter your level of AWS experience.</div>');
    } else if (virtual == "empty") {
      $('#form-response').html('<div class="mt-3 alert alert-danger" role="alert">Please enter if you will be virtual at this event.</div>');
    } else {
      $('#yobutton').prop('disabled', true);
      $('#yobutton').html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>  Saving your preferences</button>');

      timestamp.setUTCSeconds(utcSeconds);

      var data = JSON.stringify({
        'firstName': firstName,
        'lastName': lastName,
        'email': email,
        'customer': customer,
        'location': location,
        'jobFunction': job_function,
        'experience': experience,
        'virtual': virtual,
        'optTimestamp': timestamp.toString()
      });

      $.ajax({
        type: 'POST',
        url: 'https://va4q3t7wo9.execute-api.us-east-1.amazonaws.com/V2/register',
        dataType: "json",
        crossDomain: "true",
        contentType: "application/json; charset=utf-8",
        data: data,
        success: function(res) {
          console.log(res)
          $('#form-response').html('<div class="mt-3 alert alert-success" role="alert"><p>'+res+'</p></div>');
          $('#yobutton').prop('hidden', true);
          $('#yobutton').text('Thanks for submitting!');
        },
        error: function(jqxhr, status, exception) {
          console.log(res)
          $('#form-response').html('<div class="mt-3 alert alert-danger" role="alert">An error occurred. Please try again later.</div>');
          $('#yobutton').prop('disabled', false);
        }
      });
    }
  });
});
