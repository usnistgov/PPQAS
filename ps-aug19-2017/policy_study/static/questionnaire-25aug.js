// track which option in select one questions is selected -
// in order to be able to get the previously selected option when one changes
var selected = {};

$().ready(function () {

	//try to clear out dumb Firefox autofills
	$('input[type=checkbox]').each(function() {
		var item = $("#" + escape_dots(this.id));
		var attr = item.attr('checked');
		if ( attr != 'checked') {
			item.prop('checked', false);
		}else{
			item[0].checked = true;
		}
	});

	$('input[type=radio]').each(function() {
		var item = $("#" + escape_dots(this.id));
		var attr = item.attr('checked');
		if ( attr != 'checked') {
			item.prop('checked', false);
		}else{
			item[0].checked = true;
		}
	});

    // Uncheckable Radio buttons
    (function( $ ){
		$.fn.uncheckableRadio = function() {

            return this.each(function() {
				$(this).mousedown(function() {
                    $(this).data('wasChecked', this.checked);
				});

				$(this).click(function() {
                    if ($(this).data('wasChecked') && ! $(this).hasClass("hasclones")) {
						this.checked = false;
						$(this).change();
					}
				});
            });

		};
    })( jQuery );
    $('input[type=radio]').uncheckableRadio();


	// tracking previously selected radio button
	$('input[type="radio"]').filter(':checked').each(function() {
		selected[this.name] = this;
	});


    // response posting
    $( ".qresp" ).change(   function (obj) { post_response(obj.target); });
    $( ".cloze" ).change( check_parent_and_post_change );
    $( ".qselectone" ).change(select_one_func); /* was .click */
    $( ".qresplist" ).change(select_multi_func);


    // reset answers to cloze questions inside options which are no longer checked
    $('input[type=radio]').change(cleanup_clozes_inside_options);  // calls valid()
    $('input[type=checkbox]').change(cleanup_clozes_inside_options); // calls valid()

    //have to have this stupid bugfix because the up and down arrows on the html 5 number box don't call valid for some reason
	$('input select').change(function(obj) {$(obj.target).valid();  });

    /* set up validation for main questions */
    $("#theform").validate({
		errorClass: "errClass",
		debug: false
    });

	//updating things
	$( ".q" ).change(update_inserts);


    /* remove default required message, and make all qselectone's required */
    $.validator.addMethod("cRequired", cRequired, "");

    $("label.errClass").hide(); // don't show errors on initial page load

});

var update_inserts = function(eventObject) {
	// var jqinput = $(eventObject.target);
	// console.log("UPDATE INSERTS", eventObject);
	$(".insert").each(function (i, obj) {
		var set_text = function (resp_string){
			$(obj).html(resp_string);
		};
		post_clear_responses(function () {$.post(INSERT_URL, $(obj).attr("insert"), set_text, "text");});
	});
};

var cRequired = function (value, element, params) {
    if(params !== "required"){
		return true;
    }

    var optid = $(element).attr("optid");
    if(optid && optid !== "None"){
		if(!$("#" + escape_dots(optid)).is(":checked")) {
			return true;
		}
    }

    if ( element.nodeName.toLowerCase() === "select" ) {
		// could be an array for select-multiple or a string, both are fine this way
		console.log("It's a select! val=", val);
		var val = $( element ).val();
		return val && val.length > 0;
    }
    if ( this.checkable( element ) ) {
		return this.getLength( value, element ) > 0;
    }
    return $.trim( value ).length > 0;
};


var check_opt = function (el) {
    /* Return true if the element referenced by el's optid is checked, or if the reference is "None" */
    var jqel = $(el);
    if(jqel.attr('optid') && jqel.attr('optid') != "None"){
		if($("#" + escape_dots(jqel.attr('optid'))).is(':checked')){
			return true;
		}
    }
    if(jqel.attr('optid') == "None"){
		return true;
    }
    return false;
};


var gt = function (a, b){ return a > b; };
var lt = function (a, b){ return a < b; };
var gte = function (a, b){ return a >= b; };
var lte = function (a, b){ return a <= b; };
var eq = function (a, b){ return a == b; };

var comparison_validator = function (comp) {
    return function(value, el, params) {
		var target = $("[name='" + escape_dots(clozify_id(params)) + "']");
		var target_val = get_num_from_input_or_checkbox(target);
		var el_val = get_num_from_input_or_checkbox($(el));
		console.log("target_val before ", target_val);
		if(target_val==null || target_val==undefined){
			target_val = QUESTIONS[clozify_id(params)];
			if(target_val instanceof Array){
				target_val = target_val.length;
			}
		}
		console.log("Target", target, "  El", el, " target_val:", target_val, "el_val:", el_val);
		if(!el_val && el_val !== 0){
			//unanswered should validate to true except for the required validator
			return true;
		}
		if(check_opt(el) && target_val){
			return comp(parseInt(el_val), parseInt(target_val));
		}
		else {
			return true;
		}
    };
};

$.validator.addMethod("gt", comparison_validator(gt) , "");
$.validator.addMethod("lt", comparison_validator(lt) , "");
$.validator.addMethod("gte", comparison_validator(gte) , "");
$.validator.addMethod("lte", comparison_validator(lte) , "");
$.validator.addMethod("eq", comparison_validator(eq) , "");


var get_num_from_input_or_checkbox = function (jqelement) {
    var resp;
    if (jqelement.attr("type") == "number"){
		resp = parseInt(jqelement.val());
    }
    else if (jqelement.attr("type") == "checkbox"){
		resp = count_select_multi(jqelement.attr("name"));
    }
    return resp;
};

var count_select_multi = function (name){
    var query = $("[name='" + escape_dots(name) + "']");
    var count = 0;
    query.each(function (idx, el) {
		if ($(el).is(':checked')){
			count += 1;
		}
    });
    return count;
};


var cleanup_clozes_inside_options = function (){
    /* reset values for all clozes whose parent option is not checked */
    $("[optid]").each(function(index, rawelement){
		var element = $(rawelement);
		var optid = element.attr("optid");
		if (optid == "None") return;
		if ($("#" + escape_dots(optid)).is(':checked')){
			return;
		}
		else if($("#" + escape_dots(optid)).length > 0) {
			element.val('');
		}
		element.valid();  // call valid to reset any lingering invalid messages
    });
};


var reload_func = function (a, b, c) {
    clicked_link = true;
	window.setTimeout(function() {
		location.reload();
	}, 60);
};

var post_response = function(obj) {
	console.log("Posting: ", obj);
    /* obj is a raw DOM element */
    resp_obj = { question: obj.name,
				 policy: POLICY_NAME };

    // if the object has no response key, it will act as a delete
    if ($(obj).prop('checked')) {
		resp_obj.response = obj.value;
    }
    else if ($(obj).is(".qresp")) {
		resp_obj.response = obj.value;
    }
    var json_string = JSON.stringify(resp_obj);
	//    console.log(json_string);
    post_clear_responses(function () {$.post(API_URL, json_string, null, "application/json");});
	//    console.log("End Posting.");
};

var get_qid = function (someid) {
    var orig = someid;
    if (typeof someid != "string") {
		someid = someid.id;
		if(someid == null || someid == ""){
			someid = orig.name;
		}
    }
    var ret = qid_from_optid(qid_from_cloze_id(someid));
    return ret;
};

var qid_from_optid = function (qid) {
    // console.log("qid_from_optid " + qid);
    var qid2 = qid.replace(new RegExp("\\.[A-Z]$"), "");
    // console.log("qid " + qid2);
    return qid2;
};

var qid_from_cloze_id = function (cloze_id) {
    return cloze_id.replace(new RegExp(">.*$"), "");
};

var clozify_id = function (tid) {
    /* convert q.2.1.A.b to q.2.1>q.2.1.A.b */
	/* but don't do anything to q.2.1 */
	if(tid.match("^[a-z]\..*\.[a-z]")){
		var m = tid.match("^[a-z]\\.[0-9.]*[0-9]")[0];
		return m + ">" + tid;
	}
	else {
		return tid;
	}

};

var escape_dots = function (astr) {
    // console.log("escape_dots " + astr);
    var newstr = astr.replace(new RegExp("\\.", "g"), "\\.");
    // console.log("escaped dots " + newstr);
    return newstr;
};

var ed = escape_dots; // helpful for debugging in console

var get_opt_id = function (astr) {
    // get rid of qid part if it exists
    var newstr = astr.replace(new RegExp("^.*>"), "");
    // get rid of cloze part of opt id
    newstr = newstr.replace(new RegExp("\\.[a-z]"), "");
    return newstr;
};


var check_parent_of_cloze = function (event){
    if (!event.target.value || (event.target.value == "")){
		return;
    }
    var element = $(event.target);
    var opt_id = element.attr('optid'); //get_opt_id(event.target.name);
    if (!opt_id) return;
    if (opt_id == "None") return;

    var qid = qid_from_cloze_id(event.target.name);
    console.log("check parent of cloze " + opt_id);

    // uncheck whichever option of the parent question is checked
    $("input[name='" + qid + "'][checked='checked'][type='radio']").prop('checked', false);

    // check the opt that is the parent of this cloze
    $("#" + escape_dots(opt_id) ).prop('checked', 'checked');

    //"change" the parent of the cloze to initiate a post
    $("#" + escape_dots(opt_id) ).change();
};

var check_parent_and_post_change = function (event){
    check_parent_of_cloze(event);
    if($(event.target).hasClass("qresplist")){
		select_multi_func(event);
    }
    else {
		post_response(event.target);
    }
};

var select_multi_func = function (e) {
    var input = e.target;
	var jqinput = $(input);

	// check if we are deselecting an option which creates clones
	if(jqinput.attr("clone") && !jqinput.prop("checked")){
		do_alert(clone_warning_title, clone_warning_text, clone_warning_continue, clone_warning_cancel,
				 function(button){
					 finish_select_multi(input);
				 },
				 function(button){
					 jqinput.prop("checked", "checked");
				 });
	}
	else {
		finish_select_multi(input);
	}
};

var finish_select_multi = function(input) {
		clone_list = [];
		//check for clones
		if(check_for_clones(input)){
			//if there are any, display the warning
			do_alert(clone_warning_title, clone_warning_text, clone_warning_continue, clone_warning_cancel,
				 function(button){
				 	really_finish_select_multi(input)
				 },
				 function(button){
					reload_func();
				 });

   }else{
   	really_finish_select_multi(input);
   }
};
var really_finish_select_multi = function(input){
	post_list_response(input);
	display_when_where(input);
	if ($(input).attr("clone")) {
		reload_func();
	}
}

var post_list_response = function(obj) {
    var type;
    if (obj.checked) {
		type = "append";
    }
    else {
		type = "remove";
    }

    var json_string = JSON.stringify({ question: obj.name,
									   response: obj.value,
									   rtype: type,
									   policy: POLICY_NAME});
    //console.log(json_string);
    post_clear_responses(function () {$.post(API_URL, json_string, null, "application/json");});
};


var post_clear_response = function(qid){
	clear_list.push(qid);
}

var post_clear_responses = function(callback) {
	if (clear_list.length != 0){
		var json_string = JSON.stringify({ policy: POLICY_NAME,
										   qids: clear_list});
		console.log("posting to clear responses ", CLEAR_RESPONSES_URL, " ", json_string);
		$.post(CLEAR_RESPONSES_URL, json_string, callback(), "application/json");
		clear_list=[];

	}else{
		callback();
	}
};


var select_one_func = function (e) {
    /* Callback for when a select_one option changes */
    var input = e.target;
	var jqinput = $(input);

	// if this is being deselected and that will kill clones
	if(jqinput.attr("clone") && !jqinput.prop("checked")){
		do_alert(clone_warning_title, clone_warning_text, clone_warning_continue, clone_warning_cancel,
				 function(button){
					 // user confirmed, go ahead with the select_one
					 finish_select_one(input);
					 selected[this.name] = this;
				 },
				 function(button){
					 // user canceled - recheck the option
					 jqinput.prop('checked', "checked");
				 });
	}
	//if something was selected and this is not that something, and that something makes a clone
	else if (this.name in selected && this != selected[this.name] && $(selected[this.name]).attr("clone") ){
		do_alert(clone_warning_title, clone_warning_text, clone_warning_continue, clone_warning_cancel,
				 function(button){
					 // user confirmed, finish the select one process
					 finish_select_one(input);
					 selected[this.name] = this;
				 },
				 function(button){
					 // user canceled - uncheck selected option, and recheck previously selected option
					 jqinput.prop("checked", false);
					 $(selected[input.name]).prop("checked", "checked");
				 });
	}
	else {
		finish_select_one(input);
		selected[this.name] = this;
	}
};

var finish_select_one = function (input){
	clone_list = [];
	var jqinput = $(input);
	//check for clones
	if(check_for_clones(input)){
		//if there are any, display the warning
		do_alert(clone_warning_title, clone_warning_text, clone_warning_continue, clone_warning_cancel,
			 function(button){
				really_finish_select_one(input);
			 },
			 function(button){
				 //bring back the "yes"
					 jqinput.prop("checked", false);
				 reload_func();
			 });
   }else{
   		really_finish_select_one(input);
   }

};

var really_finish_select_one = function (input){
 	// update display_when and display_where questions for each option in this select_one
	$("[name='" + input.name + "']").each(function(num, e) { if(e!=input) {display_when_where(e); }});
	display_when_where(input);
	// post response for the passed in option
	post_response(input);
	if ($(input).hasClass("hasclones")) {

		reload_func();
	}
}

var do_alert = function(title, text, cont, cancel, onok, oncancel){
		alertify.confirm(title, text, onok, oncancel)
		.setting('labels',
				 {ok: cont, cancel: cancel})
		.setting('reverseButtons', true);
};


function check_for_clones(input){
	var retVal = false;
	$("[name='" + input.name + "']").each(function(num, obj) {
		if(!$(obj).attr("displayq") && !$(obj).attr("make_space")) { /* console.log("end display_when"); */ return; }
		var dwhen_qs = $(obj).attr("displayq").split(",");
		var dwhere_qs = $(obj).attr("make_space").split(",");
		var display_qs = dwhen_qs.concat(dwhere_qs);
		for (i = 0; i < display_qs.length; i++) {
			var qid = display_qs[i];

			if ($(qid).hasClass("hasclones") && $(qid).prop('checked')== true) {
				return true;
			}
			$("[name='" + qid + "']").each(function (i, e){
				if ($(e).hasClass("hasclones") && $(e).prop('checked')== true) {
					retVal = true;
				}
			});

			// reset clozes
			$("[name^='" + qid + ">']").each(function (i, e){
			if ($(e).hasClass("hasclones") && $(e).prop('checked')== true) {
					retVal = true;
				}
			});
		}
	});
	return retVal;

}

var clone_list = [];

var clear_list = [];

// unset all answers to hidden question
var reset = function (i, e) {
	if ($(e).hasClass("hasclones") && $(e).prop('checked')== true) {
		clone_list.push(e);
	}
	$(e).prop('checked', false);
	if($(e).is("select")){
		$(e).val("");
		for (var j = 0; j < e.options.length; j++){
			display_when_where(e.options[j]);
		}
	}
	else if($(e).is("input[type='number']")){
		$(e).val("");
	}
	else if($(e).is("input[type='text']")){
		$(e).val("");
	}
	else if($(e).is("input[type='checkbox'] .cloze")){

	}
	else {
		display_when_where(e);
	}
	// update display when and where questions associated with child options
};

var display_when_where = function(obj) {
    /* The given object is an option, for each comma separated
     option in it's displayq parameter display or hide that question
     depending on whether the option is selected or not */
	//    console.log("display_when");
	//    console.log(obj);
    if(!$(obj).attr("displayq") && !$(obj).attr("make_space")) { /* console.log("end display_when"); */ return; }
    var dwhen_qs = $(obj).attr("displayq").split(",");
    var dwhere_qs = $(obj).attr("make_space").split(",");
    var display_qs = dwhen_qs.concat(dwhere_qs.filter(function (item) {
		return dwhen_qs.indexOf(item) < 0;
	}));

    dwhen_qs.concat(dwhere_qs);
	//    console.log(display_qs);
    var qid;
    var i;
    if($(obj).prop('checked')){
		for (i = 0; i < display_qs.length; i++) {
			qid = display_qs[i];
			if (qid != "") {
				//		console.log("showing " + qid);
				$( "#" + escape_dots(qid) ).show("fast");
			}
		}
    }
    else {
		 for (i = 0; i < display_qs.length; i++) {
			qid = display_qs[i];
			if (qid != "") {
				//		console.log("hiding " + qid);
				$( "#" + escape_dots(qid) ).hide("fast");

				// in addition to doing these client side resets, we need clear each response server-side
				post_clear_response(qid);
				$("[name='" + qid + "']").each(reset);
				// reset clozes
				$("[name^='" + qid + ">']").each(reset);

			}
		}

		//for all the clones that we just reset, remove all the clones
		for (i = 0; i < clone_list.length; i++) {
			cloneid = clone_list[i];
			 finish_select_multi(cloneid);
		}
		//    console.log("End display_when");
	};
}