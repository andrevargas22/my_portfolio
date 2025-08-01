/**
 * Interactive Travel Map using Mapbox GL JS
 * 
 * This script creates an interactive world map showing visited countries
 * with photo markers and country highlighting. Features:
 * - Country highlighting with different colors
 * - Photo markers with popup galleries
 * - Smooth animations and modern styling
 * - Responsive design
 * 
 * Dependencies:
 * - Mapbox GL JS
 */

// Mapbox access token
// Validate token before use
if (!window.mapboxToken || window.mapboxToken.trim() === '') {
    console.error('Mapbox token is missing or empty. Map cannot be initialized.');
    document.addEventListener('DOMContentLoaded', () => {
        const mapContainer = document.getElementById('map');
        if (mapContainer) {
            mapContainer.innerHTML = `
                <div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #721c24; background-color: #f8d7da; border: 1px solid #f5c6cb; border-radius: 0.25rem; padding: 0.75rem 1.25rem;">
                    <strong>Error:</strong>&nbsp;Map cannot be loaded. Mapbox token is missing.
                </div>
            `;
        }
    });
} else {
    mapboxgl.accessToken = window.mapboxToken;
}

// Visited places data
const visitedPlaces = [
    // [lng, lat] format
    {
        country: "Argentina",
        coordinates: [-68.3029, -54.8019],
        photo: "ushuaia.jpg",
        location: "Ushuaia",
        color: "#28a745"
    },
    {
        country: "Austria",
        coordinates: [16.3738, 48.2082],
        photo: "vienna.jpg",
        location: "Vienna",
        color: "#28a745"
    },
    {
        country: "Belgium",
        coordinates: [4.3517, 50.8503],
        photo: "brussels.jpg",
        location: "Brussels",
        color: "#28a745"
    },
    {
        country: "Brazil",
        coordinates: [-46.1594, -22.7536],
        photo: "camanducaia.jpg",
        location: "Camanducaia",
        color: "#dc3545"
    },
    {
        country: "Brazil",
        coordinates: [-40.5088, -2.7845],
        photo: "jericoacoara.jpg",
        location: "Jericoacoara",
        color: "#dc3545"
    },
    {
        country: "Brazil",
        coordinates: [-38.5014, -12.9714],
        photo: "salvador.jpg",
        location: "Salvador",
        color: "#dc3545"
    },
    {
        country: "Brazil",
        coordinates: [-40.3128, -20.3155],
        photo: "vitoria.jpeg",
        location: "Vitória",
        color: "#dc3545"
    },
    {
        country: "Czechia",
        coordinates: [14.4378, 50.0755],
        photo: "prague.jpg",
        location: "Prague",
        color: "#28a745"
    },
    {
        country: "France",
        coordinates: [2.3522, 48.8566],
        photo: "paris.jpg",
        location: "Paris",
        color: "#28a745"
    },
    {
        country: "Germany",
        coordinates: [10.7019, 47.5696],
        photo: "fussen.jpg",
        location: "Füssen",
        color: "#28a745"
    },
    {
        country: "Germany",
        coordinates: [13.4050, 52.5200],
        photo: "berlin.jpg",
        location: "Berlin",
        color: "#28a745"
    },
    {
        country: "Hungary",
        coordinates: [19.0402, 47.4979],
        photo: "budapest.jpg",
        location: "Budapest",
        color: "#28a745"
    },
    {
        country: "Italy",
        coordinates: [11.2558, 43.7696],
        photo: "florence.jpg",
        location: "Florence",
        color: "#28a745"
    },
    {
        country: "Italy",
        coordinates: [12.4964, 41.9028],
        photo: "rome.jpg",
        location: "Rome",
        color: "#28a745"
    },
    {
        country: "Italy",
        coordinates: [11.3308, 43.3188],
        photo: "siena.jpg",
        location: "Siena",
        color: "#28a745"
    },
    {
        country: "Ireland",
        coordinates: [-6.2603, 53.3498],
        photo: "dublin.jpg",
        location: "Dublin",
        color: "#28a745"
    },
    {
        country: "Morocco",
        coordinates: [-4.0125, 31.1012],
        photo: "merzouga.jpg",
        location: "Merzouga",
        color: "#28a745"
    },
    {
        country: "Morocco",
        coordinates: [-7.9811, 31.6295],
        photo: "marrakech.jpg",
        location: "Marrakech",
        color: "#28a745"
    },
    {
        country: "Netherlands",
        coordinates: [4.9041, 52.3676],
        photo: "amsterdam.jpg",
        location: "Amsterdam",
        color: "#28a745"
    },
    {
        country: "Norway",
        coordinates: [10.7522, 59.9139],
        photo: "oslo.jpg",
        location: "Oslo",
        color: "#28a745"
    },
    {
        country: "Poland",
        coordinates: [19.2044, 50.0413],
        photo: "oswiecim.jpg",
        location: "Oświęcim",
        color: "#28a745"
    },
    {
        country: "Poland",
        coordinates: [19.9496, 49.2992],
        photo: "zakopane.jpg",
        location: "Zakopane",
        color: "#28a745"
    },
    {
        country: "Portugal",
        coordinates: [-9.1393, 38.7223],
        photo: "lisbon.jpg",
        location: "Lisbon",
        color: "#28a745"
    },
    {
        country: "Slovakia",
        coordinates: [17.1077, 48.1486],
        photo: "bratislava.jpg",
        location: "Bratislava",
        color: "#28a745"
    },
    {
        country: "Spain",
        coordinates: [2.1734, 41.3851],
        photo: "barcelona.jpg",
        location: "Barcelona",
        color: "#28a745"
    },
    {
        country: "Spain",
        coordinates: [-3.7038, 40.4168],
        photo: "madrid.jpg",
        location: "Madrid",
        color: "#28a745"
    },
    {
        country: "Sweden",
        coordinates: [18.0686, 59.3293],
        photo: "stockholm.jpg",
        location: "Stockholm",
        color: "#28a745"
    },
    {
        country: "United Kingdom",
        coordinates: [-3.1791, 51.4816],
        photo: "cardiff.jpg",
        location: "Cardiff",
        color: "#28a745"
    },
    {
        country: "United Kingdom",
        coordinates: [-3.2186, 51.5826],
        photo: "caerphilly.jpg",
        location: "Caerphilly",
        color: "#28a745"
    },
    {
        country: "United Kingdom",
        coordinates: [-0.1278, 51.5074],
        photo: "london.jpg",
        location: "London",
        color: "#28a745"
    }
];

// Initialize the map
function initializeMap() {
    // Check if token is available before proceeding
    if (!window.mapboxToken || window.mapboxToken.trim() === '') {
        console.error('Cannot initialize map: Mapbox token is not available.');
        return;
    }

    const map = new mapboxgl.Map({
        container: 'map',
        style: 'mapbox://styles/mapbox/dark-v11',
        center: [-23.393254, 5.411838], // [lng, lat] - centered around Brazil and Argentina
        zoom: 2,
        projection: 'mercator'
    });

    map.on('load', () => {
        // Add country highlighting source
        map.addSource('countries', {
            'type': 'vector',
            'url': 'mapbox://mapbox.country-boundaries-v1'
        });

        // Get unique countries for highlighting
        const uniqueCountries = [...new Set(visitedPlaces.map(place => place.country))];
        
        // Add country highlighting layers
        uniqueCountries.forEach(country => {
            const countryData = visitedPlaces.find(place => place.country === country);
            const color = countryData.color;
            
            map.addLayer({
                'id': `country-${country}`,
                'type': 'fill',
                'source': 'countries',
                'source-layer': 'country_boundaries',
                'filter': ['==', ['get', 'name_en'], country],
                'paint': {
                    'fill-color': color,
                    'fill-opacity': 0.5
                }
            });

            map.addLayer({
                'id': `country-border-${country}`,
                'type': 'line',
                'source': 'countries',
                'source-layer': 'country_boundaries',
                'filter': ['==', ['get', 'name_en'], country],
                'paint': {
                    'line-color': '#000000',
                    'line-width': 1
                }
            });
        });

        // Add markers for each visited place
        visitedPlaces.forEach(place => {
            // Create custom marker
            const el = document.createElement('div');
            el.className = 'custom-marker';
            el.style.backgroundColor = place.color;
            el.style.width = '20px';
            el.style.height = '20px';
            el.style.borderRadius = '50%';
            el.style.border = '2px solid white';
            el.style.cursor = 'pointer';
            el.style.boxShadow = '0 2px 4px rgba(0,0,0,0.3)';

            // Create popup content
            const popupContent = `
                <div class="map-popup">
                    <img src="/static/images/map/${place.photo}" alt="${place.location}" style="width: 200px; height: 150px; object-fit: cover; border-radius: 8px;">
                    <h6 style="margin-top: 10px; margin-bottom: 5px; text-align: center;">${place.location}</h6>
                    <p style="margin: 0; text-align: center; color: #666; font-size: 14px;">${place.country}</p>
                </div>
            `;

            // Create popup
            const popup = new mapboxgl.Popup({ 
                offset: 25,
                maxWidth: '250px'
            }).setHTML(popupContent);

            // Create marker
            new mapboxgl.Marker(el)
                .setLngLat(place.coordinates)
                .setPopup(popup)
                .addTo(map);
        });

        // Add navigation controls
        map.addControl(new mapboxgl.NavigationControl());
        
        // Add fullscreen control
        map.addControl(new mapboxgl.FullscreenControl());

        // Remove loading indicator once everything is loaded
        removeLoadingIndicator();
    });

    // Improved loading state management
    map.on('idle', () => {
        // Map is fully loaded and rendered when idle
        removeLoadingIndicator();
    });

    // Handle map load errors
    map.on('error', (e) => {
        console.error('Map loading error:', e);
        removeLoadingIndicator();
        showMapError('Failed to load map. Please try again later.');
    });
}

// Helper function to remove loading indicator
function removeLoadingIndicator() {
    const loadingIndicator = document.getElementById('loading-indicator');
    if (loadingIndicator) {
        loadingIndicator.remove();
    }
}

// Helper function to show map errors
function showMapError(message) {
    const mapContainer = document.getElementById('map');
    if (mapContainer) {
        const errorDiv = document.createElement('div');
        errorDiv.style.cssText = `
            display: flex; 
            align-items: center; 
            justify-content: center; 
            height: 100%; 
            color: #721c24; 
            background-color: #f8d7da; 
            border: 1px solid #f5c6cb; 
            border-radius: 0.25rem; 
            padding: 0.75rem 1.25rem;
            text-align: center;
        `;
        errorDiv.innerHTML = `<strong>Error:</strong>&nbsp;${message}`;
        mapContainer.appendChild(errorDiv);
    }
}

// Initialize map when DOM is ready
document.addEventListener('DOMContentLoaded', initializeMap);
