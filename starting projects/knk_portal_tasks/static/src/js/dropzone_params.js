let dropzoneParams = {
  // camelized version of the `id`
  paramName: "file", // The name that will be used to transfer the file
  maxFilesize: 5, // MB
  url: "/ticket_public/",
  acceptedFiles: "image/*,video/mp4",
  addRemoveLinks: true,
  thumbnailWidth: 240,
  thumbnailHeight: 240,
  autoProcessQueue: false,
  thumbnailMethod: "contain",
  uploadMultiple: true,
  dictDefaultMessage: "Drop images or mp4 videos here to upload",
  // The setting up of the dropzone
  init: function () {
    var myDropzone = this;

    
    document.querySelector("a[id='s_website_form_send']").addEventListener("click", function (e,f) {
        e.preventDefault();
        e.stopPropagation();
        if (myDropzone.getQueuedFiles().length > 0) {                        
            myDropzone.processQueue();  
        } else {                  
          var blob = new Blob();
          blob.upload = { 'chunked': myDropzone.options.chunking };     
          myDropzone.uploadFiles([blob]);
        } 
        //myDropzone.processQueue();

    });

    

    // Listen to the sendingmultiple event. In this case, it's the sendingmultiple event instead
    // of the sending event because uploadMultiple is set to true.
    this.on("sendingmultiple", function (data, xhr, formData) {
        console.log('sending multiple')
        formData.append("subject",      jQuery("#subject").val());
        formData.append("issue_type",   jQuery("#issue_type").val());
        formData.append("description",  jQuery("#description").val());
        formData.append("total_images", jQuery('.dz-image').length);
      // Gets triggered when the form is actually being sent.
      // Hide the success button or the complete form.
    });
    this.on("successmultiple", function (files, response) {
        console.log('success multiple')
        response_json = JSON.parse(response)
        if (response_json.status==true){
          jQuery('#s_website_form_result').html("")
          location.href="/meetings-thank-you"
        }else{
          jQuery('#s_website_form_result').html(response_json.data)
        }
        //debugger;
      // Gets triggered when the files have successfully been sent.
      // Redirect user or notify of success.
    });
    this.on("errormultiple", function (files, response) {
        console.log('error multiple')
      // Gets triggered when there was an error sending the files.
      // Maybe show form again, and notify user of error
    });
  },
  accept: function (file, done) {
    if (file.name == "justinbieber.jpg") {
      done("Naha, you don't.");
    } else {
      done();
    }
  },
};
//Dropzone.options.createTicketForm = dropzoneParams;
let dropzone = new Dropzone("div#attachment-tickets", dropzoneParams);
