/* Copyright 2010 Dusty Phillips

* This file is part of Prickle.

* Prickle is free software: you can redistribute it and/or modify
* it under the terms of the GNU Affero General Public License as
* published by the Free Software Foundation, either version 3 of
* the License, or (at your option) any later version.

* Prickle is distributed in the hope that it will be useful, but
* WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
* GNU Affero General Public License for more details.

* You should have received a copy of the GNU Affero General
* Public License along with Prickle.  If not, see
* <http://www.gnu.org/licenses/>.
*/
function parse_duration(value) {
    /* expect value to be a string of the form
     * (to represent two and a half hours):
     * 2:30 hours and minutes
     * 2.5 float hours 
     * 150 total minutes
     * (to represent 1 hour):
     * 1:00
     * 1
     * 1.0
     * 60
     *
     * Converts the value to formated as hh:mm
     */
    parsable = /^[0-9]*[:.]?[0-9]*$/;
    if (value == '') {
        return '';
    }
    if (!parsable.test(value)) {
        return null;
    }
    if (/:/.test(value)) {
        // Assume if it's got a colon, it's correct
        var splitted = value.split(':');
        var hours = splitted[0];
        if (!hours) {
            hours = "0";
        }
        minutes = splitted[1];
        return hours + ":" + minutes; 
    }
    if(/\./.test(value)) {
        // Convert Decimal to hours:minutes
        var splitted = value.split('.');
        var hours = splitted[0];
        if (!hours) {
            hours = "0";
        }
        var minutes = format_time_part(
                Math.round(parseFloat('0.' + splitted[1]) * 60));
        return hours + ":" + minutes;
    }
    // All integers. If it's a low number, assume hours else minutes
    value = parseInt(value);
    if (value < 7) {
        return "" + value + ":00";
    }
    if (value > 59) {
        var hours = "" + Math.floor(value / 60);
        var minutes = format_time_part(value % 60);
        return hours + ":" + minutes;
    }
    minutes = format_time_part(value);
    return "00:" + minutes;
}
function setup_duration(id) {
    if (!id) {
        id = '#duration';
    }
    $(id).blur(function() {
        var parsed = parse_duration($(id).val());
        if (parsed != null) {
            $(id).val(parsed);
        }
    });
}

function update_totals() {
    var duration = 0.0;
    $('.duration_sum').each(function(i, e) {
        var splitted = $(e).html().split(':');
        duration += parseInt(splitted[0]);
        duration += parseInt(splitted[1]) / 60.0;
    });
    $('tr.total').children(":eq(1)").html(parse_duration(duration.toFixed(2)));

    var fee = 0.0;
    $('.fee_sum').each(function(i, e) {
        fee += parseFloat($(e).html().substring(1));
    });
    $('tr.total').children(":eq(3)").html('$' + fee.toFixed(2));

}

function delete_timesheet(id) {
    $.post('/timesheet/delete/' + id, {}, function(data, textStatus, xhr) {
        $('#timesheet_row_' + id).remove();
        update_totals();
    });
}
edit_row = null;
function edit_timesheet(id) {
    $.get('/timesheet/edit/' + id, {}, function(data, textStatus, xhr) {
        $('#timesheet_row_' + id).before(data);
        edit_row = $('#timesheet_row_' + id).detach();
        setup_duration('#edit_duration');
    });
}
function save_edit_timesheet(id) {
    $.post('/timesheet/save_edit/' + id, {
        'date': $('#edit_date').val(),
        'duration': $('#edit_duration').val(),
        'project': $('#edit_project').val(),
        'type': $('#edit_type').val(),
        'description': $('#edit_description').val(),
    }, function(data, textStatus, xhr) {
        console.log(data);
        $('#edit_timesheet_' + id).replaceWith(data);
        update_totals();
    });
    return false;
}
function cancel_edit_timesheet(id) {
    $('#edit_timesheet_'+id).replaceWith(edit_row);
}

function format_time_part(time_part) {
    time_part = "" + time_part;
    if (time_part.length == 1) {
        time_part = "0" + time_part;
    }
    return time_part;
}
/*
 * It would be nicer, perhaps, if these were incorporated into a jquery plugin.
 */
timer_seconds = 0;
timer_interval_id = null;
function timer_interval() {
    timer_seconds += 1;
    var minutes = Math.floor(timer_seconds / 60);
    var seconds = format_time_part(timer_seconds % 60);
    var hours = format_time_part(Math.floor(minutes / 60));
    minutes = format_time_part(minutes % 60);

    $('#timerlabel').html(hours + ":" + minutes + ":" + seconds);
}
function start_timer() {
    timer_interval_id = window.setInterval(timer_interval, 1000);
    $('#pause_timer').show();
    $('#stop_timer').show();
    $('#start_timer').hide();
}
function stop_timer() {
    var minutes = Math.ceil(timer_seconds / 60);
    minutes = Math.round(minutes / 15) * 15;
    var hours = format_time_part(Math.floor(minutes / 60));
    var minutes = format_time_part("" + minutes % 60);
    $('#duration').val(hours + ":" + minutes);

    if (timer_interval) {
        window.clearInterval(timer_interval_id);
    }
    timer_seconds = 0;
    $('#start_timer').show();
    $('#pause_timer').hide();
    $('#stop_timer').hide();
    window.setTimeout(function() {
        $('#timerlabel').html("00:00:00");
    }, 2000);
    $('#project').focus();
}
function pause_timer() {
    if (timer_interval) {
        window.clearInterval(timer_interval_id);
    }
    $('#start_timer').show();
    $('#pause_timer').hide();
    $('#stop_timer').hide();
}

/*
 * jQuery UI Autocomplete Select First Extension
 *
 * Copyright 2010, Scott González (http://scottgonzalez.com)
 * Dual licensed under the MIT or GPL Version 2 licenses.
 *
 * http://github.com/scottgonzalez/jquery-ui-extensions
 */
(function( $ ) {

$( ".ui-autocomplete-input" ).live( "autocompleteopen", function() {
	var autocomplete = $( this ).data( "autocomplete" ),
		menu = autocomplete.menu;

	if ( !autocomplete.options.selectFirst ) {
		return;
	}

	menu.activate( $.Event({ type: "mouseenter" }), menu.element.children().first() );
});

}( jQuery ));

/* Additional validators */
$.validator.addMethod("duration", function(value, element) {
    return /^[0-9]*[:.]?[0-9]*$/.test(value); 
    }, "Invalid Time");

