var build_func = function(){
    var the_img = document.createElement("div");
    the_img.innerHTML = "<img id='popupimg' src='" + exclam_url + "'/>";
    the_img = the_img.firstChild;

    var bodychild =  this.elements.body.firstChild;
    this.elements.body.appendChild(the_img);
    this.elements.body.appendChild(bodychild);
};


if(!alertify.imgAlert){
    //define a new imgAlert based on alert
    alertify.dialog('imgAlert',function factory(){
	return {
	    build: build_func
	};
    },true,'alert');
}


if(!alertify.imgConfirm){
    //define a new imgAlert based on alert
    alertify.dialog('imgConfirm',function factory(){
	return {
	    build: build_func
	};
    },true,'confirm');
}





var readyStateCheckInterval = setInterval(function() {
    if (document.readyState === "complete") {
		call_alerts();
        clearInterval(readyStateCheckInterval);
    }
}, 10);


var call_alerts = function() {
	if(GENERAL_COMMENTS_EMAIL){
		var msg;
		if (GENERAL_COMMENTS_EMAIL == "success"){
			msg = email_sent_text;
		}
		else if (GENERAL_COMMENTS_EMAIL == "error"){
			msg = email_error_text;
		}

		alertify.imgAlert(email_title, msg, function () {})
			.setting({'pinnable': false, 'modal': false, label: email_ok});
	}
};

//sends user to different page on the website (general comments, help, etc.)
var follow_link_with_next = function (link) {
	var currentPage = window.location.href;

	window.location.href = link + "?next=" + encodeURIComponent(currentPage);
};

//sends user to different page on the questionnaire
var follow_link_with_next_questionnaire = function (link) {
	var currentPolicyURL = document.URL.substr(0,document.URL.lastIndexOf('/'));
	window.location.href = currentPolicyURL + link;
};


// // from stackoverflow
// (function($) {
//   /**
//    * polyfill for html5 form attr
//    */

//   // detect if browser supports this
//   var sampleElement = $('[form]').get(0);
//   if (sampleElement && window.HTMLFormElement && sampleElement.form instanceof HTMLFormElement) {
//     // browser supports it, no need to fix
//     return;
//   }

//   /**
//    * Append a field to a form
//    *
//    */
//   $.fn.appendField = function(data) {
//     // for form only
//     if (!this.is('form')) return;

//     // wrap data
//     if (!$.isArray(data) && data.name && data.value) {
//       data = [data];
//     }

//     var $form = this;

//     // attach new params
//     $.each(data, function(i, item) {
//       $('<input/>')
//         .attr('type', 'hidden')
//         .attr('name', item.name)
//         .val(item.value).appendTo($form);
//     });

//     return $form;
//   };

//   /**
//    * Find all input fields with form attribute
//    *
//    */
//   $('form[id]').submit(function(e) {
//     // serialize data
//     var data = $('[form='+ this.id + ']').serializeArray();
//     // append data to form
//     $(this).appendField(data);
//   }).each(function() {
//     var form = this,
//       $fields = $('[form=' + this.id + ']');

//     $fields.filter('button, input').filter('[type=reset],[type=submit]').click(function() {
//       var type = this.type.toLowerCase();
//       if (type === 'reset') {
//         // reset form
//         form.reset();
//         // for elements outside form
//         $fields.each(function() {
//           this.value = this.defaultValue;
//           this.checked = this.defaultChecked;
//         }).filter('select').each(function() {
//           $(this).find('option').each(function() {
//             this.selected = this.defaultSelected;
//           });
//         });
//       } else if (type.match(/^submit|image$/i)) {
//         $(form).appendField({name: this.name, value: this.value}).submit();
//       }
//     });
//   });


// })(jQuery);
