/*
Split an array into groups of successive items
where a key function returns the same value.
Calls a function for each key and group of items.
 */
function eachGroup(lst, keyFunc, groupFunc) {
    var lastKey;
    var values = [];
    var i, n = lst.length;
    for (i = 0; i < n; i++) {
	var item = lst[i];
	var key = keyFunc(i, item);
	if (values.length > 0 && key != lastKey) {
	    groupFunc(lastKey, values);
	    values = [];
	}
	values.push(item);
	lastKey = key;
    }
    if (values.length > 0) {
	groupFunc(lastKey, values);
    }
};

/*
Split an array into chunks of a given size,
calling a function for each group.
 */
function eachChunk(lst, chunkSize, groupFunc) {
    eachGroup(lst, function(i, item) {
	return Math.floor(i / chunkSize);
    }, function(key, values) {
	groupFunc(values);
    });
};

/*
Fetch list of all photos and add to the page.
 */
function showPhotos() {
    var dir = "photos/";
    var fileExtension = ".jpg";
    var images;
    $.ajax({
        dataType: "json",
        url: dir,
        error: function() {
            console.log("Error fetching directory.");
        },
        success: function(data) {
            console.log("Successfully fetched directory.");
            var photoHTML = "";
	    data = data.filter(function(item) {
		return item.endsWith(".jpg");
	    });
            data.sort();
            data.reverse();
	    var today = (new Date()).toISOString().slice(0,10);
	    eachGroup(data, function(i, item) {
		return item.slice(0, 10); // yyyy-mm-dd
	    }, function(date, datePhotos) {
		photoHTML += "<div id='date-" + date + "'>";
		var dateTitle = (date == today ? "Today" : date);
		photoHTML += "<h2>" + dateTitle + "</h2>";
		eachChunk(datePhotos, 3, function(linePhotos) {
		    photoHTML += "<div class='row'>";
		    for (var i = 0; i < 3; i++) {
			var photo = linePhotos[i];
			photoHTML += "<div class='col-md-4'>";
			if (photo != undefined) {
			    photoHTML += "<img src='" + dir + photo + "'>";
			}
			photoHTML += "</div>";
		    }
		    photoHTML += "</div>";
		});
		photoHTML += "</div>";
	    });
            if (data.length == 0) {
                $("#photos").append("<div class='row'><div class='col-md-12'><h2>No photos.</h2></div></div>");
                $("#download-zip").hide();
            }
            else $("#photos").append(photoHTML);
        }
    });
};

showPhotos();
