jQuery(document).ready(function($) {
    var timelines = $('.cd-horizontal-timeline'),
        eventsMinDistance = 100; // Ajuste este valor conforme necessário

    if (timelines.length > 0) initTimeline(timelines);

    function initTimeline(timelines) {
        timelines.each(function() {
            var timeline = $(this),
                timelineComponents = {};

            // Cache dos componentes da timeline
            timelineComponents['timelineWrapper'] = timeline.find('.events-wrapper');
            timelineComponents['eventsWrapper'] = timelineComponents['timelineWrapper'].children('.events');
            timelineComponents['fillingLine'] = timelineComponents['eventsWrapper'].children('.filling-line');
            timelineComponents['timelineEvents'] = timelineComponents['eventsWrapper'].find('a');
            timelineComponents['timelineNavigation'] = timeline.find('.cd-timeline-navigation');
            timelineComponents['eventsContent'] = timeline.children('.events-content');

            // Configurações iniciais
            setEqualPosition(timelineComponents);
            var timelineTotWidth = setTimelineWidth(timelineComponents);
            timeline.addClass('loaded');

            // Seleciona o evento mais recente por padrão
            var lastEvent = timelineComponents['timelineEvents'].last();
            lastEvent.addClass('selected');
            updateFilling(lastEvent, timelineComponents['fillingLine'], timelineTotWidth);
            updateVisibleContent(lastEvent, timelineComponents['eventsContent']);

            // Mostra o conteúdo do evento mais recente por padrão
            timelineComponents['eventsContent'].find('li').removeClass('selected');
            timelineComponents['eventsContent'].find('[data-date="' + lastEvent.data('date') + '"]').addClass('selected');

            // Define a altura máxima para o contêiner de conteúdo
            setMaxHeight(timelineComponents['eventsContent']);

            // Detecta clique em um evento - mostra o novo conteúdo
            timelineComponents['eventsWrapper'].on('click', 'a', function(event) {
                event.preventDefault();
                timelineComponents['timelineEvents'].removeClass('selected');
                $(this).addClass('selected');
                updateFilling($(this), timelineComponents['fillingLine'], timelineTotWidth);
                updateVisibleContent($(this), timelineComponents['eventsContent']);
            });

            // Navegação por teclado
            $(document).keyup(function(event) {
                if (event.which == '37' && elementInViewport(timeline.get(0))) {
                    showNewContent(timelineComponents, timelineTotWidth, 'prev');
                } else if (event.which == '39' && elementInViewport(timeline.get(0))) {
                    showNewContent(timelineComponents, timelineTotWidth, 'next');
                }
            });
        });
    }

    // Função para definir a altura máxima dos blocos de conteúdo
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

    // Função para posicionar os eventos igualmente na timeline
    function setEqualPosition(timelineComponents) {
        var totalEvents = timelineComponents['timelineEvents'].length;
        var totalWidth = Number(timelineComponents['timelineWrapper'].css('width').replace('px', ''));
        var centerIndex = Math.floor(totalEvents / 2);
        var distance = eventsMinDistance;

        timelineComponents['timelineEvents'].each(function(index) {
            var position;
            if (totalEvents % 2 === 0) {
                // Número par de eventos
                position = (index - centerIndex + 0.5) * distance + totalWidth / 2;
            } else {
                // Número ímpar de eventos
                position = (index - centerIndex) * distance + totalWidth / 2;
            }
            $(this).css('left', position + 'px');
        });
    }

    // Função para definir a largura total da timeline
    function setTimelineWidth(timelineComponents) {
        var totalEvents = timelineComponents['timelineEvents'].length;
        var totalWidth = Number(timelineComponents['timelineWrapper'].css('width').replace('px', ''));
        var width = (totalEvents - 1) * eventsMinDistance;
        timelineComponents['eventsWrapper'].css('width', width + 'px');
        updateFilling(timelineComponents['timelineEvents'].first(), timelineComponents['fillingLine'], width);
        return width;
    }

    // Função para atualizar o conteúdo visível
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

        // Remova ou comente a linha abaixo para não ajustar a altura dinamicamente
        // eventsContent.css('height', selectedContentHeight + 'px');
    }

    // Função para mostrar novo conteúdo ao navegar
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

    // Função para atualizar a linha de preenchimento
    function updateFilling(selectedEvent, filling, totWidth) {
        var eventStyle = window.getComputedStyle(selectedEvent.get(0), null),
            eventLeft = eventStyle.getPropertyValue("left"),
            eventWidth = eventStyle.getPropertyValue("width");
        eventLeft = Number(eventLeft.replace('px', '')) + Number(eventWidth.replace('px', '')) / 2;
        var scaleValue = eventLeft / totWidth; // Valor de escala
        setTransformValue(filling.get(0), 'scaleX', scaleValue);
    }

    // Função para definir o valor de transformação de um elemento
    function setTransformValue(element, property, value) {
        element.style["-webkit-transform"] = property + "(" + value + ")";
        element.style["-moz-transform"] = property + "(" + value + ")";
        element.style["-ms-transform"] = property + "(" + value + ")";
        element.style["-o-transform"] = property + "(" + value + ")";
        element.style["transform"] = property + "(" + value + ")";
    }

    // Função para verificar se um elemento está na viewport
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

    // Função para obter o valor de tradução da timeline
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

    // Função para verificar a mídia query
    function checkMQ() {
        return window.getComputedStyle(document.querySelector('.cd-horizontal-timeline'), '::before').getPropertyValue('content').replace(/'/g, "").replace(/"/g, "");
    }
});
