
$().ready(function () {

    win = window.open("", POLICY_NAME, "width=600,height=600,scrollbars=yes");
    if (win==null || win.closed) {
		win = window.open(PDF_URL, POLICY_NAME, "width=600,height=600,scrollbars=yes");
		checkWindow(win);
    }
    else if (win.location.href == "about:blank") {
		win.close();
		win = window.open(PDF_URL, POLICY_NAME, "width=600,height=600,scrollbars=yes");
		checkWindow(win);
    }
    else {
		$("#pdfmessage").hide();
    }

	var qs = $("#theform .q:visible");
	if (qs.length == 0) {
		$("#emptypagemessage").show();
		$("#theform").hide();
		$("#commentform").hide();
	}
    /* close policy pdf if window/tab is closed */
    window.onbeforeunload = function (e) {
		//var e = e || window.event;
		/* need this to differentiate between navigating to a different page and closing browser window/tab */
		if (!clicked_link){
			if (win) {
				win.close();
			}
		}
    };

	$(".q").change(function () {should_display_validation_popup = true;});

    /* intercept link clicks and validate page - if not valid, pop up
     * an alert and don't follow the url until user confirms.
     * Also, if link is going off the questionnaire, close the popup pdf window */
    $("a").click(function(event) {

		var the_a = this;
		var url = event.currentTarget.href;
		//no validation popup on help and GC... issue #91
		if (url.indexOf("/general_comments") > -1 ||
			url.indexOf("/help") > -1) {
			clicked_link = true;
			return true;
		}

		//custom popup on logout
		if (url.indexOf("/logout") > -1){
			alertify
				.confirm(
					logout_title,
					logout_text,
					function (ret) {
						if(ret){
							check_popup(event);
							window.location.href = the_a.href;
						}
					},
					function () {})
				.setting('labels',
						 {
							 ok: logout_continue,
							 cancel: logout_cancel
						 })
				.setting('reverseButtons', true);
		}
		else if (!should_display_validation_popup) {
			check_popup(event);
			return true;
		}


		else if ($("#theform").valid()){
			console.log("form valid");
			check_popup(event);
			return true;
		}
		else {
			alertify
				.confirm(invalid_popup_title,
						 invalid_popup_text,
						 function (ret) {
							 if(ret){
								 check_popup(event);
								 window.location.href = the_a.href;
							 }
						 },
						 function () {})
				.setting('labels',
						 {
							 ok: CONTINUE_LABEL,
							 cancel: CANCEL_LABEL
						 })
				.setting('reverseButtons', true);
		}
		return false;
    });

    /* set up validation for comments (should not obey qselectone rule from above) */
    $("#commentform").validate({
		errorClass: "errClass",
		debug: true
    });

    // $("label.errClass").hide(); // don't show errors on initial page load
    if(TRIED_COMPLETE){
		$("#theform").valid(); // if we're in "already tried to complete" mode, then validate all questions immediately
    }
});

var check_popup = function (event) {
    var url = event.currentTarget.href;
    if (url.indexOf("/general_comments") == -1 &&
		url.indexOf("/help") == -1 &&
		url.indexOf("/policy/") == -1){
		if (win){
			win.close();
		}
    }
    clicked_link = true;
};


var checkWindow = function (win) {
    if (win==null || win.closed) {
		$("#pdfmessage").show("fast");
    }
    else {
		$("#pdfmessage").hide();
    }
};
