# My Portfolio Website

Source code for my personal website showcasing projects, blog posts, and interactive demos.

## Tech Stack

**Backend:** Flask (Python 3.10)
**Frontend:** HTML5, CSS3, JavaScript (ES6+), Three.js
**Infrastructure:** Docker, Google Cloud Run
**APIs:** Custom MNIST Classifier API, Medium RSS, Mapbox

## Projects

- **MNIST 3D Visualization**: Real-time 3D visualization of CNN activations using Three.js
- **Travel Map**: Interactive world map with Mapbox integration
- **Game of Life**: Conway's Game of Life implementation
- **Games Archive**: Filterable gallery of completed video games

## Environment Variables

```env
MNIST_ENDPOINT=<mnist_api_url>
MAPBOX_ACCESS_TOKEN=<mapbox_token>
WEBHOOK_HMAC_SECRET=<webhook_secret>
```

## Development

```bash
make debug  # Run local server with hot reload
```

## Production

Live at: [andrevargas.com.br](https://andrevargas.com.br)
