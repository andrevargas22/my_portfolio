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
            layoutMode: 'fitRows',
            // Robust top rank sort: read numeric attribute or fallback high
            getSortData: {
                topRank: function(itemElem) {
                    var v = itemElem.getAttribute('data-top-rank');
                    var n = parseInt(v, 10);
                    return isNaN(n) ? 999 : n;
                }
            },
            sortAscending: {
                topRank: true
            }
        });
    });

    // Filter items on button click
    $('.portfolio-menu ul li').click(function() {
        $('.portfolio-menu ul li').removeClass('active');
        $(this).addClass('active');

        var selector = $(this).attr('data-filter');
        
        // If filtering by Top 10, force re-sort by rank (ascending 1..10)
        if (selector === '.top-10') {
            $grid.isotope({ filter: selector });
            // trigger separate sort to ensure order update after filter
            $grid.isotope({ sortBy: 'topRank' });
        } else {
            // revert to original order for other filters
            $grid.isotope({ filter: selector, sortBy: 'original-order' });
        }
        
        return false;
    });
});
