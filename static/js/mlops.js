/**
 * MLOps Stack Builder Visualization
 * 
 * Interactive visualization tool for building and understanding MLOps stacks.
 * Features:
 * - Interactive graph visualization using Cytoscape.js
 * - Tool selection and information display
 * - Modal-based detailed tool information
 * - Visual feedback for selected components
 * 
 * Graph Structure:
 * - Nodes represent different MLOps components
 * - Edges show relationships and dependencies
 * - Tools can be added to each component
 */

document.addEventListener("DOMContentLoaded", function() {
    let previousNode = null;

    const cy = cytoscape({
        container: document.getElementById('cy'),
        style: [
            {
                selector: 'node',
                style: {
                    'background-color': '#ffffff',
                    'label': 'data(label)',
                    'shape': 'roundrectangle',
                    'text-valign': 'center', 
                    'text-halign': 'center',
                    'width': '170px',
                    'height': '60px',
                    'border-width': '2px',
                    'border-color': '#333333',
                    'font-family': 'Arial',
                    'font-size': '12px',
                    'font-weight': 'bold',
                    'color': '#333333',
                    'text-wrap': 'wrap',
                    'text-margin-y': '0px'
                }
            },
            {
                selector: 'edge',
                style: {
                    'width': 2,
                    'line-color': '#333333',
                    'target-arrow-color': '#333333',
                    'target-arrow-shape': 'triangle',
                    'curve-style': 'bezier'
                }
            }
        ],
        layout: {
            name: 'preset'
        },
        elements: {
            nodes: [
                { data: { id: 'a', label: 'EXPERIMENT TRACKING' }, position: { x: 100, y: 50 } },
                { data: { id: 'b', label: 'EXPERIMENTATION' }, position: { x: 350, y: 50 } },
                { data: { id: 'c', label: 'DATA VERSIONING' }, position: { x: 100, y: 150 } },
                { data: { id: 'd', label: 'CODE VERSIONING' }, position: { x: 350, y: 150 } },
                { data: { id: 'e', label: 'PIPELINE ORCHESTRATION' }, position: { x: 200, y: 250 } },
                { data: { id: 'f', label: 'ARTIFACT TRACKING' }, position: { x: 200, y: 350 } },
                { data: { id: 'g', label: 'MODEL REGISTRY' }, position: { x: 450, y: 250 } },
                { data: { id: 'h', label: 'MODEL SERVING' }, position: { x: 700, y: 250 } },
                { data: { id: 'i', label: 'MODEL MONITORING' }, position: { x: 700, y: 350 } },
                { data: { id: 'j', label: 'RUNTIME ENGINE' }, position: { x: 600, y: 100 } } 
            ],
            edges: [
                { data: { source: 'a', target: 'b' } },
                { data: { source: 'b', target: 'c' } },
                { data: { source: 'b', target: 'd' } },
                { data: { source: 'c', target: 'e' } },
                { data: { source: 'd', target: 'e' } },
                { data: { source: 'e', target: 'f' } },
                { data: { source: 'e', target: 'g' } },
                { data: { source: 'g', target: 'h' } },
                { data: { source: 'h', target: 'i' } }
                
            ]
        }
    });

    cy.on('tap', 'node', function(evt) {
        const node = evt.target;

        if (previousNode) {
            previousNode.animate({
                style: { 'background-color': '#ffffff' }
            }, {
                duration: 500
            });
        }

        node.animate({
            style: { 'background-color': '#ffcc00' }
        }, {
            duration: 500,
            complete: function() {
                previousNode = node;
            }
        });

        updateSidebar(node.data('label'));
    });

    /**
     * Updates the sidebar with information about the selected component
     * @param {string} title - The name of the selected component
     */
    function updateSidebar(title) {
        const sidebarTitle = document.querySelector('.sidebar h5');
        const sidebarContent = document.querySelector('.sidebar');

        sidebarTitle.textContent = title;

        if (title.includes('EXPERIMENT TRACKING')) {
            sidebarContent.innerHTML = `
                <h5>EXPERIMENT TRACKING</h5>
                <p>Experiment Tracking is the practice of managing and documenting your experiments in machine learning projects. It helps in organizing experiments, tracking progress, and ensuring reproducibility.</p>
                
                <div class="tool-buttons">
                    <div class="tool-button" data-tool="MLFlow">
                        <img src="/static/images/mlopsstack/mlflow.png" alt="MLFlow Logo">
                        <span>MLFlow</span>
                    </div>
                    <div class="tool-button" data-tool="CometML">
                        <img src="/static/images/mlopsstack/comet.png" alt="CometML Logo">
                        <span>CometML</span>
                    </div>
                    <div class="tool-button" data-tool="ClearML">
                        <img src="/static/images/mlopsstack/clearml.png" alt="ClearML Logo">
                        <span>ClearML</span>
                    </div>
                    <div class="tool-button" data-tool="DVC">
                        <img src="/static/images/mlopsstack/dvc.png" alt="DVC Logo">
                        <span>DVC</span>
                    </div>
                    <div class="tool-button" data-tool="Neptune">
                        <img src="/static/images/mlopsstack/neptune.webp" alt="Neptune Logo">
                        <span>Neptune</span>
                    </div>
                    <div class="tool-button" data-tool="Polyaxon">
                        <img src="/static/images/mlopsstack/polyaxon.png" alt="Polyaxon Logo">
                        <span>Polyaxon</span>
                    </div>
                    <div class="tool-button" data-tool="WandB">
                        <img src="/static/images/mlopsstack/wandb.png" alt="W&B Logo">
                        <span>W&B</span>
                    </div>
                </div>
            `;
        } else {
            sidebarContent.innerHTML = `
                <h5>${title}</h5>
                <p>Click on a block in the diagram to see more details.</p>`;
        }

        document.querySelectorAll('.tool-button').forEach(function(button) {
            button.addEventListener('click', function() {
                const tool = this.getAttribute('data-tool');
                openToolModal(tool);
            });
        });
    }

    /**
     * Displays detailed information about a selected tool
     * @param {string} tool - The tool identifier
     */
    function openToolModal(tool) {
        const toolInfo = getToolInfo(tool);

        const modalTitle = document.getElementById('toolModalLabel');
        const modalLogo = document.getElementById('toolLogo');
        const modalDescription = document.getElementById('toolDescription');
        const modalAdvantages = document.getElementById('toolAdvantages');
        const modalDisadvantages = document.getElementById('toolDisadvantages');
        const modalLink = document.getElementById('toolLink');
        const addToStackButton = document.getElementById('addToStackButton');

        modalTitle.textContent = toolInfo.name;
        modalLogo.src = toolInfo.logo;
        modalDescription.textContent = toolInfo.description;
        modalAdvantages.innerHTML = toolInfo.advantages.map(adv => `<li>${adv}</li>`).join('');
        modalDisadvantages.innerHTML = toolInfo.disadvantages.map(disadv => `<li>${disadv}</li>`).join('');
        modalLink.textContent = 'Visit Website';
        modalLink.href = toolInfo.link;

        const modalElement = new bootstrap.Modal(document.getElementById('toolModal'));
        modalElement.show();

        addToStackButton.onclick = function() {
            addToolToNode(tool, cy.$(':selected'));
            modalElement.hide();  // Fechar o modal após adicionar a ferramenta
        };
    }

    function addToolToNode(tool, node) {
        if (node) {
            const [title] = node.data('label').split('\n\n');
            const toolLogo = getToolLogo(tool);

            node.data('label', `${title}\n\n${tool}`);
            node.style({
                'background-image': `url(${toolLogo})`,
                'background-fit': 'contain',
                'background-position-x': '10px',
                'background-position-y': 'center',
                'background-clip': 'none',
                'background-width': '30px',
                'background-height': '30px'
            });
        }
    }

    // Tool information definitions
    function getToolInfo(tool) {
        switch(tool) {
            case 'MLFlow':
                return {
                    name: 'MLFlow',
                    logo: '/static/images/mlopsstack/mlflow.png',
                    description: 'MLFlow is an open-source platform for managing the end-to-end machine learning lifecycle.',
                    advantages: ['Supports multiple ML libraries', 'Simplifies tracking of experiments'],
                    disadvantages: ['Can be complex to set up', 'Requires additional infrastructure'],
                    link: 'https://mlflow.org/'
                };
            case 'CometML':
                return {
                    name: 'CometML',
                    logo: '/static/images/mlopsstack/comet.png',
                    description: 'CometML is a machine learning platform that allows you to track, compare, explain, and optimize experiments and models.',
                    advantages: ['Rich tracking features', 'Collaborative features'],
                    disadvantages: ['Paid plans can be expensive', 'Some advanced features may be complex'],
                    link: 'https://www.comet.ml/'
                };
            case 'ClearML':
                return {
                    name: 'ClearML',
                    logo: '/static/images/mlopsstack/clearml.png',
                    description: 'ClearML is an open-source platform that unifies experiment management, data management, and model management.',
                    advantages: ['Integrated with many tools', 'Open-source and free'],
                    disadvantages: ['Learning curve for beginners', 'Requires configuration'],
                    link: 'https://clear.ml/'
                };
            case 'DVC':
                return {
                    name: 'DVC',
                    logo: '/static/images/mlopsstack/dvc.png',
                    description: 'DVC is an open-source version control system for data science and machine learning projects.',
                    advantages: ['Version control for models and data', 'Integrates with Git'],
                    disadvantages: ['Requires understanding of Git', 'Not as intuitive for non-developers'],
                    link: 'https://dvc.org/'
                };
            case 'Neptune':
                return {
                    name: 'Neptune.ai',
                    logo: '/static/images/mlopsstack/neptune.webp',
                    description: 'Neptune.ai is a lightweight experiment management tool that helps you organize and control your experiments.',
                    advantages: ['User-friendly interface', 'Supports multiple frameworks'],
                    disadvantages: ['Limited features in free tier', 'Integration requires setup'],
                    link: 'https://neptune.ai/'
                };
            case 'Polyaxon':
                return {
                    name: 'Polyaxon',
                    logo: '/static/images/mlopsstack/polyaxon.png',
                    description: 'Polyaxon is a platform for reproducible and scalable machine learning and deep learning on Kubernetes.',
                    advantages: ['Scalable on Kubernetes', 'Supports distributed training'],
                    disadvantages: ['Requires Kubernetes knowledge', 'More suitable for advanced users'],
                    link: 'https://polyaxon.com/'
                };
            case 'WandB':
                return {
                    name: 'Weights & Biases',
                    logo: '/static/images/mlopsstack/wandb.png',
                    description: 'Weights & Biases (W&B) is a tool for tracking machine learning experiments, models, and datasets.',
                    advantages: ['Easy to use', 'Comprehensive tracking'],
                    disadvantages: ['Expensive for large teams', 'Can be overwhelming for new users'],
                    link: 'https://wandb.ai/'
                };
            default:
                return {};
        }
    }

    function getToolLogo(tool) {
        return getToolInfo(tool).logo;
    }

    updateSidebar('MLOPs Stack Builder');
});
