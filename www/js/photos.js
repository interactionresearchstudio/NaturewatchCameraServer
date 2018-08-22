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
            var numOfPhotos = 0;
            var photoHTML = "";
            //$(data).find("a:contains(" + fileExtension + ")").each(function() {
            data.sort();
            data.reverse();
            $.each(data, function() {
                console.log(this);
                //var filename = this.href.replace(window.location.host, "").replace("http://", "");
                var filename = this;
                if (filename.endsWith(".jpg")) {
                    numOfPhotos++;
                    if (numOfPhotos % 3 == 0) {
                        console.log("Third photo.");
                        photoHTML += "<div class='col-md-4'><img src='" + dir + filename + "'></div></div>";
                    }
                    else if (numOfPhotos % 3 == 1) {
                        console.log("First photo");
                        photoHTML += "<div class='row'><div class='col-md-4'><img src='" + dir + filename + "'></div>";
                    }
                    else {
                        console.log("Middle photo");
                        photoHTML += "<div class='col-md-4'><img src='" + dir + filename + "'></div>";
                    }
                }
            })
            if (numOfPhotos % 3 != 0) {
                console.log("did not finish on 3.");
                for (var i=0; i<numOfPhotos%3-1; i++) {
                    console.log("adding extra empty div");
                    photoHTML += "<div class='col-md-4'></div>";
                }
                photoHTML += "</div>";
            }
            if (numOfPhotos == 0) {
                $("#photos").append("<div class='row'><div class='col-md-12'><h2>No photos.</h2></div></div>");
                $("#download-zip").hide();
            }
            else $("#photos").append(photoHTML);
        }
    });
};

showPhotos();
