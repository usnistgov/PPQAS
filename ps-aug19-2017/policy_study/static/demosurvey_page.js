
$().ready(function () {

    // $( "input[type='number']" ).keypress( check_parent_of_cloze );
    // $( "input[type='text']" ).keypress( check_parent_of_cloze );
    // $( ".qresp" ).change(function (obj) { post_response(obj.target); });
    // $( ".qresp" ).keyup(function (obj) { post_response(obj.target); });
    // // $("input[type='radio']").change(function () { valid_all("[optid]"); });
    // // $("input[type='checkbox']").change(function () { valid_all("[optid]"); });
    // $( ".cloze" ).change( check_parent_of_cloze );
    // (function( $ ){

    // 	$.fn.uncheckableRadio = function() {

    //         return this.each(function() {
    // 		$(this).mousedown(function() {
    //                 $(this).data('wasChecked', this.checked);
    // 		});

    // 		$(this).click(function() {
    //                 if ($(this).data('wasChecked')) {
    // 			this.checked = false;
    // 			$(this).change();
    // 		    }
    // 		});
    //         });

    // 	};

    // })( jQuery );
    // $('input[type=radio]').uncheckableRadio();
    // $( ".qselectone" ).click(select_one_func);
    // $( ".qresplist" ).change(select_multi_func);

    // $("#theform").validate({
    // 	errorClass: "errClass",
    // 	debug: true
    // });

    // $.validator.addMethod("cRequired", $.validator.methods.required, "");
    // $.validator.addClassRules("qselectone", {cRequired: true});
    // $("label.errClass").hide(); // don't show errors on initial page load
});



var demo_survey_finish = function(url, submit_text) {
    console.log();
    if( !$("#theform").valid() ){
	alertify
	    .imgConfirm(submit_text_title,
			submit_text,
			function(){
			    $.post(COMPLETE_URL, "", function () {window.location.href = url;} );
			},
			function () {})
	    .setting({'pinnable': false, 'modal': false})
	    .setting('labels',
		     {
			 ok: CONTINUE_LABEL,
			 cancel: CANCEL_LABEL
		     })
	    .setting('reverseButtons', true);

    }
    else {
	$.post(COMPLETE_URL, "", function () {window.location.href = url;});
    }

};
