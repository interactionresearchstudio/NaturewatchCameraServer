let dir = "photos/";
let fileExtension = ".jpg";
let pageSize = 9;
let pageNumber = 1;
let numPages = 0;
let pageWindow = 5;

let loadFunction = function () {
    $("#photos").html('');
    let url = dir + "?page=" + pageNumber + "&size=" + pageSize;

    function activateNextAndPrev() {
        if (1 === pageNumber) {
            console.log('Disabling prev and enabling next')
            $('.move-backwards').addClass('disabled');
            $('.move-forwards').removeClass('disabled');
        } else if (numPages === pageNumber) {
            console.log('Disabling next and enabling prev')
            $('.move-backwards').removeClass('disabled');
            $('.move-forwards').addClass('disabled');
        } else {
            console.log('Enabling next and prev')
            $('.move-backwards').removeClass('disabled');
            $('.move-forwards').removeClass('disabled');
        }
    }

    function buildPaginationLinks(response) {
        $('[data-toggle="tooltip"]').tooltip('hide');
        let $navigation = $('#navigation');
        $navigation.show();
        $('#page-nav li').each(function (idx, obj) {
            if (!$(obj).hasClass('move-backwards') && !$(obj).hasClass('move-forwards')) {
                $(obj).remove();
            }
        });

        // Total number of pages needed to show all photos
        numPages = Math.ceil(response.total / pageSize);

        // If no pages or single page, hide and don't do navigation
        if (numPages < 2) {
            $navigation.hide();
            return;
        }

        // The number of extra link slots to each side of the selected page
        let side = Math.floor(pageWindow / 2);

        // Where it would like to be
        let leftSidePointer = pageNumber - side;

        // If less than 1, we need to fix it to the first page
        let startNumber = (leftSidePointer < 1) ? 1 : leftSidePointer;

        // Carry over the missing pages from the left side and add them to the right
        let addToRightSide = (leftSidePointer < 1) ? leftSidePointer - 1 : 0;

        // If we are at the end always have a whole window of pages
        if (startNumber > pageWindow && startNumber > numPages - pageWindow) {
            startNumber = numPages - pageWindow + 1;
        }

        // numPages if pageNumber plus the side is higher, otherwise the page number plus side and any extra from the left
        let endNumber = (((pageNumber + side) - numPages > 0) ? numPages : pageNumber + side + (-addToRightSide));

        for (let i = startNumber; i <= endNumber; ++i) {
            let $link = $(
                '<li class="page-item page-number"><a class="page-link" href="javascript:void(0);">' + i + '</a></li>'
            );
            if (i === pageNumber) {
                $link.addClass('active');
            }
            $link.insertBefore(
                $('#next')
            );
        }
    }

    function addClickHandlers() {
        $('.page-number').on('click', function (event) {
            let value = $(this).children('a').text();
            if (value > 0 && value <= numPages) {
                pageNumber = parseInt(value);
                console.log('page number changed to ' + value);
                loadFunction();
                event.stopPropagation();
                return false;
            }
        });
    }

    function buildPhotoHtml(response) {
        let numOfPhotos = 0;
        let photoHTML = "";
        let data = response.files;
        data.sort();
        data.reverse();
        $.each(data, function () {
            console.log(this);
            //var filename = this.href.replace(window.location.host, "").replace("http://", "");
            var filename = this;
            if (filename.endsWith(fileExtension)) {
                numOfPhotos++;
                if (numOfPhotos % 3 === 0) {
                    console.log("Third photo.");
                    photoHTML += "<div class='col-md-4'><img src='" + dir + filename + "'></div></div>";
                } else if (numOfPhotos % 3 === 1) {
                    console.log("First photo");
                    photoHTML += "<div class='row'><div class='col-md-4'><img src='" + dir + filename + "'></div>";
                } else {
                    console.log("Middle photo");
                    photoHTML += "<div class='col-md-4'><img src='" + dir + filename + "'></div>";
                }
            }
        });
        if (numOfPhotos % 3 !== 0) {
            console.log("did not finish on 3.");
            for (var i = 0; i < numOfPhotos % 3 - 1; i++) {
                console.log("adding extra empty div");
                photoHTML += "<div class='col-md-4'></div>";
            }
            photoHTML += "</div>";
        }
        if (numOfPhotos === 0) {
            $("#photos").append("<div class='row'><div class='col-md-12'><h2>No photos.</h2></div></div>");
            $("#download-zip").hide();
            $("#navigation").hide();
        } else {
            $("#photos").append(photoHTML);
            $("#navigation").show();
        }
    }

    $('.page-size').each(function (idx, obj) {
        let value = $(obj).children('a').text();
        if (value == pageSize) {
            $(obj).addClass('active');
        } else {
            $(obj).removeClass('active');
        }
    });

    $.ajax({
        dataType: "json",
        url: url,
        error: function () {
            console.log("Error fetching directory.");
        },
        success: function (response) {
            console.log("Successfully fetched url: " + url);
            buildPaginationLinks(response);
            addClickHandlers();
            activateNextAndPrev();
            buildPhotoHtml(response);
        }
    });
};
loadFunction();

$('.move-backwards').on('click', function (event) {
    let amount = $(this).data('amount');
    if ('all' === amount) {
        console.log('Setting to first page');
        pageNumber = 1;
    } else if (10 === amount && pageNumber > 2) {
        console.log('Go back 10 pages');
        pageNumber -= 10;
        if (pageNumber < 1) {
            pageNumber = 1;
        }
    } else if (1 === amount && pageNumber > 2) {
        console.log('Go back 1 page');
        --pageNumber;
    }
    console.log('page down', pageNumber);
    loadFunction();
});

$('.move-forwards').on('click', function (event) {
    let amount = $(this).data('amount');
    if ('all' === amount) {
        console.log('Setting to last page');
        pageNumber = numPages;
    } else if (10 === amount && pageNumber < numPages) {
        console.log('Go forward 10 pages');
        pageNumber += 10;
        if (pageNumber > numPages) {
            pageNumber = numPages;
        }
    } else if (1 === amount && pageNumber < numPages) {
        console.log('Go forward 1 page');
        ++pageNumber;
    }
    console.log('page up', pageNumber);
    loadFunction();
});

$('.page-size').on('click', function (event) {
    let value = $(this).children('a').text();
    console.log('page size changed to ' + value);
    pageSize = value;
    pageNumber = 1;
    loadFunction();
});

