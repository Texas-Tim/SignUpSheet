$(document).ready(function() {
  $('#languageid').prop('hidden', 'l_flag');
  $('#languagelabel').prop('hidden', 'l_flag');

  // Handle form submission.
  $("#yobutton").click(function(e) {
    $('#yobutton').text('Submit');

    //User inputted variables
    var firstName = $("#firstnameid").val(),
        lastName = $("#lastnameid").val(),
        customer = $("#companyid").val(),
        job_function = $("#jobid").val(),
        language = $("#languageid").val(),
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
    } else if (customer == "") {
      $('#form-response').html('<div class="mt-3 alert alert-danger" role="alert">Please enter your company name.</div>');
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
        'customer': customer,
        'jobFunction': job_function,
        'experience': experience,
        'language': language,
        'virtual': virtual,
        'optTimestamp': timestamp.toString()
      });

      $.ajax({
        type: 'POST',
        //Api_Gateway_Endpoint
        url: 'Api_Gateway_Endpoint',
        dataType: "json",
        crossDomain: "true",
        contentType: "application/json; charset=utf-8",
        data: data,
        success: function(res) {
          console.log(res)

          $("#firstnameid").prop('hidden', true);
          $("#namelabel").prop('hidden', true);
          $("#lastnameid").prop('hidden', true);
          $("#companyid").prop('hidden', true);
          $("#companylabel").prop('hidden', true);
          $("#jobid").prop('hidden', true);
          $("#joblabel").prop('hidden', true);
          $('#experienceid').prop('hidden', true);
          $('#experiencelabel').prop('hidden', true);
          $('#virtualid').prop('hidden', true);
          $('#virtuallabel').prop('hidden', true);
          $('#languageid').prop('hidden', true);
          $('#languagelabel').prop('hidden', true);



          var result = res.result
          var team_num = res.team
          var team_hash = res.hash
          var team_room = res.team_room
          var conference_room = res.main_room
          var attendeeId = res.attendee

          const inv = document.getElementById('openinginvite')
          const end = document.getElementById('submittedtext')


          if(team_room == 'undefined'){

            inv.innerHTML=`<h1>Hello ${firstName}! Thank you for attending todays Game Day! Below, I’ve shared the information for your team:</h1>
            <p style="font-size:15px;">
              <br>
              <br>
              <br>
              Main Event Room: <a href=${conference_room}>Event Room</a>
              <br>
              <br>
              Provided AWS Account: <a href=${team_hash}>Team EE Hash</a>
              <br>
              <br>
              Your Team Number: <strong>${team_num}</strong>
              <br>
              Your Attendee ID: <strong>${attendeeId}</strong>
              <br>
              <br>
              "Please make sure to keep your attendee ID handy as it is unique to you!"
              <br>
              <strong>"WARNING!</strong> Please save this page for your records as all information will be gone once you move away"
            </p>`;

          } else {

            inv.innerHTML=`<h1>Hello ${firstName}! Thank you for attending todays Game Day! Below, I’ve shared the information for your team:</h1>
            <p style="font-size:15px;">
              <br>
              <br>
              <br>
              Main Event Room: <a href=${conference_room}>Event Room</a>
              <br>
              <br>
              Provided AWS Account: <a href=${team_hash}>Team EE Hash</a>
              <br>
              <br>
              Your Team Event Room: <a href=${team_room}>Team Event Room</a>
              <br>
              <br>
              Your Team Number: <strong>${team_num}</strong>
              <br>
              Your Attendee ID: <strong>${attendeeId}</strong>
              <br>
              <br>
              Please make sure to keep your attendee ID handy as it is unique to you!
              <br>
              <br>
              <strong>WARNING!</strong> Please save this page for your records as all information will be gone once you move away
            </p>`;
          }



          end.innerHTML=`<h2>${result}</h2>`
          $('#submittedtext').prop('hidden', false);
          $('#yobutton').prop('hidden', true);

        },
        error: function(jqxhr, status, exception) {

          const div = document.getElementById('submittedtext')
          div.innerHTML=`<div class="alert">
          <h2> An error occurred. Refresh the page to try again.</h2>
          </div>`;

          $("#firstnameid").prop('hidden', true);
          $("#namelabel").prop('hidden', true);
          $("#lastnameid").prop('hidden', true);
          $("#companyid").prop('hidden', true);
          $("#companylabel").prop('hidden', true);
          $("#jobid").prop('hidden', true);
          $("#joblabel").prop('hidden', true);
          $('#experienceid').prop('hidden', true);
          $('#experiencelabel').prop('hidden', true);
          $('#languageid').prop('hidden', true);
          $('#languagelabel').prop('hidden', true);
          $('#virtualid').prop('hidden', true);
          $('#virtuallabel').prop('hidden', true);

          $('#submittedtext').prop('hidden', false);
          $("#openinginvite").prop('hidden', true);

          console.log(jqxhr)
          console.log(status)
          console.log(exception)
          $('#yobutton').prop('disabled', true);
          $('#yobutton').prop('hidden', true);
        }
      });
    }
  });
});
