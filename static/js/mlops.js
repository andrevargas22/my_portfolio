document.addEventListener("DOMContentLoaded", function() {
    let previousNode = null; // Para armazenar o nó previamente selecionado

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
                    'text-margin-y': '0px' // Ajuste para elevar o texto
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
                { data: { id: 'b', label: 'EXPERIMENTATION' }, position: { x: 300, y: 50 } },
                { data: { id: 'c', label: 'DATA VERSIONING' }, position: { x: 100, y: 150 } },
                { data: { id: 'd', label: 'CODE VERSIONING' }, position: { x: 300, y: 150 } },
                { data: { id: 'e', label: 'PIPELINE ORCHESTRATION' }, position: { x: 200, y: 250 } },
                { data: { id: 'f', label: 'ARTIFACT TRACKING' }, position: { x: 200, y: 350 } },
                { data: { id: 'g', label: 'MODEL REGISTRY' }, position: { x: 500, y: 250 } },
                { data: { id: 'h', label: 'MODEL SERVING' }, position: { x: 700, y: 250 } },
                { data: { id: 'i', label: 'MODEL MONITORING' }, position: { x: 700, y: 350 } },
                { data: { id: 'j', label: 'RUNTIME ENGINE' }, position: { x: 700, y: 50 } }
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
                { data: { source: 'h', target: 'i' } },
                { data: { source: 'j', target: 'h' } }
            ]
        }
    });

    cy.on('tap', 'node', function(evt) {
        const node = evt.target;

        // Se houver um nó previamente selecionado, remove a cor de fundo
        if (previousNode) {
            previousNode.animate({
                style: { 'background-color': '#ffffff' }
            }, {
                duration: 500 // Duração de 0.5 segundos para desfazer a animação
            });
        }

        // Atualiza a cor de fundo do nó atual
        node.animate({
            style: { 'background-color': '#ffcc00' } // Cor amarela
        }, {
            duration: 500, // Duração de 0.5 segundos para a animação de destaque
            complete: function() {
                previousNode = node; // Atualiza o nó previamente selecionado
            }
        });

        updateSidebar(node.data('label'));
    });

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
                addToolToNode(tool);
            });
        });
    }

    function addToolToNode(tool) {
        const selectedNode = cy.$(':selected');
        if (selectedNode) {
            const [title] = selectedNode.data('label').split('\n\n'); // Pega o título original
            const toolLogo = getToolLogo(tool); // Função para obter a URL da logo da ferramenta

            // Atualiza o rótulo do nó com o nome da ferramenta
            selectedNode.data('label', `${title}\n\n${tool}`);

            // Adiciona a imagem como background do nó
            selectedNode.style({
                'background-image': `url(${toolLogo})`,
                'background-fit': 'contain',
                'background-position-x': '10px', // Ajusta a posição horizontal da imagem
                'background-position-y': 'center', // Centraliza verticalmente
                'background-clip': 'none',
                'background-width': '30px', // Define a largura da imagem
                'background-height': '30px' // Define a altura da imagem
            });
        }
    }

    function getToolLogo(tool) {
        switch(tool) {
            case 'MLFlow':
                return '/static/images/mlopsstack/mlflow.png';
            case 'CometML':
                return '/static/images/mlopsstack/comet.png';
            case 'ClearML':
                return '/static/images/mlopsstack/clearml.png';
            case 'DVC':
                return '/static/images/mlopsstack/dvc.png';
            case 'Neptune':
                return '/static/images/mlopsstack/neptune.webp';
            case 'Polyaxon':
                return '/static/images/mlopsstack/polyaxon.png';
            case 'WandB':
                return '/static/images/mlopsstack/wandb.png';
            default:
                return '';
        }
    }

    updateSidebar('MLOPs Stack Builder');
});
