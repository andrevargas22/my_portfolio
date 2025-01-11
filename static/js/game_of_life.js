/**
 * Conway's Game of Life Implementation
 * 
 * This is an interactive implementation of Conway's Game of Life cellular automaton.
 * The game runs on a canvas element with the following features:
 * - Click and drag to draw/erase cells
 * - Responsive grid that adapts to screen size
 * - Controls for starting, stopping, clearing, and randomizing the grid
 * 
 * Rules of the Game:
 * 1. Any live cell with 2-3 live neighbors survives
 * 2. Any dead cell with exactly 3 live neighbors becomes alive
 * 3. All other cells die or stay dead
 * 
 * Implementation Details:
 * - Uses HTML5 Canvas for rendering
 * - Maintains 16:9 aspect ratio
 * - Supports window resizing while preserving pattern
 * - Grid wraps around edges (toroidal array)
 * - Drawing interface supports both adding and erasing cells
 */

class GameOfLife {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.cells = [];
        this.isRunning = false;
        this.interval = null;
        this.isDrawing = false;
        this.isErasing = false;
        
        // Add resize handler
        window.addEventListener('resize', () => this.handleResize());
        
        // Mouse event handlers for drawing
        this.canvas.addEventListener('mousedown', (e) => this.handleMouse(e));
        this.canvas.addEventListener('mousemove', (e) => this.isDrawing && this.handleMouse(e));
        this.canvas.addEventListener('mouseup', () => this.isDrawing = false);
        this.canvas.addEventListener('mouseleave', () => this.isDrawing = false);
        
        // Initial setup
        this.setupCanvas();
    }

    setupCanvas() {
        // Get container width
        const container = this.canvas.parentElement;
        const containerWidth = container.clientWidth;
        
        // Set canvas size maintaining 16:9 aspect ratio
        this.canvas.style.width = '100%';
        this.canvas.style.height = 'auto';
        this.canvas.width = containerWidth;
        this.canvas.height = containerWidth * 0.5625; // 16:9 aspect ratio
        
        // Adjust cell size based on canvas width
        this.cellSize = Math.floor(this.canvas.width / 50); // Aim for about 50 cells across
        
        // Calculate grid dimensions
        this.cols = Math.floor(this.canvas.width / this.cellSize);
        this.rows = Math.floor(this.canvas.height / this.cellSize);
        
        // Initialize or resize grid
        this.initializeGrid();
        this.draw();
    }

    handleResize() {
        const oldCells = this.cells;
        this.setupCanvas();
        
        // Preserve existing pattern as much as possible
        const minRows = Math.min(oldCells.length, this.rows);
        const minCols = Math.min(oldCells[0].length, this.cols);
        
        for (let row = 0; row < minRows; row++) {
            for (let col = 0; col < minCols; col++) {
                this.cells[row][col] = oldCells[row][col];
            }
        }
        this.draw();
    }

    initializeGrid() {
        this.cells = Array(this.rows).fill().map(() => Array(this.cols).fill(0));
    }

    handleMouse(event) {
        const rect = this.canvas.getBoundingClientRect();
        const scaleX = this.canvas.width / rect.width;
        const scaleY = this.canvas.height / rect.height;
        
        const x = (event.clientX - rect.left) * scaleX;
        const y = (event.clientY - rect.top) * scaleY;
        
        const col = Math.floor(x / this.cellSize);
        const row = Math.floor(y / this.cellSize);
        
        if (row >= 0 && row < this.rows && col >= 0 && col < this.cols) {
            if (event.type === 'mousedown') {
                this.isDrawing = true;
                // Determine if we're erasing based on initial cell state
                this.isErasing = this.cells[row][col] === 1;
            }
            // Set cell based on whether we're erasing or drawing
            this.cells[row][col] = this.isErasing ? 0 : 1;
            this.draw();
        }
    }

    randomize() {
        this.cells = this.cells.map(row => row.map(() => Math.random() > 0.7 ? 1 : 0));
        this.draw();
    }

    countNeighbors(row, col) {
        let count = 0;
        for (let i = -1; i <= 1; i++) {
            for (let j = -1; j <= 1; j++) {
                if (i === 0 && j === 0) continue;
                const r = (row + i + this.rows) % this.rows;
                const c = (col + j + this.cols) % this.cols;
                count += this.cells[r][c];
            }
        }
        return count;
    }

    nextGeneration() {
        const newCells = Array(this.rows).fill().map(() => Array(this.cols).fill(0));
        
        for (let row = 0; row < this.rows; row++) {
            for (let col = 0; col < this.cols; col++) {
                const neighbors = this.countNeighbors(row, col);
                if (this.cells[row][col]) {
                    newCells[row][col] = (neighbors === 2 || neighbors === 3) ? 1 : 0;
                } else {
                    newCells[row][col] = neighbors === 3 ? 1 : 0;
                }
            }
        }
        this.cells = newCells;
    }

    draw() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        for (let row = 0; row < this.rows; row++) {
            for (let col = 0; col < this.cols; col++) {
                const x = col * this.cellSize;
                const y = row * this.cellSize;
                
                this.ctx.strokeStyle = '#ddd';
                this.ctx.strokeRect(x, y, this.cellSize, this.cellSize);
                
                if (this.cells[row][col]) {
                    this.ctx.fillStyle = '#333';
                    this.ctx.fillRect(x, y, this.cellSize, this.cellSize);
                }
            }
        }
    }

    start() {
        if (!this.isRunning) {
            this.isRunning = true;
            this.interval = setInterval(() => {
                this.nextGeneration();
                this.draw();
            }, 100);
        }
    }

    stop() {
        this.isRunning = false;
        if (this.interval) {
            clearInterval(this.interval);
            this.interval = null;
        }
    }

    clear() {
        this.stop();
        this.initializeGrid();
        this.draw();
    }
}

// Initialize game when document is ready
document.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById('gameCanvas');
    const game = new GameOfLife(canvas);
    game.draw();

    document.getElementById('startBtn').addEventListener('click', () => game.start());
    document.getElementById('stopBtn').addEventListener('click', () => game.stop());
    document.getElementById('clearBtn').addEventListener('click', () => game.clear());
    document.getElementById('randomBtn').addEventListener('click', () => game.randomize());
});
