jQuery(document).ready(function($) {
    var timelines = $('.cd-horizontal-timeline'),
        eventsMinDistance = 100; // Adjust this value to set the minimum distance between events

    if (timelines.length > 0) initTimeline(timelines);

    function initTimeline(timelines) {
        timelines.each(function() {
            var timeline = $(this),
                timelineComponents = {};

            // Cache timeline components
            timelineComponents['timelineWrapper'] = timeline.find('.events-wrapper');
            timelineComponents['eventsWrapper'] = timelineComponents['timelineWrapper'].children('.events');
            timelineComponents['fillingLine'] = timelineComponents['eventsWrapper'].children('.filling-line');
            timelineComponents['timelineEvents'] = timelineComponents['eventsWrapper'].find('a');
            timelineComponents['timelineNavigation'] = timeline.find('.cd-timeline-navigation');
            timelineComponents['eventsContent'] = timeline.children('.events-content');

            // Assign equal positions to the single events along the timeline
            setEqualPosition(timelineComponents);
            // Assign a width to the timeline
            var timelineTotWidth = setTimelineWidth(timelineComponents);
            // The timeline has been initialized - show it
            timeline.addClass('loaded');

            // Select the most recent event by default
            var lastEvent = timelineComponents['timelineEvents'].last();
            lastEvent.addClass('selected');
            updateFilling(lastEvent, timelineComponents['fillingLine'], timelineTotWidth);
            updateVisibleContent(lastEvent, timelineComponents['eventsContent']);

            // Show the content of the most recent event by default
            timelineComponents['eventsContent'].find('li').removeClass('selected');
            timelineComponents['eventsContent'].find('[data-date="' + lastEvent.data('date') + '"]').addClass('selected');

            // Detect click on the next arrow
            timelineComponents['timelineNavigation'].on('click', '.next', function(event) {
                event.preventDefault();
                updateSlide(timelineComponents, timelineTotWidth, 'next');
            });
            // Detect click on the prev arrow
            timelineComponents['timelineNavigation'].on('click', '.prev', function(event) {
                event.preventDefault();
                updateSlide(timelineComponents, timelineTotWidth, 'prev');
            });
            // Detect click on a single event - show new event content
            timelineComponents['eventsWrapper'].on('click', 'a', function(event) {
                event.preventDefault();
                timelineComponents['timelineEvents'].removeClass('selected');
                $(this).addClass('selected');
                updateFilling($(this), timelineComponents['fillingLine'], timelineTotWidth);
                updateVisibleContent($(this), timelineComponents['eventsContent']);
            });

            // On swipe, show next/prev event content
            timelineComponents['eventsContent'].on('swipeleft', function() {
                var mq = checkMQ();
                (mq == 'mobile') && showNewContent(timelineComponents, timelineTotWidth, 'next');
            });
            timelineComponents['eventsContent'].on('swiperight', function() {
                var mq = checkMQ();
                (mq == 'mobile') && showNewContent(timelineComponents, timelineTotWidth, 'prev');
            });

            // Keyboard navigation
            $(document).keyup(function(event) {
                if (event.which == '37' && elementInViewport(timeline.get(0))) {
                    showNewContent(timelineComponents, timelineTotWidth, 'prev');
                } else if (event.which == '39' && elementInViewport(timeline.get(0))) {
                    showNewContent(timelineComponents, timelineTotWidth, 'next');
                }
            });
        });
    }

    // Function to set equal positions for the events along the timeline
    function setEqualPosition(timelineComponents) {
        var totalEvents = timelineComponents['timelineEvents'].length;
        var totalWidth = Number(timelineComponents['timelineWrapper'].css('width').replace('px', ''));
        var centerIndex = Math.floor(totalEvents / 2);
        var distance = eventsMinDistance;
        
        timelineComponents['timelineEvents'].each(function(index) {
            var position;
            if (totalEvents % 2 === 0) {
                // Even number of events
                position = (index - centerIndex + 0.5) * distance + totalWidth / 2;
            } else {
                // Odd number of events
                position = (index - centerIndex) * distance + totalWidth / 2;
            }
            $(this).css('left', position + 'px');
        });
    }

    // Function to set the total width of the timeline
    function setTimelineWidth(timelineComponents) {
        var totalEvents = timelineComponents['timelineEvents'].length;
        var totalWidth = Number(timelineComponents['timelineWrapper'].css('width').replace('px', ''));
        var width = (totalEvents - 1) * eventsMinDistance;
        timelineComponents['eventsWrapper'].css('width', width + 'px');
        updateFilling(timelineComponents['timelineEvents'].first(), timelineComponents['fillingLine'], width);
        return width;
    }

    // Function to update the timeline slide (next/prev)
    function updateSlide(timelineComponents, timelineTotWidth, string) {
        var translateValue = getTranslateValue(timelineComponents['eventsWrapper']),
            wrapperWidth = Number(timelineComponents['timelineWrapper'].css('width').replace('px', ''));
        (string == 'next') ?
        translateTimeline(timelineComponents, translateValue - wrapperWidth + eventsMinDistance, wrapperWidth - timelineTotWidth) : translateTimeline(timelineComponents, translateValue + wrapperWidth - eventsMinDistance);
    }

    // Function to show new content on slide or swipe
    function showNewContent(timelineComponents, timelineTotWidth, string) {
        var visibleContent = timelineComponents['eventsContent'].find('.selected'),
            newContent = (string == 'next') ? visibleContent.next() : visibleContent.prev();

        if (newContent.length > 0) {
            var selectedDate = timelineComponents['eventsWrapper'].find('.selected'),
                newEvent = (string == 'next') ? selectedDate.parent('li').next('li').children('a') : selectedDate.parent('li').prev('li').children('a');

            updateFilling(newEvent, timelineComponents['fillingLine'], timelineTotWidth);
            updateVisibleContent(newEvent, timelineComponents['eventsContent']);
            newEvent.addClass('selected');
            selectedDate.removeClass('selected');
        }
    }

    // Function to translate the timeline
    function translateTimeline(timelineComponents, value, totWidth) {
        var eventsWrapper = timelineComponents['eventsWrapper'].get(0);
        value = (value > 0) ? 0 : value;
        value = (!(typeof totWidth === 'undefined') && value < totWidth) ? totWidth : value;
        setTransformValue(eventsWrapper, 'translateX', value + 'px');
        (value == 0) ? timelineComponents['timelineNavigation'].find('.prev').addClass('inactive') : timelineComponents['timelineNavigation'].find('.prev').removeClass('inactive');
        (value == totWidth) ? timelineComponents['timelineNavigation'].find('.next').addClass('inactive') : timelineComponents['timelineNavigation'].find('.next').removeClass('inactive');
    }

    // Function to update the filling line
    function updateFilling(selectedEvent, filling, totWidth) {
        var eventStyle = window.getComputedStyle(selectedEvent.get(0), null),
            eventLeft = eventStyle.getPropertyValue("left"),
            eventWidth = eventStyle.getPropertyValue("width");
        eventLeft = Number(eventLeft.replace('px', '')) + Number(eventWidth.replace('px', '')) / 2;
        var scaleValue = eventLeft / totWidth; // Scale value
        setTransformValue(filling.get(0), 'scaleX', scaleValue);
    }

    // Function to update the visible content
    function updateVisibleContent(event, eventsContent) {
        var eventDate = event.data('date'),
            visibleContent = eventsContent.find('.selected'),
            selectedContent = eventsContent.find('[data-date="' + eventDate + '"]'),
            selectedContentHeight = selectedContent.height();

        if (selectedContent.index() > visibleContent.index()) {
            var classEntering = 'selected enter-right',
                classLeaving = 'leave-left';
        } else {
            var classEntering = 'selected enter-left',
                classLeaving = 'leave-right';
        }

        selectedContent.attr('class', classEntering);
        visibleContent.attr('class', classLeaving).one('webkitAnimationEnd oanimationend msAnimationEnd animationend', function() {
            visibleContent.removeClass('leave-right leave-left');
            selectedContent.removeClass('enter-left enter-right');
        });
        eventsContent.css('height', selectedContentHeight + 'px');
    }

    // Function to get the translate value of the timeline
    function getTranslateValue(timeline) {
        var timelineStyle = window.getComputedStyle(timeline.get(0), null),
            timelineTranslate = timelineStyle.getPropertyValue("-webkit-transform") ||
            timelineStyle.getPropertyValue("-moz-transform") ||
            timelineStyle.getPropertyValue("-ms-transform") ||
            timelineStyle.getPropertyValue("-o-transform") ||
            timelineStyle.getPropertyValue("transform");

        if (timelineTranslate.indexOf('(') >= 0) {
            var timelineTranslate = timelineTranslate.split('(')[1];
            timelineTranslate = timelineTranslate.split(')')[0];
            timelineTranslate = timelineTranslate.split(',');
            var translateValue = timelineTranslate[4];
        } else {
            var translateValue = 0;
        }

        return Number(translateValue);
    }

    // Function to set the transform value of an element
    function setTransformValue(element, property, value) {
        element.style["-webkit-transform"] = property + "(" + value + ")";
        element.style["-moz-transform"] = property + "(" + value + ")";
        element.style["-ms-transform"] = property + "(" + value + ")";
        element.style["-o-transform"] = property + "(" + value + ")";
        element.style["transform"] = property + "(" + value + ")";
    }

    // Function to check if an element is in viewport
    function elementInViewport(el) {
        var top = el.offsetTop;
        var left = el.offsetLeft;
        var width = el.offsetWidth;
        var height = el.offsetHeight;

        while (el.offsetParent) {
            el = el.offsetParent;
            top += el.offsetTop;
            left += el.offsetLeft;
        }

        return (
            top < (window.pageYOffset + window.innerHeight) &&
            left < (window.pageXOffset + window.innerWidth) &&
            (top + height) > window.pageYOffset &&
            (left + width) > window.pageXOffset
        );
    }

    // Function to check the media query
    function checkMQ() {
        return window.getComputedStyle(document.querySelector('.cd-horizontal-timeline'), '::before').getPropertyValue('content').replace(/'/g, "").replace(/"/g, "");
    }
});
