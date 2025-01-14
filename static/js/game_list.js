/**
 * Games Portfolio Gallery Handler
 * 
 * Manages the interactive games portfolio with filtering and image popups.
 * Features:
 * - Isotope grid layout
 * - Category filtering
 * - Image gallery popups
 * - Responsive grid
 * 
 * Dependencies:
 * - jQuery
 * - Isotope
 * - Magnific Popup
 * - ImagesLoaded
 */

$(document).ready(function() {
    // Initialize Magnific Popup
    var popup_btn = $('.popup-btn');
    popup_btn.magnificPopup({
        type: 'image',
        gallery: {
            enabled: true
        }
    });

    // Initialize Isotope after images have loaded
    var $grid = $('.portfolio-item').imagesLoaded(function() {
        $grid.isotope({
            itemSelector: '.item',
            layoutMode: 'fitRows'
        });
    });

    // Filter items on button click
    $('.portfolio-menu ul li').click(function() {
        $('.portfolio-menu ul li').removeClass('active');
        $(this).addClass('active');

        var selector = $(this).attr('data-filter');
        $grid.isotope({
            filter: selector
        });
        return false;
    });
});
