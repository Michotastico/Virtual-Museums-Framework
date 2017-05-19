/**
 * @author [Michel Llorens]{@link http://michotastico.github.io}
 * @version 1.0.0
 * @license GPL
 * @email mllorens@dcc.uchile.cl
 */
function displayPDF(pdfURL, canvasId, pageContainerId,
                    firstButtonId, lastButtonId, prevButtonId, nextButtonId) {
    var canvas = document.getElementById(canvasId);
    var context = canvas.getContext('2d');
    var pageElement = document.getElementById(pageContainerId);

    var reachedEdge = false;
    var touchStart = null;
    var touchDown = false;

    var lastTouchTime = 0;
    pageElement.addEventListener('touchstart', function (e) {
        touchDown = true;

        if (e.timeStamp - lastTouchTime < 500) {
            lastTouchTime = 0;
            toggleZoom();
        } else {
            lastTouchTime = e.timeStamp;
        }
    });

    pageElement.addEventListener('touchmove', function (e) {
        if (pageElement.scrollLeft === 0 ||
            pageElement.scrollLeft === pageElement.scrollWidth - page.clientWidth) {
            reachedEdge = true;
        } else {
            reachedEdge = false;
            touchStart = null;
        }

        if (reachedEdge && touchDown) {
            if (touchStart === null) {
                touchStart = e.changedTouches[0].clientX;
            } else {
                var distance = e.changedTouches[0].clientX - touchStart;
                if (distance < -100) {
                    touchStart = null;
                    reachedEdge = false;
                    touchDown = false;
                    openNextPage();
                } else if (distance > 100) {
                    touchStart = null;
                    reachedEdge = false;
                    touchDown = false;
                    openPrevPage();
                }
            }
        }
    });

    pageElement.addEventListener('touchend', function (e) {
        touchStart = null;
        touchDown = false;
    });

    var pdfFile;
    var currPageNumber = 1;

    var openNextPage = function () {
        var pageNumber = Math.min(pdfFile.numPages, currPageNumber + 1);
        if (pageNumber !== currPageNumber) {
            currPageNumber = pageNumber;
            openPage(pdfFile, currPageNumber);
        }
    };

    document.getElementById(nextButtonId).addEventListener('click', openNextPage);

    var openLastPage = function () {
        currPageNumber = pdfFile.numPages;
        openPage(pdfFile, currPageNumber);
    };

    document.getElementById(lastButtonId).addEventListener('click', openLastPage);

    var openPrevPage = function () {
        var pageNumber = Math.max(1, currPageNumber - 1);
        if (pageNumber !== currPageNumber) {
            currPageNumber = pageNumber;
            openPage(pdfFile, currPageNumber);
        }
    };

    document.getElementById(prevButtonId).addEventListener('click', openPrevPage);

    var openFirstPage = function () {
        currPageNumber = 1;
        openPage(pdfFile, currPageNumber);
    };

    document.getElementById(firstButtonId).addEventListener('click', openFirstPage);

    var zoomed = false;
    var toggleZoom = function () {
        zoomed = !zoomed;
        openPage(pdfFile, currPageNumber);
    };

    var fitScale = 1;
    var openPage = function (pdfFile, pageNumber) {
        var scale = zoomed ? fitScale : 1;

        pdfFile.getPage(pageNumber).then(function (page) {
            viewport = page.getViewport(1);

            if (zoomed) {
                var scale = pageElement.clientWidth / viewport.width;
                viewport = page.getViewport(scale);
            }

            canvas.height = viewport.height;
            canvas.width = viewport.width;

            var renderContext = {
                canvasContext: context,
                viewport: viewport
            };

            page.render(renderContext);
        });

        document.getElementById('page_num').textContent = currPageNumber;
    };

    $(document).keydown(function(e) {
        switch(e.which) {
            case 37: // left
                openPrevPage();
                break;

            case 38: // up
                openFirstPage();
                break;

            case 39: // right
                openNextPage();
                break;

            case 40: // down
                openLastPage();
                break;

            default: return; // exit this handler for other keys
        }
        e.preventDefault(); // prevent the default action (scroll / move caret)
    });

    PDFJS.disableStream = true;
    PDFJS.getDocument(pdfURL).then(function (pdf) {
        pdfFile = pdf;
        document.getElementById('page_count').textContent = pdfFile.numPages;

        openPage(pdf, currPageNumber, 1);
    });
}