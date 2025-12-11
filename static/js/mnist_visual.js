/**
 * MNIST 3D Visualization - Interactive Canvas and API Integration
 * 
 * This script provides:
 * - Interactive canvas for drawing digits (28x28 resolution)
 * - POST requests to MNIST API with activations
 * - Display of predictions and confidence scores
 * - Integration point for 3D visualization (to be implemented)
 */

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

function init() {
    console.log('MNIST 3D Visualization - Initializing...');
    initializeCanvas();
    initializeVisualization();
}

// ==================== CANVAS SETUP ====================
let canvas, ctx;
let isDrawing = false;
let lastPos = { x: 0, y: 0 };
let updateInputLayerTimer = null; // Throttle timer for real-time updates

function initializeCanvas() {
    console.log('initializeCanvas called');
    canvas = document.getElementById('canvas');
    if (!canvas) {
        console.error('Canvas element not found!');
        return;
    }
    
    console.log('Canvas element found:', canvas);
    ctx = canvas.getContext('2d');
    
    // Canvas configuration
    ctx.lineWidth = 20;
    ctx.lineJoin = 'round';
    ctx.lineCap = 'round';
    ctx.strokeStyle = '#fff';
    
    // Initialize with black background
    ctx.fillStyle = '#000000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Setup event listeners
    setupCanvasEvents();
    
    console.log('Canvas initialized successfully, event listeners attached');
}

function setupCanvasEvents() {
    console.log('setupCanvasEvents called, canvas:', canvas);
    
    // ==================== MOUSE EVENTS ====================
    canvas.addEventListener('mousedown', (e) => {
        console.log('mousedown event');
        isDrawing = true;
        lastPos = getMousePos(canvas, e);
    });

    canvas.addEventListener('mouseup', () => {
        isDrawing = false;
    });

    canvas.addEventListener('mousemove', (e) => {
        if (!isDrawing) return;
        
        const currentPos = getMousePos(canvas, e);
        ctx.beginPath();
        ctx.moveTo(lastPos.x, lastPos.y);
        ctx.lineTo(currentPos.x, currentPos.y);
        ctx.stroke();
        lastPos = currentPos;
        
        // Update Input layer in real-time
        updateInputLayerRealtime();
    });

    canvas.addEventListener('mouseleave', () => {
        isDrawing = false;
    });

    // ==================== TOUCH EVENTS ====================
    canvas.addEventListener('touchstart', (e) => {
        e.preventDefault();
        const touch = e.touches[0];
        const mouseEvent = new MouseEvent('mousedown', {
            clientX: touch.clientX,
            clientY: touch.clientY
        });
        canvas.dispatchEvent(mouseEvent);
    });

    canvas.addEventListener('touchend', (e) => {
        e.preventDefault();
        const mouseEvent = new MouseEvent('mouseup', {});
        canvas.dispatchEvent(mouseEvent);
    });

    canvas.addEventListener('touchmove', (e) => {
        e.preventDefault();
        const touch = e.touches[0];
        const mouseEvent = new MouseEvent('mousemove', {
            clientX: touch.clientX,
            clientY: touch.clientY
        });
        canvas.dispatchEvent(mouseEvent);
    });
    
    // ==================== BUTTON EVENTS ====================
    document.getElementById('btn-clear').addEventListener('click', clearCanvas);
    document.getElementById('btn-visualize').addEventListener('click', visualizeDigit);
}

// ==================== UTILITY FUNCTIONS ====================
function getMousePos(canvasDom, mouseEvent) {
    const rect = canvasDom.getBoundingClientRect();
    return {
        x: mouseEvent.clientX - rect.left,
        y: mouseEvent.clientY - rect.top
    };
}

function clearCanvas() {
    // Clear the canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Re-fill with black background (required for MNIST preprocessing)
    ctx.fillStyle = '#000000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Hide prediction panels
    hidePredictionPanel();
    
    // Reset 3D visualization to empty state (without rebuilding)
    if (window.cnnVisualizer) {
        window.cnnVisualizer.resetToEmpty();
    }
    
    // Clear feature map previews
    clearFeatureMapPreviews();
}

function getCanvasImageData() {
    // Get canvas as base64 data URL
    return canvas.toDataURL('image/png');
}

function getCanvasPixelData() {
    // Get the canvas pixel data as a 28x28 array (normalized 0-1)
    // This matches what the model receives
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const pixels = [];
    
    // Downsample to 28x28 and normalize
    const scaleX = canvas.width / 28;
    const scaleY = canvas.height / 28;
    
    for (let y = 0; y < 28; y++) {
        for (let x = 0; x < 28; x++) {
            // Sample the center of each 28x28 grid cell
            const srcX = Math.floor((x + 0.5) * scaleX);
            const srcY = Math.floor((y + 0.5) * scaleY);
            const idx = (srcY * canvas.width + srcX) * 4;
            
            // Convert RGB to grayscale (use red channel since drawing is white on black)
            const gray = imageData.data[idx] / 255.0;
            pixels.push(gray);
        }
    }
    
    return pixels;
}

/**
 * Update only the Input layer in real-time as user draws
 * Uses throttling to avoid excessive updates
 */
function updateInputLayerRealtime() {
    // Clear any pending update
    if (updateInputLayerTimer) {
        clearTimeout(updateInputLayerTimer);
    }
    
    // Schedule update with throttle (100ms)
    updateInputLayerTimer = setTimeout(() => {
        if (window.cnnVisualizer && window.cnnVisualizer.layerMeshes.length > 0) {
            // Get current canvas pixels
            const pixels = getCanvasPixelData();
            
            // Update only the Input layer (first layer, index 0)
            const inputLayerMesh = window.cnnVisualizer.layerMeshes[0];
            if (inputLayerMesh && inputLayerMesh.name === 'input') {
                const mesh = inputLayerMesh.mesh;
                
                // Update each neuron color based on pixel intensity
                pixels.forEach((value, index) => {
                    // Color mapping: 0 (black/no drawing) = blue, 1 (white/drawn) = yellow/red
                    if (value < 0.1) {
                        // Dark blue for empty pixels
                        window.cnnVisualizer.tempColor.setRGB(0, 0, 1);
                    } else if (value < 0.5) {
                        // Blue to Cyan
                        const t = value * 2;
                        window.cnnVisualizer.tempColor.setRGB(0, t, 1);
                    } else {
                        // Cyan to Yellow/White
                        const t = (value - 0.5) * 2;
                        window.cnnVisualizer.tempColor.setRGB(t, 1, 1 - t * 0.5);
                    }
                    
                    mesh.setColorAt(index, window.cnnVisualizer.tempColor);
                });
                
                mesh.instanceColor.needsUpdate = true;
            }
        }
    }, 50); // 50ms throttle
}

// ==================== UI FUNCTIONS ====================
function showLoading() {
    document.getElementById('loading-indicator').style.display = 'block';
    document.getElementById('btn-visualize').disabled = true;
}

function hideLoading() {
    document.getElementById('loading-indicator').style.display = 'none';
    document.getElementById('btn-visualize').disabled = false;
}

function showPredictionPanel() {
    const bottomPanel = document.getElementById('prediction-panel-bottom');
    if (bottomPanel) bottomPanel.style.display = 'block';
}

function hidePredictionPanel() {
    const bottomPanel = document.getElementById('prediction-panel-bottom');
    if (bottomPanel) bottomPanel.style.display = 'none';
}

function displayPrediction(data) {
    // API returns predictions array with top 3 predictions
    // Example: [{"digit":0,"probability":0.87}, {"digit":8,"probability":0.11}, ...]
    
    if (!data.predictions || !Array.isArray(data.predictions) || data.predictions.length === 0) {
        console.error('Invalid predictions format:', data);
        return;
    }
    
    // Populate only the bottom prediction panel (beside feature maps)
    const top3List = document.getElementById('top-3-list-bottom');
    if (!top3List) return;
    
    top3List.innerHTML = '';
    
    // Create progress bars for each prediction
    data.predictions.forEach((pred, idx) => {
        const probability = (pred.probability * 100).toFixed(2);
        const progressBarColor = idx === 0 ? 'bg-success' : idx === 1 ? 'bg-primary' : 'bg-danger';
        
        top3List.innerHTML += `
            <div class="d-flex align-items-center my-2">
                <strong>${idx + 1}. ${pred.digit}:</strong>
                <div class="progress flex-grow-1 mx-2" style="height: 20px;">
                    <div class="progress-bar ${progressBarColor}" role="progressbar" style="width: 0%;" 
                         aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"></div>
                </div>
            </div>
        `;
    });
    
    // Animate progress bars
    const progressBars = top3List.querySelectorAll('.progress-bar');
    progressBars.forEach((bar, idx) => {
        const targetPercentage = data.predictions[idx].probability * 100;
        animateProgressBar(bar, targetPercentage);
    });
    
    showPredictionPanel();
}

// ==================== TEMPORARY: FEATURE MAP EXPORT ====================
/**
 * Save feature maps as downloadable PNG images in a ZIP file
 * TEMPORARY FUNCTION FOR DEVELOPMENT/ANALYSIS - TO BE REMOVED
 */
async function saveFeatureMapsAsImages(activations) {
    console.log('Saving feature maps as images...');
    
    const layers = [
        { name: 'conv2d', data: activations.conv2d, size: 26 },
        { name: 'conv2d_1', data: activations.conv2d_1, size: 11 },
        { name: 'conv2d_2', data: activations.conv2d_2, size: 3 }
    ];
    
    const images = [];
    
    for (const layer of layers) {
        console.log(`Processing ${layer.name}...`, layer.data);
        
        if (!layer.data || !layer.data.feature_maps) {
            console.warn(`No feature maps for ${layer.name}`);
            continue;
        }
        
        // Save first 12 feature maps of each layer
        const featureMaps = layer.data.feature_maps.slice(0, 12);
        console.log(`${layer.name}: ${featureMaps.length} feature maps`);
        
        for (let idx = 0; idx < featureMaps.length; idx++) {
            const fmap = featureMaps[idx];
            const canvas = document.createElement('canvas');
            const scaleFactor = 20; // Scale up small images
            canvas.width = layer.size * scaleFactor;
            canvas.height = layer.size * scaleFactor;
            const ctx = canvas.getContext('2d');
            
            // Find min/max for normalization
            let min = Infinity, max = -Infinity;
            fmap.forEach(row => {
                row.forEach(val => {
                    min = Math.min(min, val);
                    max = Math.max(max, val);
                });
            });
            
            const range = max - min || 1;
            
            // Draw feature map with viridis-like colormap
            fmap.forEach((row, y) => {
                row.forEach((val, x) => {
                    // Normalize to 0-1
                    const normalized = (val - min) / range;
                    
                    // Simple viridis approximation (blue -> cyan -> yellow)
                    let r, g, b;
                    if (normalized < 0.5) {
                        const t = normalized * 2;
                        r = 0;
                        g = Math.floor(t * 255);
                        b = Math.floor((1 - t * 0.5) * 255);
                    } else {
                        const t = (normalized - 0.5) * 2;
                        r = Math.floor(t * 255);
                        g = 255;
                        b = Math.floor((1 - t) * 128);
                    }
                    
                    ctx.fillStyle = `rgb(${r},${g},${b})`;
                    ctx.fillRect(x * scaleFactor, y * scaleFactor, scaleFactor, scaleFactor);
                });
            });
            
            // Convert to blob and store
            const blob = await new Promise(resolve => canvas.toBlob(resolve));
            images.push({
                name: `${layer.name}_fmap_${idx.toString().padStart(2, '0')}.png`,
                blob: blob
            });
        }
    }
    
    console.log(`Generated ${images.length} images, downloading as single ZIP...`);
    
    // Download all as a single ZIP file
    const zip = await createZipFromImages(images);
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
    downloadBlob(zip, `feature_maps_${timestamp}.zip`);
    
    console.log('Feature maps ZIP downloaded! Extract to your maps folder.');
}

/**
 * Create a ZIP file from image blobs
 */
async function createZipFromImages(images) {
    // Use native browser APIs to create ZIP (basic implementation)
    // For production, you'd use JSZip library, but for quick test:
    
    // Actually, let's just download them with delay to avoid blocking
    // Browser blocks multiple simultaneous downloads
    for (let i = 0; i < images.length; i++) {
        await new Promise(resolve => setTimeout(resolve, 200)); // 200ms delay between downloads
        downloadBlob(images[i].blob, images[i].name);
    }
    
    return null; // Not using ZIP for now due to library requirement
}

/**
 * Download a blob with given filename
 */
function downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a); // Required for Firefox
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

/**
 * Animates a progress bar to show prediction confidence
 * @param {Element} element - The progress bar element
 * @param {number} targetPercentage - Final percentage to animate to
 */
function animateProgressBar(element, targetPercentage) {
    // Round to avoid showing tiny percentages as 1%
    const roundedTarget = Math.round(targetPercentage);
    
    // Skip animation for values < 1%
    if (roundedTarget < 1) {
        element.style.width = '0%';
        element.setAttribute('aria-valuenow', 0);
        element.innerHTML = '< 1%';
        return;
    }
    
    let width = 0;
    const interval = setInterval(function() {
        if (width >= roundedTarget) {
            clearInterval(interval);
        } else {
            width++;
            element.style.width = width + '%';
            element.setAttribute('aria-valuenow', width);
            element.innerHTML = width + '%';
        }
    }, 10);
}

function showError(message) {
    alert(`Error: ${message}\n\nPlease try again or check the console for details.`);
}

// ==================== API COMMUNICATION ====================
async function visualizeDigit() {
    // Get canvas data
    const imageData = getCanvasImageData();
    
    // Check if canvas is empty (mostly black)
    if (isCanvasEmpty()) {
        alert('Please draw a digit first!');
        return;
    }
    
    // Show loading state
    showLoading();
    
    // Debug: log first 100 chars of base64 to verify it's changing
    console.log('Sending image (first 100 chars):', imageData.substring(0, 100));
    
    try {
        // Get API endpoint from window (set in template)
        const apiEndpoint = window.apiEndpoint;
        
        if (!apiEndpoint) {
            throw new Error('API endpoint not configured');
        }
        
        // Make POST request
        const response = await fetch(apiEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                imageBase64: imageData
            })
        });
        
        if (!response.ok) {
            throw new Error(`API returned ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        console.log('Full API response:', data);
        
        // Add canvas pixel data to response for input layer visualization
        data.input_image = getCanvasPixelData();
        
        // Display prediction results
        displayPrediction(data);
        
        // Visualize activations in 3D - pass entire response object
        if (data.activations) {
            console.log('Starting 3D visualization...');
            visualize3D(data);  // Pass full response, not just activations
        } else {
            console.warn('No activations in API response');
        }
        
    } catch (error) {
        console.error('Visualization error:', error);
        showError(error.message);
    } finally {
        hideLoading();
    }
}

function isCanvasEmpty() {
    // Check if canvas has any non-black pixels
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const pixels = imageData.data;
    
    // Check if any pixel has significant brightness
    for (let i = 0; i < pixels.length; i += 4) {
        const r = pixels[i];
        const g = pixels[i + 1];
        const b = pixels[i + 2];
        const brightness = (r + g + b) / 3;
        
        if (brightness > 10) { // Threshold for "drawn"
            return false;
        }
    }
    
    return true;
}

// ==================== 3D VISUALIZATION ====================
/**
 * CNNVisualizer3D - Interactive 3D visualization of CNN activations
 * Adapted from Neural-Network-Visualisation for CNN architecture
 * 
 * Visualizes:
 * - Dense layers as spheres (like MLP neurons)
 * - Connections between neurons (top-N strongest weights)
 * - Activation intensity via color mapping
 */
class CNNVisualizer3D {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.activations = null;
        
        // Visualization state
        this.layerMeshes = [];      // Array of {mesh, positions, type, layerIndex}
        this.connectionGroups = []; // Array of {mesh, connections, sourceLayer}
        this.meshes = [];           // All meshes for cleanup
        
        // Temporary objects for matrix calculations
        this.tempObject = new THREE.Object3D();
        this.tempColor = new THREE.Color();
        this.upVector = new THREE.Vector3(0, 1, 0);
        
        // Configuration (similar to Neural-Network-Visualisation)
        this.config = {
            layerSpacing: 8.0,           // Distance between layers along X axis
            neuronSpacing: 1.2,          // Spacing between neurons in grid
            neuronSize: 0.35,            // Sphere radius for neurons
            connectionRadius: 0.012,     // Cylinder radius for connections
            maxConnectionsPerNeuron: 64, // Top-N connections to show
            cameraDistance: 20,          // Initial camera distance (closer for better view)
            flattenSampleRate: 8,        // Show 1 out of every N neurons for flatten
            colors: {
                background: 0x000000,    // Pure black background (matching canvas)
                neuron: 0xffffff,
                connectionPositive: 0x00ff00,  // Green for positive contribution
                connectionNegative: 0xff0000   // Red for negative contribution
            }
        };
        
        // Scene center (will be calculated after building layers)
        this.sceneCenter = new THREE.Vector3(0, 0, 0);
        
        this.init();
    }
    
    init() {
        // Create scene
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(this.config.colors.background);
        
        // Setup camera
        const aspect = this.container.clientWidth / this.container.clientHeight;
        this.camera = new THREE.PerspectiveCamera(60, aspect, 0.1, 1000);
        this.camera.position.set(20, 10, this.config.cameraDistance);
        this.camera.lookAt(0, 0, 0);
        
        // Setup renderer
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.container.appendChild(this.renderer.domElement);
        
        // Setup basic mouse controls
        this.setupBasicControls();
        
        // Add lighting
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        this.scene.add(ambientLight);
        
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.5);
        directionalLight.position.set(10, 10, 10);
        this.scene.add(directionalLight);
        
        // Handle window resize
        window.addEventListener('resize', () => this.onWindowResize());
        
        // Start animation loop
        this.animate();
        
        console.log('CNNVisualizer3D initialized');
    }
    
    /**
     * Setup basic mouse controls for camera rotation
     */
    setupBasicControls() {
        this.isDragging = false;
        this.previousMousePosition = { x: 0, y: 0 };
        this.rotation = { x: 0.15, y: 0.1 }; // Initial rotation (slightly tilted for better depth view)
        
        this.renderer.domElement.addEventListener('mousedown', (e) => {
            this.isDragging = true;
            this.previousMousePosition = { x: e.clientX, y: e.clientY };
        });
        
        this.renderer.domElement.addEventListener('mousemove', (e) => {
            if (!this.isDragging) return;
            
            const deltaX = e.clientX - this.previousMousePosition.x;
            const deltaY = e.clientY - this.previousMousePosition.y;
            
            this.rotation.y += deltaX * 0.01;
            this.rotation.x += deltaY * 0.01;
            
            // Clamp vertical rotation
            this.rotation.x = Math.max(-Math.PI / 2, Math.min(Math.PI / 2, this.rotation.x));
            
            // Update camera position
            this.updateCameraPosition();
            
            this.previousMousePosition = { x: e.clientX, y: e.clientY };
        });
        
        this.renderer.domElement.addEventListener('mouseup', () => {
            this.isDragging = false;
        });
        
        this.renderer.domElement.addEventListener('mouseleave', () => {
            this.isDragging = false;
        });
        
        // Zoom with mouse wheel
        this.renderer.domElement.addEventListener('wheel', (e) => {
            e.preventDefault();
            this.config.cameraDistance += e.deltaY * 0.05;
            this.config.cameraDistance = Math.max(15, Math.min(80, this.config.cameraDistance));
            this.updateCameraPosition();
        });
        
        // Initial camera position
        this.updateCameraPosition();
    }
    
    updateCameraPosition() {
        const distance = this.config.cameraDistance;
        this.camera.position.x = this.sceneCenter.x + distance * Math.sin(this.rotation.y) * Math.cos(this.rotation.x);
        this.camera.position.y = this.sceneCenter.y + distance * Math.sin(this.rotation.x);
        this.camera.position.z = this.sceneCenter.z + distance * Math.cos(this.rotation.y) * Math.cos(this.rotation.x);
        this.camera.lookAt(this.sceneCenter);
    }
    
    /**
     * Calculate scene center based on all layer positions and center camera
     */
    centerCameraOnScene() {
        if (this.layerMeshes.length === 0) return;
        
        // Calculate bounding box of all positions
        let minX = Infinity, maxX = -Infinity;
        let minY = Infinity, maxY = -Infinity;
        let minZ = Infinity, maxZ = -Infinity;
        
        this.layerMeshes.forEach(layer => {
            layer.positions.forEach(pos => {
                minX = Math.min(minX, pos.x);
                maxX = Math.max(maxX, pos.x);
                minY = Math.min(minY, pos.y);
                maxY = Math.max(maxY, pos.y);
                minZ = Math.min(minZ, pos.z);
                maxZ = Math.max(maxZ, pos.z);
            });
        });
        
        // Calculate center point
        this.sceneCenter.set(
            (minX + maxX) / 2,
            (minY + maxY) / 2,
            (minZ + maxZ) / 2
        );
        
        console.log('Scene centered at:', this.sceneCenter);
        
        // Update camera to look at center
        this.updateCameraPosition();
    }
    
    /**
     * Initialize visualization with zero activations (empty state)
     */
    initializeEmpty() {
        const emptyResponse = {
            activations: {
                conv2d: { feature_maps: [], shape: [1, 26, 26, 32] },
                conv2d_1: { feature_maps: [], shape: [1, 11, 11, 64] },
                conv2d_2: { feature_maps: [], shape: [1, 3, 3, 64] },
                flatten: { shape: [1, 576], isEmpty: true },
                dense: { activations: Array(64).fill(0) },
                dense_1: { activations: Array(10).fill(0) }
            },
            input_image: Array(784).fill(0) // 28x28 = 784 zeros
        };
        
        // Create dummy feature maps (all zeros)
        emptyResponse.activations.conv2d.feature_maps = Array(32).fill(null).map(() => 
            Array(26).fill(null).map(() => Array(26).fill(0))
        );
        emptyResponse.activations.conv2d_1.feature_maps = Array(64).fill(null).map(() => 
            Array(11).fill(null).map(() => Array(11).fill(0))
        );
        emptyResponse.activations.conv2d_2.feature_maps = Array(64).fill(null).map(() => 
            Array(3).fill(null).map(() => Array(3).fill(0))
        );
        
        console.log('Initializing empty visualization...');
        this.visualize(emptyResponse);
    }
    
    /**
     * Reset all activations to zero without rebuilding the scene
     * Used when clearing the canvas
     */
    resetToEmpty() {
        // Reset all neuron colors to dark blue (zero activation)
        this.layerMeshes.forEach(layerMesh => {
            const mesh = layerMesh.mesh;
            const count = mesh.count;
            
            // Set all neurons to dark blue (zero activation color)
            this.tempColor.setRGB(0, 0, 1); // Blue for zero
            for (let i = 0; i < count; i++) {
                mesh.setColorAt(i, this.tempColor);
            }
            mesh.instanceColor.needsUpdate = true;
        });
        
        // Hide all connections (InstancedMesh)
        this.connectionGroups.forEach(group => {
            const mesh = group.mesh;
            if (mesh && mesh.material) {
                mesh.material.opacity = 0;
                mesh.material.needsUpdate = true;
                mesh.visible = false;
            }
        });
    }
    
    /**
     * Main visualization function - called with API response data
     */
    visualize(apiResponse) {
        console.log('Visualizing API response:', apiResponse);
        console.log('Has activations:', !!apiResponse.activations);
        console.log('Has input_image:', !!apiResponse.input_image);
        
        // Extract dense layers from API response
        const denseLayers = this.extractDenseLayers(apiResponse);
        
        if (denseLayers.length === 0) {
            console.warn('No dense layers found in API response');
            return;
        }
        
        // Check if scene already exists (after initial build)
        const sceneExists = this.layerMeshes.length > 0;
        
        if (!sceneExists) {
            // First time - build complete scene
            console.log('Building initial scene...');
            
            // Build neuron meshes for each layer
            this.buildNeuronLayers(denseLayers);
            
            // Calculate and center camera on entire scene
            this.centerCameraOnScene();
        } else {
            // Scene exists - need to rebuild connections for new activations
            // Clear old connections
            this.connectionGroups.forEach(group => {
                if (group.mesh) {
                    this.scene.remove(group.mesh);
                    if (group.mesh.geometry) group.mesh.geometry.dispose();
                    if (group.mesh.material) group.mesh.material.dispose();
                }
            });
            this.connectionGroups = [];
        }
        
        // Build/rebuild connections based on current activations
        this.buildConnections(denseLayers);
        
        // Update activation colors (works for both initial and updates)
        this.updateActivationColors(denseLayers);
        
        console.log('Visualization complete - Layers rendered:', this.layerMeshes.length);
        console.log('Total meshes in scene:', this.meshes.length);
    }
    
    /**
     * Extract dense layer activations from API response
     */
    extractDenseLayers(apiResponse) {
        const layers = [];
        
        console.log('Extracting layers from API response...');
        
        // Check if activations exist
        if (!apiResponse.activations) {
            console.error('No activations in API response');
            return layers;
        }
        
        console.log('Available activations:', Object.keys(apiResponse.activations));
        
        // Build layers in correct order: Input → Conv2D → Conv2D_1 → Conv2D_2 → Flatten → Dense → Output
        
        // Add Input layer (28x28 original image) - FIRST layer showing drawn digit
        if (apiResponse.input_image) {
            try {
                // Input is the original 28x28 grayscale image
                const inputData = Array.isArray(apiResponse.input_image[0]) 
                    ? apiResponse.input_image.flat() 
                    : apiResponse.input_image;
                
                layers.push({
                    name: 'input',
                    type: 'input',
                    activations: inputData,
                    size: inputData.length,
                    shape: '28×28'
                });
                console.log('Input layer added: 28x28 =', inputData.length, 'pixels');
            } catch (err) {
                console.warn('Failed to add Input layer:', err);
            }
        } else {
            console.warn('No input_image in API response - Input layer skipped');
        }
        
        // Add Conv2D layer (use full H×W resolution, average across channels)
        if (apiResponse.activations.conv2d && apiResponse.activations.conv2d.feature_maps) {
            try {
                const featureMaps = apiResponse.activations.conv2d.feature_maps;
                const shape = apiResponse.activations.conv2d.shape; // [1, H, W, C]

                const height = shape[1];
                const width = shape[2];

                const fullValues = [];
                for (let i = 0; i < height; i++) {
                    for (let j = 0; j < width; j++) {
                        let sum = 0;
                        let count = 0;
                        for (let k = 0; k < featureMaps.length; k++) {
                            const map = featureMaps[k];
                            if (map && map[i] && map[i][j] !== undefined) {
                                sum += map[i][j];
                                count++;
                            }
                        }
                        fullValues.push(count > 0 ? sum / count : 0);
                    }
                }

                layers.push({
                    name: 'conv2d',
                    type: 'conv',
                    activations: fullValues,
                    size: fullValues.length,
                    shape: `${height}×${width}`,
                    channels: featureMaps.length,
                    featureMaps: featureMaps
                });
                console.log('Conv2D layer added:', fullValues.length, 'neurons');
            } catch (err) {
                console.error('Error adding Conv2D layer:', err);
            }
        }
        
        // Add Conv2D_1 layer (11x11x64 - render full 11x11 grid) - SECOND conv layer
        if (apiResponse.activations.conv2d_1 && apiResponse.activations.conv2d_1.feature_maps) {
            try {
                const featureMaps = apiResponse.activations.conv2d_1.feature_maps;
                const shape = apiResponse.activations.conv2d_1.shape; // [1, 11, 11, 64]
                
                console.log('Conv2D_1 shape:', shape, 'feature_maps length:', featureMaps.length);
                
                const height = shape[1]; // 11
                const width = shape[2];  // 11
                const fullValues = [];
                
                // Render all 11x11 pixels (121 neurons)
                for (let i = 0; i < height; i++) {
                    for (let j = 0; j < width; j++) {
                        // Average across all feature maps at this spatial position
                        let sum = 0;
                        featureMaps.forEach(map => {
                            if (map && map[i] && map[i][j] !== undefined) {
                                sum += map[i][j];
                            }
                        });
                        fullValues.push(sum / featureMaps.length);
                    }
                }
                
                layers.push({
                    name: 'conv2d_1',
                    type: 'conv',
                    activations: fullValues,
                    size: fullValues.length,
                    shape: '11×11',
                    channels: featureMaps.length,
                    featureMaps: featureMaps
                });
                console.log('Conv2D_1 layer added:', fullValues.length, 'neurons');
            } catch (err) {
                console.error('Error adding Conv2D_1 layer:', err);
            }
        }
        
        // Add Conv2D_2 layer (last convolutional layer - 3x3x64) - THIRD conv layer
        if (apiResponse.activations.conv2d_2 && apiResponse.activations.conv2d_2.feature_maps) {
            try {
                const featureMaps = apiResponse.activations.conv2d_2.feature_maps;
                const shape = apiResponse.activations.conv2d_2.shape; // [1, 3, 3, 64]
                
                console.log('Conv2D_2 shape:', shape, 'feature_maps length:', featureMaps.length);
                
                // Average all feature maps into a single 3x3 representation
                const height = shape[1]; // 3
                const width = shape[2];  // 3
                const avgMap = Array(height).fill(0).map(() => Array(width).fill(0));
                
                // Average across all feature maps
                featureMaps.forEach(map => {
                    for (let i = 0; i < height; i++) {
                        for (let j = 0; j < width; j++) {
                            if (map && map[i] && map[i][j] !== undefined) {
                                avgMap[i][j] += map[i][j] / featureMaps.length;
                            }
                        }
                    }
                });
                
                // Flatten to 1D for visualization (3x3 = 9 values)
                const flatValues = avgMap.flat();
                
                layers.push({
                    name: 'conv2d_2',
                    type: 'conv',
                    activations: flatValues,
                    size: flatValues.length,
                    shape: `${height}×${width}`,
                    channels: featureMaps.length,
                    featureMaps: featureMaps
                });
                console.log('Conv2D_2 layer added:', flatValues.length, 'neurons');
            } catch (err) {
                console.error('Error adding Conv2D_2 layer:', err);
            }
        }
        
        // Add flatten layer (576 values = 64 feature maps of 3x3)
        // Render as 64 layers of 3x3 grids to show all activations from Conv2D_2
        if (apiResponse.activations.flatten && apiResponse.activations.conv2d_2) {
            const isEmpty = apiResponse.activations.flatten.isEmpty === true;
            const featureMaps = apiResponse.activations.conv2d_2.feature_maps || [];
            
            // Each feature map is 3x3, we have 64 of them
            const allActivations = [];
            
            if (isEmpty) {
                // Empty initialization - all zeros
                for (let i = 0; i < 576; i++) {
                    allActivations.push(0);
                }
            } else {
                // Extract all values from the 64 feature maps (3x3 each)
                featureMaps.forEach(map => {
                    if (Array.isArray(map)) {
                        map.forEach(row => {
                            if (Array.isArray(row)) {
                                allActivations.push(...row);
                            }
                        });
                    }
                });
                
                // If we don't have 576 values, pad with random
                while (allActivations.length < 576) {
                    allActivations.push(Math.random() * 0.5);
                }
            }
            
            layers.push({
                name: 'flatten',
                type: 'flatten_3d', // New type to render as stacked 3x3 grids
                activations: allActivations,
                size: allActivations.length,
                gridSize: 3,        // Each layer is 3x3
                numLayers: 64,      // 64 feature maps stacked
                fullSize: 576
            });
        }
        
        // Add dense layer (64 neurons)
        if (apiResponse.activations.dense && apiResponse.activations.dense.activations) {
            layers.push({
                name: 'dense',
                type: 'hidden',
                activations: apiResponse.activations.dense.activations,
                size: apiResponse.activations.dense.activations.length
            });
        }
        
        // Add output layer (10 neurons - digits 0-9)
        if (apiResponse.activations.dense_1 && apiResponse.activations.dense_1.activations) {
            layers.push({
                name: 'dense_1',
                type: 'output',
                activations: apiResponse.activations.dense_1.activations,
                size: apiResponse.activations.dense_1.activations.length
            });
        }
        
        console.log('Extracted layers:', layers.map(l => `${l.name} (${l.size})`));
        return layers;
    }
    
    clearScene() {
        // Remove all meshes
        this.meshes.forEach(mesh => {
            if (mesh.geometry) mesh.geometry.dispose();
            if (mesh.material) {
                if (Array.isArray(mesh.material)) {
                    mesh.material.forEach(m => m.dispose());
                } else {
                    mesh.material.dispose();
                }
            }
            this.scene.remove(mesh);
        });
        this.meshes = [];
        this.layerMeshes = [];
        this.connectionGroups = [];
    }
    
    /**
     * Build neuron sphere meshes for each layer
     */
    buildNeuronLayers(denseLayers) {
        denseLayers.forEach((layer, layerIndex) => {
            const neuronCount = layer.size;
            const positions = this.computeLayerPositions(layerIndex, neuronCount, denseLayers.length, layer.type, layer);
            
            // Use smaller spheres for flatten layer
            const neuronSize = (layer.type === 'flatten' || layer.type === 'flatten_3d') ? 
                this.config.neuronSize * 0.5 : this.config.neuronSize;
            const sphereGeometry = new THREE.SphereGeometry(neuronSize, 16, 16);
            
            // Create instanced mesh for neurons
            const material = new THREE.MeshPhongMaterial({
                color: 0xffffff,
                emissive: 0x000000
            });
            
            const mesh = new THREE.InstancedMesh(sphereGeometry, material, neuronCount);
            mesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
            
            // Create instance color attribute
            const colors = new Float32Array(neuronCount * 3);
            for (let i = 0; i < neuronCount; i++) {
                colors[i * 3] = 1;
                colors[i * 3 + 1] = 1;
                colors[i * 3 + 2] = 1;
            }
            mesh.instanceColor = new THREE.InstancedBufferAttribute(colors, 3);
            
            // Position each neuron
            positions.forEach((position, index) => {
                this.tempObject.position.copy(position);
                this.tempObject.updateMatrix();
                mesh.setMatrixAt(index, this.tempObject.matrix);
            });
            
            mesh.instanceMatrix.needsUpdate = true;
            this.scene.add(mesh);
            this.meshes.push(mesh);
            
            this.layerMeshes.push({
                mesh,
                positions,
                type: layer.type,
                layerIndex,
                name: layer.name
            });
            
            // Add text label above layer
            this.createLayerLabel(positions, layer);
            
            // Add labels for output layer
            if (layer.type === 'output') {
                this.createOutputLabels(positions);
            }
        });
    }
    
    /**
     * Create text label above a layer
     */
    createLayerLabel(positions, layer) {
        // Determine label text based on layer
        let labelText = '';
        
        if (layer.type === 'input') {
            labelText = `Input (${layer.shape})`;
        } else if (layer.type === 'conv') {
            // Extract layer name: conv2d, conv2d_1, conv2d_2
            const layerName = layer.name === 'conv2d' ? 'Conv2D' : 
                             layer.name === 'conv2d_1' ? 'Conv2D_1' : 'Conv2D_2';
            labelText = `${layerName} (${layer.shape})`;
        } else if (layer.type === 'flatten') {
            labelText = `Flatten (${layer.size})`;
        } else if (layer.type === 'flatten_3d') {
            labelText = `Flatten (64×3×3)`;
        } else if (layer.type === 'hidden') {
            labelText = `Dense (${layer.size})`;
        } else if (layer.type === 'output') {
            labelText = `Output (${layer.size})`;
        }
        
        if (!labelText) return;
        
        // Calculate position above the layer
        const minY = Math.min(...positions.map(p => p.y));
        const maxY = Math.max(...positions.map(p => p.y));
        const avgX = positions.length > 0 ? positions[0].x : 0;
        const avgZ = positions.reduce((sum, p) => sum + p.z, 0) / positions.length;
        
        const labelY = maxY + 2; // Position above the layer
        
        // Create label with larger font
        const label = this.createTextSprite(labelText, 1.2, '#ffffff');
        label.position.set(avgX, labelY, avgZ);
        this.scene.add(label);
        this.meshes.push(label);
    }
    
    /**
     * Create a text sprite
     */
    createTextSprite(text, scale, color) {
        const canvas = document.createElement('canvas');
        canvas.width = 1024;
        canvas.height = 256;
        const ctx = canvas.getContext('2d');
        
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.font = 'bold 120px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillStyle = color;
        ctx.fillText(text, canvas.width / 2, canvas.height / 2);
        
        const texture = new THREE.CanvasTexture(canvas);
        const spriteMaterial = new THREE.SpriteMaterial({ 
            map: texture,
            transparent: true,
            depthTest: false
        });
        const sprite = new THREE.Sprite(spriteMaterial);
        sprite.scale.set(scale * 8, scale * 2, 1);
        
        return sprite;
    }
    
    /**
     * Compute 3D positions for neurons in a layer
     */
    computeLayerPositions(layerIndex, neuronCount, totalLayers, layerType, layer = null) {
        const positions = [];
        const layerX = layerIndex * this.config.layerSpacing;
        
        // Special handling for flatten_3d: 64 layers of 3x3 grids
        if (layerType === 'flatten_3d' && layer && layer.gridSize && layer.numLayers) {
            const gridSize = layer.gridSize; // 3
            const numLayers = layer.numLayers; // 64
            const gridSpacing = this.config.neuronSpacing * 0.6;
            const layerDepth = 0.15; // Space between each 3x3 layer
            
            for (let depth = 0; depth < numLayers; depth++) {
                for (let i = 0; i < gridSize * gridSize; i++) {
                    const row = Math.floor(i / gridSize);
                    const col = i % gridSize;
                    const y = ((gridSize - 1) / 2 - row) * gridSpacing;
                    const z = (col - (gridSize - 1) / 2) * gridSpacing + (depth - numLayers / 2) * layerDepth;
                    positions.push(new THREE.Vector3(layerX, y, z));
                }
            }
            
            return positions;
        }
        
        // Arrange neurons based on layer type and size
        if (layerType === 'input') {
            // 28x28 grid for input layer (784 neurons)
            const gridSize = Math.sqrt(neuronCount);
            const spacing = this.config.neuronSpacing * 0.4; // Uniform spacing for all grid layers
            
            for (let i = 0; i < neuronCount; i++) {
                const row = Math.floor(i / gridSize);
                const col = i % gridSize;
                const y = ((gridSize - 1) / 2 - row) * spacing;
                const z = (col - (gridSize - 1) / 2) * spacing;
                positions.push(new THREE.Vector3(layerX, y, z));
            }
        } else if (layerType === 'conv') {
            // Grid for conv layers - use same uniform spacing for all
            const gridSize = Math.sqrt(neuronCount);
            const spacing = this.config.neuronSpacing * 0.4; // Same as input for consistent scale
            
            for (let i = 0; i < neuronCount; i++) {
                const row = Math.floor(i / gridSize);
                const col = i % gridSize;
                const y = ((gridSize - 1) / 2 - row) * spacing;
                const z = (col - (gridSize - 1) / 2) * spacing;
                positions.push(new THREE.Vector3(layerX, y, z));
            }
        } else if (neuronCount <= 10) {
            // Vertical line (good for output layer - 10 neurons)
            const spacing = this.config.neuronSpacing;
            const totalHeight = (neuronCount - 1) * spacing;
            
            for (let i = 0; i < neuronCount; i++) {
                const y = (totalHeight / 2) - (i * spacing);
                positions.push(new THREE.Vector3(layerX, y, 0));
            }
        } else if (layerType === 'flatten') {
            // Vertical column for flatten layer (sampled ~72 neurons)
            // Use moderate spacing for better visibility
            const columnSpacing = 0.25;
            const totalHeight = (neuronCount - 1) * columnSpacing;
            
            for (let i = 0; i < neuronCount; i++) {
                const y = (totalHeight / 2) - (i * columnSpacing);
                positions.push(new THREE.Vector3(layerX, y, 0));
            }
        } else {
            // Grid arrangement (good for hidden layers - 64 neurons)
            const cols = Math.ceil(Math.sqrt(neuronCount));
            const rows = Math.ceil(neuronCount / cols);
            const spacing = this.config.neuronSpacing;
            
            for (let i = 0; i < neuronCount; i++) {
                const row = Math.floor(i / cols);
                const col = i % cols;
                const y = ((rows - 1) / 2 - row) * spacing;
                const z = (col - (cols - 1) / 2) * spacing;
                positions.push(new THREE.Vector3(layerX, y, z));
            }
        }
        
        return positions;
    }
    
    /**
     * Create text labels for output layer (digits 0-9)
     */
    createOutputLabels(positions) {
        const labelOffset = 0.8;
        
        positions.forEach((position, index) => {
            const canvas = document.createElement('canvas');
            canvas.width = 512;
            canvas.height = 512;
            const ctx = canvas.getContext('2d');
            
            // Draw digit label
            ctx.fillStyle = 'rgba(255, 255, 255, 0.95)';
            ctx.font = 'bold 280px Arial';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(String(index), 256, 256);
            
            // Create sprite
            const texture = new THREE.CanvasTexture(canvas);
            const spriteMaterial = new THREE.SpriteMaterial({ 
                map: texture,
                transparent: true
            });
            const sprite = new THREE.Sprite(spriteMaterial);
            
            sprite.position.copy(position);
            sprite.position.x += labelOffset;
            sprite.scale.set(1.0, 1.0, 1);
            
            this.scene.add(sprite);
            this.meshes.push(sprite);
        });
    }
    
    /**
     * Build connections between layers
     * Note: API doesn't return actual weights, so we simulate connections
     * based on activation values
     */
    buildConnections(denseLayers) {
        if (denseLayers.length < 2) return;
        
        const cylinderGeometry = new THREE.CylinderGeometry(
            this.config.connectionRadius,
            this.config.connectionRadius,
            1,
            8,
            1,
            true
        );
        
        // Connect each pair of adjacent layers
        for (let layerIdx = 0; layerIdx < denseLayers.length - 1; layerIdx++) {
            const sourceLayer = this.layerMeshes[layerIdx];
            const targetLayer = this.layerMeshes[layerIdx + 1];
            
            if (!sourceLayer || !targetLayer) continue;
            
            const connections = this.selectImportantConnections(
                sourceLayer,
                targetLayer,
                denseLayers[layerIdx].activations,
                denseLayers[layerIdx + 1].activations
            );
            
            if (connections.length === 0) continue;
            
            // Create instanced mesh for connections
            const material = new THREE.MeshBasicMaterial({
                color: 0xffffff,
                transparent: true,
                opacity: 0.3
            });
            
            const mesh = new THREE.InstancedMesh(cylinderGeometry, material, connections.length);
            mesh.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
            
            // Create instance color attribute
            const colors = new Float32Array(connections.length * 3);
            mesh.instanceColor = new THREE.InstancedBufferAttribute(colors, 3);
            
            // Position each connection
            connections.forEach((conn, index) => {
                const sourcePos = sourceLayer.positions[conn.sourceIndex];
                const targetPos = targetLayer.positions[conn.targetIndex];
                
                // Calculate cylinder position and orientation
                const direction = new THREE.Vector3().subVectors(targetPos, sourcePos);
                const length = direction.length();
                const midpoint = new THREE.Vector3().addVectors(sourcePos, targetPos).multiplyScalar(0.5);
                
                this.tempObject.position.copy(midpoint);
                this.tempObject.quaternion.setFromUnitVectors(this.upVector, direction.normalize());
                this.tempObject.scale.set(1, length, 1);
                this.tempObject.updateMatrix();
                
                mesh.setMatrixAt(index, this.tempObject.matrix);
                
                // Set initial color (will be updated by activation)
                mesh.setColorAt(index, this.tempColor.setRGB(0.5, 0.5, 0.5));
            });
            
            mesh.instanceMatrix.needsUpdate = true;
            mesh.instanceColor.needsUpdate = true;
            
            this.scene.add(mesh);
            this.meshes.push(mesh);
            
            this.connectionGroups.push({
                mesh,
                connections,
                sourceLayerIndex: layerIdx,
                targetLayerIndex: layerIdx + 1
            });
        }
    }
    
    /**
     * Select important connections to visualize
     * Optimized for large layers - limits total connections to prevent performance issues
     */
    selectImportantConnections(sourceLayer, targetLayer, sourceActivations, targetActivations) {
        const connections = [];
        const minStrengthThreshold = 0.001;
        
        // Calculate total possible connections
        const totalPossible = sourceLayer.positions.length * targetLayer.positions.length;
        
        // Set max connections based on layer sizes to prevent browser freeze
        let maxConnections;
        if (totalPossible > 500000) {
            // Very large (Input→Conv2D: 784×676 = 529,984)
            maxConnections = 5000; // Drastically limit
        } else if (totalPossible > 100000) {
            maxConnections = 10000;
        } else if (totalPossible > 10000) {
            maxConnections = 20000;
        } else {
            maxConnections = 50000; // No limit for small layers
        }
        
        // Collect all potential connections with their strengths
        const candidates = [];
        
        targetLayer.positions.forEach((targetPos, targetIndex) => {
            const targetActivation = targetActivations[targetIndex];
            
            // Skip if target has very low activation
            if (targetActivation < minStrengthThreshold) return;
            
            sourceLayer.positions.forEach((sourcePos, sourceIndex) => {
                const sourceActivation = sourceActivations[sourceIndex];
                
                // Heuristic: connection strength = product of activations
                const strength = sourceActivation * targetActivation;
                
                // Only consider connections with significant strength
                if (strength > minStrengthThreshold) {
                    candidates.push({
                        sourceIndex,
                        targetIndex,
                        strength
                    });
                }
            });
        });
        
        // If we have too many connections, keep only the strongest ones
        if (candidates.length > maxConnections) {
            console.log(`Limiting connections: ${candidates.length} → ${maxConnections} (${sourceLayer.name}→${targetLayer.name})`);
            candidates.sort((a, b) => b.strength - a.strength);
            return candidates.slice(0, maxConnections);
        }
        
        return candidates;
    }
    
    /**
     * Update neuron colors based on activation values
     */
    updateActivationColors(denseLayers) {
        denseLayers.forEach((layer, layerIndex) => {
            const layerMesh = this.layerMeshes[layerIndex];
            if (!layerMesh) return;
            
            const activations = layer.activations;
            const mesh = layerMesh.mesh;
            
            // Find max activation for normalization
            const maxActivation = Math.max(...activations.map(Math.abs));
            const scale = maxActivation > 0 ? maxActivation : 1;
            
            // Update each neuron color
            activations.forEach((value, index) => {
                const normalized = Math.abs(value) / scale;
                const clamped = Math.max(0, Math.min(1, normalized));
                
                // Color mapping: low (blue) → medium (cyan/white) → high (yellow/red)
                if (clamped < 0.5) {
                    // Blue to Cyan
                    const t = clamped * 2;
                    this.tempColor.setRGB(0, t, 1);
                } else {
                    // Cyan to Yellow/Red
                    const t = (clamped - 0.5) * 2;
                    this.tempColor.setRGB(t, 1, 1 - t);
                }
                
                mesh.setColorAt(index, this.tempColor);
            });
            
            mesh.instanceColor.needsUpdate = true;
        });
        
        // Update connection colors
        this.updateConnectionColors(denseLayers);
    }
    
    /**
     * Update connection colors based on activation flow
     */
    updateConnectionColors(denseLayers) {
        this.connectionGroups.forEach(group => {
            const sourceActivations = denseLayers[group.sourceLayerIndex].activations;
            const targetActivations = denseLayers[group.targetLayerIndex].activations;
            
            group.connections.forEach((conn, index) => {
                const sourceAct = sourceActivations[conn.sourceIndex];
                const targetAct = targetActivations[conn.targetIndex];
                
                // Contribution = source * target (simulated weight = 1)
                const contribution = sourceAct * targetAct;
                
                // Normalize contribution
                const maxContrib = Math.max(...group.connections.map(c => 
                    Math.abs(sourceActivations[c.sourceIndex] * targetActivations[c.targetIndex])
                ));
                
                const normalized = maxContrib > 0 ? contribution / maxContrib : 0;
                const clamped = Math.max(-1, Math.min(1, normalized));
                
                // Color: green for positive, red for negative, gray for neutral
                if (Math.abs(clamped) < 0.05) {
                    this.tempColor.setRGB(0.2, 0.2, 0.2);
                } else if (clamped > 0) {
                    this.tempColor.setRGB(0, clamped, 0);
                } else {
                    this.tempColor.setRGB(-clamped, 0, 0);
                }
                
                group.mesh.setColorAt(index, this.tempColor);
            });
            
            group.mesh.instanceColor.needsUpdate = true;
        });
    }
    
    onWindowResize() {
        const width = this.container.clientWidth;
        const height = this.container.clientHeight;
        
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(width, height);
    }
    
    animate() {
        requestAnimationFrame(() => this.animate());
        this.renderer.render(this.scene, this.camera);
    }
    
    dispose() {
        this.clearScene();
        this.renderer.dispose();
        if (this.container.contains(this.renderer.domElement)) {
            this.container.removeChild(this.renderer.domElement);
        }
    }
}

// ==================== VISUALIZATION ENTRY POINT ====================
function visualize3D(apiResponse) {
    // Check if Three.js is loaded
    if (typeof THREE === 'undefined') {
        console.error('THREE.js not loaded yet, waiting...');
        // Retry after a short delay
        setTimeout(() => visualize3D(apiResponse), 100);
        return;
    }
    
    // Use the global visualizer instance created at initialization
    if (!window.cnnVisualizer) {
        console.error('Visualizer not initialized!');
        return;
    }
    
    try {
        window.cnnVisualizer.visualize(apiResponse);
        
        // Render feature map previews in separate section
        const layers = window.cnnVisualizer.extractDenseLayers(apiResponse, false);
        renderFeatureMapPreviews(layers);
    } catch (error) {
        console.error('Error visualizing:', error);
    }
}

// ==================== FEATURE MAP PREVIEW ====================
/**
 * Render feature maps in the preview section below the 3D visualization
 * Shows 2x2 grid of sample feature maps for each Conv layer
 */
function renderFeatureMapPreviews(layers) {
    const container = document.getElementById('feature-maps-container');
    if (!container) return;
    
    // Clear previous previews
    container.innerHTML = '';
    
    // Filter only Conv layers that have feature maps
    const convLayers = layers.filter(layer => 
        layer.type === 'conv' && layer.featureMaps && layer.featureMaps.length > 0
    );
    
    if (convLayers.length === 0) {
        container.style.display = 'none';
        return;
    }
    
    container.style.display = 'block';
    container.style.marginTop = '-20px'; // Move up
    
    // Create horizontal layout with labels on top
    const wrapper = document.createElement('div');
    wrapper.style.cssText = 'display: flex; justify-content: center; align-items: center; gap: 15px;';
    
    // Add Input image preview (from canvas)
    const inputGroup = document.createElement('div');
    inputGroup.style.cssText = 'display: flex; flex-direction: column; align-items: center;';
    
    const inputTitle = document.createElement('div');
    inputTitle.textContent = 'Input';
    inputTitle.style.cssText = 'color: #333; margin-bottom: 8px; font-size: 14px; font-weight: bold;';
    inputGroup.appendChild(inputTitle);
    
    // Create single input canvas with activation heatmap (like 3D visualization)
    const inputCanvas = document.createElement('canvas');
    inputCanvas.width = 134; // 2x64 + 5px gap + border
    inputCanvas.height = 134;
    inputCanvas.style.cssText = 'border: 1px solid #444; background: #000;';
    
    const inputCtx = inputCanvas.getContext('2d');
    
    // Get pixel data from canvas and create heatmap
    const sourceCanvas = document.getElementById('canvas');
    if (sourceCanvas) {
        const sourceCtx = sourceCanvas.getContext('2d');
        const imageData = sourceCtx.getImageData(0, 0, sourceCanvas.width, sourceCanvas.height);
        const pixels = imageData.data;
        
        const pixelSize = 134 / 28; // Size of each pixel in the visualization
        
        // Draw 28x28 grid with color gradient
        for (let y = 0; y < 28; y++) {
            for (let x = 0; x < 28; x++) {
                // Sample from source canvas
                const srcX = Math.floor((x / 28) * sourceCanvas.width);
                const srcY = Math.floor((y / 28) * sourceCanvas.height);
                const idx = (srcY * sourceCanvas.width + srcX) * 4;
                
                // Get grayscale value (use red channel since drawing is white on black)
                const value = pixels[idx] / 255.0;
                
                // Apply same color gradient as 3D visualization (blue -> cyan -> yellow -> red)
                let r, g, b;
                if (value < 0.25) {
                    const t = value * 4;
                    r = 0;
                    g = 0;
                    b = Math.floor(128 + 127 * t);
                } else if (value < 0.5) {
                    const t = (value - 0.25) * 4;
                    r = 0;
                    g = Math.floor(255 * t);
                    b = 255;
                } else if (value < 0.75) {
                    const t = (value - 0.5) * 4;
                    r = Math.floor(255 * t);
                    g = 255;
                    b = Math.floor(255 * (1 - t));
                } else {
                    const t = (value - 0.75) * 4;
                    r = 255;
                    g = Math.floor(255 * (1 - t));
                    b = 0;
                }
                
                inputCtx.fillStyle = `rgb(${r},${g},${b})`;
                inputCtx.fillRect(x * pixelSize, y * pixelSize, pixelSize, pixelSize);
            }
        }
    }
    
    inputGroup.appendChild(inputCanvas);
    wrapper.appendChild(inputGroup);
    
    // Arrow from Input to first Conv layer
    const inputArrow = document.createElement('div');
    inputArrow.innerHTML = `
        <svg width="60" height="80" viewBox="0 0 60 80" style="margin-top: 28px;">
            <defs>
                <marker id="arrowhead-input" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto">
                    <polygon points="0 0, 7 3, 0 6" fill="#333" />
                </marker>
            </defs>
            <line x1="5" y1="40" x2="52" y2="40" stroke="#333" stroke-width="2" marker-end="url(#arrowhead-input)" />
        </svg>
    `;
    wrapper.appendChild(inputArrow);
    
    // Create each Conv layer group with label on top
    convLayers.forEach((layer, idx) => {
        // Layer group container
        const layerGroup = document.createElement('div');
        layerGroup.style.cssText = 'display: flex; flex-direction: column; align-items: center;';
        
        // Layer title on top with better naming
        const title = document.createElement('div');
        let layerName = '';
        if (layer.name === 'conv2d') {
            layerName = `Conv2D (${layer.shape})`;
        } else if (layer.name === 'conv2d_1') {
            layerName = `Conv2D_1 (${layer.shape})`;
        } else if (layer.name === 'conv2d_2') {
            layerName = `Conv2D_2 (${layer.shape})`;
        } else {
            layerName = layer.name.replace('_', '');
        }
        title.textContent = layerName;
        title.style.cssText = 'color: #333; margin-bottom: 8px; font-size: 14px; font-weight: bold;';
        layerGroup.appendChild(title);
        
        // Create averaged feature map from all channels
        const avgCanvas = createAveragedFeatureMapCanvas(layer.featureMaps, layer.shape);
        layerGroup.appendChild(avgCanvas);
        wrapper.appendChild(layerGroup);
        
        // Add arrow between layers (except after last layer)
        if (idx < convLayers.length - 1) {
            const arrow = document.createElement('div');
            arrow.innerHTML = `
                <svg width="60" height="80" viewBox="0 0 60 80" style="margin-top: 28px;">
                    <defs>
                        <marker id="arrowhead-${idx}" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto">
                            <polygon points="0 0, 7 3, 0 6" fill="#333" />
                        </marker>
                    </defs>
                    <line x1="5" y1="40" x2="52" y2="40" stroke="#333" stroke-width="2" marker-end="url(#arrowhead-${idx})" />
                </svg>
            `;
            wrapper.appendChild(arrow);
        }
    });
    
    container.appendChild(wrapper);
}

/**
 * Create a canvas element displaying the average of all feature maps
 */
function createAveragedFeatureMapCanvas(featureMaps, shapeStr) {
    const size = parseInt(shapeStr.split('×')[0]); // Extract dimension (e.g., "26" from "26×26")
    const displaySize = 134; // Same size as input canvas
    
    const canvas = document.createElement('canvas');
    canvas.width = displaySize;
    canvas.height = displaySize;
    canvas.style.cssText = 'border: 1px solid #444; background: #000;';
    
    const ctx = canvas.getContext('2d');
    
    // Calculate average across all feature maps
    const avgFeatureMap = [];
    for (let y = 0; y < size; y++) {
        avgFeatureMap[y] = [];
        for (let x = 0; x < size; x++) {
            let sum = 0;
            let count = 0;
            
            // Average across all feature maps
            featureMaps.forEach(featureMap => {
                if (featureMap[y] && featureMap[y][x] !== undefined) {
                    sum += featureMap[y][x];
                    count++;
                }
            });
            
            avgFeatureMap[y][x] = count > 0 ? sum / count : 0;
        }
    }
    
    // Find min/max for normalization
    let min = Infinity, max = -Infinity;
    avgFeatureMap.forEach(row => {
        row.forEach(val => {
            min = Math.min(min, val);
            max = Math.max(max, val);
        });
    });
    
    const range = max - min || 1;
    const pixelSize = displaySize / size;
    
    // Draw averaged feature map with same gradient as input (blue -> cyan -> yellow -> red)
    avgFeatureMap.forEach((row, y) => {
        row.forEach((val, x) => {
            const normalized = (val - min) / range;
            
            // Apply same color gradient as input visualization
            let r, g, b;
            if (normalized < 0.25) {
                const t = normalized * 4;
                r = 0;
                g = 0;
                b = Math.floor(128 + 127 * t);
            } else if (normalized < 0.5) {
                const t = (normalized - 0.25) * 4;
                r = 0;
                g = Math.floor(255 * t);
                b = 255;
            } else if (normalized < 0.75) {
                const t = (normalized - 0.5) * 4;
                r = Math.floor(255 * t);
                g = 255;
                b = Math.floor(255 * (1 - t));
            } else {
                const t = (normalized - 0.75) * 4;
                r = 255;
                g = Math.floor(255 * (1 - t));
                b = 0;
            }
            
            ctx.fillStyle = `rgb(${r},${g},${b})`;
            ctx.fillRect(x * pixelSize, y * pixelSize, pixelSize, pixelSize);
        });
    });
    
    return canvas;
}

/**
 * Create a canvas element displaying a feature map with viridis colormap
 */
function createFeatureMapCanvas(featureMap, shapeStr) {
    const size = parseInt(shapeStr.split('×')[0]); // Extract dimension (e.g., "8" from "8×8")
    const displaySize = 64; // Fixed display size (compact)
    
    const canvas = document.createElement('canvas');
    canvas.width = displaySize;
    canvas.height = displaySize;
    canvas.style.cssText = 'border: 1px solid #444; background: #000;';
    
    const ctx = canvas.getContext('2d');
    
    // Find min/max for normalization
    let min = Infinity, max = -Infinity;
    featureMap.forEach(row => {
        row.forEach(val => {
            min = Math.min(min, val);
            max = Math.max(max, val);
        });
    });
    
    const range = max - min || 1;
    const pixelSize = displaySize / size;
    
    // Draw feature map with viridis-like colormap
    featureMap.forEach((row, y) => {
        row.forEach((val, x) => {
            const normalized = (val - min) / range;
            
            // Viridis approximation (blue -> cyan -> yellow -> orange)
            let r, g, b;
            if (normalized < 0.25) {
                const t = normalized * 4;
                r = Math.floor(68 * t);
                g = Math.floor(1 + 71 * t);
                b = Math.floor(84 + 100 * t);
            } else if (normalized < 0.5) {
                const t = (normalized - 0.25) * 4;
                r = Math.floor(68 + 32 * t);
                g = Math.floor(72 + 61 * t);
                b = Math.floor(184 - 52 * t);
            } else if (normalized < 0.75) {
                const t = (normalized - 0.5) * 4;
                r = Math.floor(100 + 125 * t);
                g = Math.floor(133 + 90 * t);
                b = Math.floor(132 - 98 * t);
            } else {
                const t = (normalized - 0.75) * 4;
                r = Math.floor(225 + 28 * t);
                g = Math.floor(223 - 29 * t);
                b = Math.floor(34 - 2 * t);
            }
            
            ctx.fillStyle = `rgb(${r},${g},${b})`;
            ctx.fillRect(x * pixelSize, y * pixelSize, pixelSize, pixelSize);
        });
    });
    
    return canvas;
}

/**
 * Clear feature map previews
 */
function clearFeatureMapPreviews() {
    const container = document.getElementById('feature-maps-container');
    if (container) {
        container.innerHTML = '';
        container.style.display = 'none';
    }
}

// ==================== INITIALIZATION ====================
function initializeVisualization() {
    if (typeof THREE === 'undefined') {
        console.error('THREE.js not loaded!');
        return;
    }
    
    // Create visualizer instance
    window.cnnVisualizer = new CNNVisualizer3D('visualization-container');
    
    // Initialize with empty/zero state
    window.cnnVisualizer.initializeEmpty();
    
    console.log('MNIST 3D Visualization initialized');
    console.log('API Endpoint:', window.apiEndpoint);
    console.log('THREE.js available:', typeof THREE !== 'undefined');
}
