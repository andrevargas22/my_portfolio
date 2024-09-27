jQuery(document).ready(function($) {
    var timelines = $('.cd-horizontal-timeline'),
        eventsMinDistance = 100; // Adjust this value as needed

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

            // Initial settings
            setEqualPosition(timelineComponents);
            var timelineTotWidth = setTimelineWidth(timelineComponents);
            timeline.addClass('loaded');

            // Select the most recent event by default
            var lastEvent = timelineComponents['timelineEvents'].last();
            lastEvent.addClass('selected');
            updateFilling(lastEvent, timelineComponents['fillingLine'], timelineTotWidth);
            updateVisibleContent(lastEvent, timelineComponents['eventsContent']);

            // Show the content of the most recent event by default
            timelineComponents['eventsContent'].find('li').removeClass('selected');
            timelineComponents['eventsContent'].find('[data-date="' + lastEvent.data('date') + '"]').addClass('selected');

            // Set the maximum height for the content container
            setMaxHeight(timelineComponents['eventsContent']);

            // Detect click on an event - show new content
            timelineComponents['eventsWrapper'].on('click', 'a', function(event) {
                event.preventDefault();
                timelineComponents['timelineEvents'].removeClass('selected');
                $(this).addClass('selected');
                updateFilling($(this), timelineComponents['fillingLine'], timelineTotWidth);
                updateVisibleContent($(this), timelineComponents['eventsContent']);
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

    // Function to set the maximum height of content blocks
    function setMaxHeight(eventsContent) {
        var maxHeight = 0;
        eventsContent.find('li').each(function() {
            var height = $(this).outerHeight();
            if (height > maxHeight) {
                maxHeight = height;
            }
        });
        eventsContent.css('min-height', maxHeight + 'px');
    }

    // Function to position events equally on the timeline
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

    // Function to update visible content
    function updateVisibleContent(event, eventsContent) {
        var eventDate = event.data('date'),
            visibleContent = eventsContent.find('.selected'),
            selectedContent = eventsContent.find('[data-date="' + eventDate + '"]');

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
    }

    // Function to show new content when navigating
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

    // Function to update the filling line
    function updateFilling(selectedEvent, filling, totWidth) {
        var eventStyle = window.getComputedStyle(selectedEvent.get(0), null),
            eventLeft = eventStyle.getPropertyValue("left"),
            eventWidth = eventStyle.getPropertyValue("width");
        eventLeft = Number(eventLeft.replace('px', '')) + Number(eventWidth.replace('px', '')) / 2;
        var scaleValue = eventLeft / totWidth; // Scale value
        setTransformValue(filling.get(0), 'scaleX', scaleValue);
    }

    // Function to set the transform value of an element
    function setTransformValue(element, property, value) {
        element.style["-webkit-transform"] = property + "(" + value + ")";
        element.style["-moz-transform"] = property + "(" + value + ")";
        element.style["-ms-transform"] = property + "(" + value + ")";
        element.style["-o-transform"] = property + "(" + value + ")";
        element.style["transform"] = property + "(" + value + ")";
    }

    // Function to check if an element is in the viewport
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
});
