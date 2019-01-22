var baseURL = "/";

var cameraShutterSpeeds = {
    "1/30": 33333,
    "1/40": 25000,
    "1/50": 20000,
    "1/60": 16666,
    "1/80": 12500,
    "1/100": 10000,
    "1/125": 8000,
    "1/160": 6250,
    "1/200": 5000,
    "1/250": 4000,
    "1/320": 3125,
    "1/400": 2500,
    "1/500": 2000,
    "1/640": 1563,
    "1/800": 1250,
    "1/1000": 1000,
    "1/1250": 800,
    "1/1600": 625,
    "1/2000": 500,
    "1/2500": 400,
    "1/3200": 313,
    "1/4000": 250
};

$(document).ready(function() {

    // Hide controls
    $("#sensitivity-controls").hide();
    $("#settings-controls").hide();
    $("#flip-controls").hide();
    $("#delete-confirm").hide();
    $("#delete-confirm2").hide();
    $("#camera-controls").hide();

    getCameraStatus();
    sendTime(getDateString());

    // Button events
    $(".btn").click(function() {
        var dataDest = $(this).data('dest');
        var thisButton = $(this);
        console.log(dataDest);
        if (dataDest == "sensitivity") {
            $("#sensitivity-controls").slideDown(100);
        }
        else if (dataDest == "less" || dataDest == "more" || dataDest == "default") {
            $.ajax({
                url: baseURL + dataDest,
                error: function() {
                    console.log("Failed to change sensitivity.");
                },
                success: function() {
                    console.log("Changed sensitivity.");
                    $("#sensitivity-controls .active").removeClass("active");
                }
            })
            $("#sensitivity-controls .active").removeClass("active");
        }
        else if (dataDest == "start") {
            $.ajax({
                url: baseURL + dataDest,
                error: function() {
                    console.log("Failed to start capture.");
                },
                success: function() {
                    console.log("Started capture");
                    thisButton.data('dest', "stop");
                    thisButton.addClass("btn-danger");
                    thisButton.removeClass("btn-success");
                    thisButton.text("Stop Image Capture");
                },
                timeout: 1000
            });
        }
        else if (dataDest == "stop") {
            $.ajax({
                url: baseURL + dataDest,
                error: function() {
                    console.log("Failed to start capture.");
                },
                success: function() {
                    console.log("Stopped capture");
                    thisButton.data('dest', "start");
                    thisButton.addClass("btn-success");
                    thisButton.removeClass("btn-danger");
                    thisButton.text("Start Image Capture");
                },
                timeout: 1000
            });
        }
        else if (dataDest == "delete") {
            $("#delete-confirm").slideDown(100);
        }
        else if (dataDest == "delete-yes") {
            $("#delete-confirm2").slideDown(100);
        }
        else if (dataDest == "delete-no") {
            $("#delete-confirm").slideUp(100);
            $("#delete-confirm2").slideUp(100);
        }
        else if (dataDest == "delete-final") {
            $.ajax({
                url: baseURL + dataDest,
                error: function() {
                    console.log("Failed to delete photos.");
                },
                success: function() {
                    console.log("Deleted photos.");
                    location.reload(true);
                },
                timeout:1000
            });
        }
        else if (dataDest == "settings") {
            $("#settings-controls").slideDown(100);
        }
        else if (dataDest == "flip") {
            $("#flip-controls").slideDown(100);
        }
        else if (dataDest == "controls") {
            $("#camera-controls").slideDown(100);
        }
        else if (dataDest == "flip-default") {
            $.ajax({
                url: baseURL + "rotate-180",
                error: function() {
                    console.log("Failed to rotate image.");
                },
                success: function() {
                    console.log("Clicked flip default");
                    $("#flip-180").removeClass("active");
                    $("#flip-default").addClass("active");
                },
                timeout: 1000
            });
        }
        else if (dataDest == "flip-180") {
            $.ajax({
                url: baseURL + "rotate-180",
                error: function() {
                    console.log("Failed to rotate image.");
                },
                success: function() {
                    console.log("Clicked flip 180");
                    $("#flip-180").addClass("active");
                    $("#flip-default").removeClass("active");
                },
                timeout: 1000
            });
        }
        else if (dataDest == "mode-auto") {
            $.ajax({
                url: baseURL + "auto-exposure",
                error: function() {
                    console.log("Failed to rotate image.");
                },
                success: function() {
                    $("#mode-auto").addClass("active");
                    $("#mode-manual").removeClass("active");
                    $("#manual-controls").slideUp(100);
                },
                timeout: 1000
            });
        }
        else if (dataDest == "mode-manual") {
            sendManualSettings();
            $("#mode-auto").removeClass("active");
            $("#mode-manual").addClass("active");
            $("#manual-controls").slideDown(100);
        }
        else if (dataDest == "update-manual") {
            sendManualSettings();
            $("#mode-auto").removeClass("active");
            $("#mode-manual").addClass("active");
        }
        else if (typeof dataDest !== 'undefined') {
            sendGetRequest(dataDest);
        }
    });

    // Range events
    $("input[type='range']").on('input', function () {
        $(this).trigger('change');
        console.log($(this).val());
        if ($(this).attr('id') == "shutter-range") {
            $("label[for='" + $(this).attr('id') + "'] span").html(Object.keys(cameraShutterSpeeds)[$(this).val()]);
        }
    });
});

function getCameraStatus() {
    $.getJSON(baseURL + "get-status", function(data) {
        console.log("Mode: " + data.mode);
        console.log("Sensitivity: " + data.sensitivity);
        console.log("ISO: " + data.iso);
        console.log("Shutter speed: " + data.shutter_speed);
        console.log("Fix camera settings: " + data.fix_camera_settings);

        if (data.mode == 1) {
            btn = $("#start-stop");
            btn.data('dest', "stop");
            btn.addClass("btn-danger");
            btn.removeClass("btn-success");
            btn.text("Stop recording");
        }
        if (data.sensitivity == "less") {
            $("#default").removeClass("active");
            $("#less").addClass("active");
        }
        else if (data.sensitivity == "more") {
            $("#default").removeClass("active");
            $("#more").addClass("active");
        }
        if (data.rotate_camera) {
            $("#flip-default").removeClass("active");
            $("#flip-180").addClass("active");
        }
        else if (!data.rotate_camera) {
            $("#flip-default").addClass("active");
            $("#flip-180").removeClass("active");
        }

        // Manual / Auto settings
        if (!data.fix_camera_settings) {
            $("#manual-controls").hide();
            $("#mode-auto").addClass("active");
        }
        else {
            $("#mode-manual").addClass("active");
            $("#mode-auto").removeClass("active");
            $("#manual-controls").show();
        }

        // Exposure slider settings
        $.each(cameraShutterSpeeds, function (key, value) {
            if(value == data.shutter_speed) {
                console.log("Found shutter speed");
                var index = Object.keys(cameraShutterSpeeds).indexOf(key);
                $("#shutter-range").val(index);
                $("label[for='shutter-range'] span").html(Object.keys(cameraShutterSpeeds)[$("#shutter-range").val()]);
                console.log(key);
            }
        });
    });
}

function sendGetRequest(r) {
    $.get(baseURL + r)
        .done(function() {
            console.log("Sent get request to " + r);
            return true;
        }).fail(function() {
            console.log("Failed to send get request.");
            return false;
        });

}

/*
Retrieves the current date and time and formats it so that it
can be used with the Unix date command.
 */
function getDateString() {
    var date = new Date();
    var hours = date.getHours();
    var hoursString = ('0' + hours).slice(-2);
    var minutes = date.getMinutes();
    var minutesString = ('0' + minutes).slice(-2);
    var year = date.getFullYear();
    var month = date.getMonth() + 1;
    var monthString = ('0' + month).slice(-2);
    var day = date.getDate();
    var dayString = ('0' + day).slice(-2);

    return year.toString() + monthString + dayString + " " + hoursString + ":" + minutesString;
}

function sendTime(t) {
    var postData = JSON.stringify({"timeString": t});
    console.log("Time: " + t);

    $.ajax({
        type: "POST",
        url: baseURL + 'set-time',
        dataType: 'json',
        contentType: 'application/json',
        data: postData,
        success: function() {
            console.log("Sent time to Python server.");
        },
        timeout: 1000
    });
}

function sendManualSettings() {
    var iso = parseInt($("#iso-range").val());
    var shutter = Object.keys(cameraShutterSpeeds)[$("#shutter-range").val()];
    var shutter_us = cameraShutterSpeeds[shutter];
    console.log("Shutter microseconds: " + shutter_us)
    var postData = JSON.stringify({"exposure": shutter_us});

    $.ajax({
        type: "POST",
        url: baseURL + 'fix-exposure',
        dataType: 'json',
        contentType: 'application/json',
        data: postData,
        success: function() {
            console.log("Sent exposure settings to Python server.");
            return true;
        },
        timeout: 1000
    });

}


