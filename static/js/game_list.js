/**
 * Games Portfolio Gallery Handler
 *
 * Title search plus toggleable platform chips (union among platforms) and a
 * Top 10 chip that intersects with them. Activating Top 10 orders the grid by
 * rank; deactivating it restores the alphabetical order. The cards have a
 * fixed CSS aspect-ratio, so Isotope initializes immediately and lazy-loaded
 * covers never shift the layout.
 *
 * Dependencies: jQuery, Isotope, Magnific Popup
 */

$(document).ready(function () {
    // Initialize Magnific Popup
    $('.popup-btn').magnificPopup({
        type: 'image',
        gallery: { enabled: true },
        image: { titleSrc: 'title' }
    });

    // Combined filter state. `platforms` holds the toggled platform chips
    // (union among themselves); empty means "All". Top 10 is its own dimension
    // and intersects with everything else (Top 10 + SNES = top games ON SNES).
    var state = { search: '', platforms: [], top10: false };

    // Isotope calls this through jQuery's .is(fn), which binds the element to
    // `this` and passes (index, element); in vanilla mode the element is the
    // first argument. Resolve the element from either convention.
    function matchesState(arg) {
        var elem = (this && this.nodeType === 1) ? this : arg;
        var $item = $(elem);
        if (state.top10 && !$item.is('.top-10')) return false;
        if (state.platforms.length && !$item.is(state.platforms.join(','))) return false;
        if (state.search) {
            var title = elem.getAttribute('data-title') || '';
            if (title.indexOf(state.search) === -1) return false;
        }
        return true;
    }

    var $grid = $('.portfolio-item');

    function updateResultCount() {
        var iso = $grid.data('isotope');
        if (!iso) return;
        $('#result-count').text('Showing ' + iso.filteredItems.length + ' of ' + iso.items.length + ' games');
    }

    function applyState() {
        $grid.isotope({
            filter: matchesState,
            // With Top 10 active the grid reads 1..10; otherwise alphabetical
            sortBy: state.top10 ? 'topRank' : 'original-order'
        });
        updateResultCount();
    }

    // Fixed-aspect cards make the layout stable without waiting for images
    $grid.isotope({
        itemSelector: '.item',
        layoutMode: 'fitRows',
        getSortData: {
            topRank: function (itemElem) {
                var n = parseInt(itemElem.getAttribute('data-top-rank'), 10);
                return isNaN(n) ? 999 : n;
            }
        },
        sortAscending: { topRank: true }
    });
    updateResultCount();

    // Filter chips: toggle on/off and accumulate (union among platforms).
    // "All" clears everything, and turning the last filter off falls back to it.
    var $chips = $('.chips .chip');
    var $allChip = $chips.filter('[data-filter="*"]');

    function setChipState($chip, on) {
        $chip.toggleClass('active', on).attr('aria-pressed', on ? 'true' : 'false');
    }

    $chips.on('click', function () {
        var $chip = $(this);
        var selector = $chip.attr('data-filter');

        if (selector === '*') {
            state.platforms = [];
            state.top10 = false;
            $chips.each(function () { setChipState($(this), false); });
        } else if (selector === '.top-10') {
            state.top10 = !state.top10;
            setChipState($chip, state.top10);
        } else {
            var idx = state.platforms.indexOf(selector);
            if (idx === -1) {
                state.platforms.push(selector);
            } else {
                state.platforms.splice(idx, 1);
            }
            setChipState($chip, idx === -1);
        }
        setChipState($allChip, state.platforms.length === 0 && !state.top10);

        applyState();
    });

    // Title search (filters as you type)
    $('#game-search').on('input', function () {
        state.search = $(this).val().trim().toLowerCase();
        applyState();
    });
});
