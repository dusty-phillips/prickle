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
    parsable = /^[0-9]+[:.]?[0-9]*$/;
    if (!parsable.test(value)) {
        return null;
    }
    if (/:/.test(value)) {
        // Assume if it's got a colon, it's correct
        return value; 
    }
    if(/\./.test(value)) {
        // Convert Decimal to hours:minutes
        var splitted = value.split('.');
        var hours = splitted[0];
        var minutes = "" + Math.round(parseFloat('0.' + splitted[1]) * 60);
        if (minutes.length == 1) minutes = "0" + minutes;
        return hours + ":" + minutes;
    }
    // All integers. If it's a low number, assume hours else minutes
    value = parseInt(value);
    if (value < 5) {
        return "" + value + ":00";
    }
    if (value > 59) {
        var hours = "" + Math.floor(value / 60);
        var minutes = "" + value % 60;
        if (minutes.length == 1) minutes = "0" + minutes;
        return hours + ":" + minutes;
    }
    minutes = value;
    if (minutes.length == 1) minutes = "0" + minutes; //FIXME: tired of yyp
    return "00:" + minutes;
}
function setup_duration() {
    $('#duration').blur(function() {
        var parsed = parse_duration($('#duration').val());
        if (parsed == null) {
            $('#error').html("Invalid Time");
        }
        else {
            $('#duration').val(parsed);
        }
    });

}
