document.addEventListener("DOMContentLoaded", function() {
    const { dia, shapes } = joint;

    const paperContainer = document.getElementById("diagram");

    if (!paperContainer) {
        console.error("O elemento #diagram não foi encontrado na página.");
        return;
    }

    const graph = new dia.Graph({}, { cellNamespace: shapes });
    const paper = new dia.Paper({
        model: graph,
        cellViewNamespace: shapes,
        width: "100%",
        height: 600,
        gridSize: 10,
        async: true,
        frozen: true,
        sorting: dia.Paper.sorting.APPROX,
        background: { color: "#f8f9fa" },
        clickThreshold: 10,
        defaultConnector: {
            name: "rounded"  // Conector padrão, sem curvas exageradas
        },
        defaultLink: new shapes.standard.Link({
            attrs: {
                line: {
                    stroke: '#333333',
                    strokeWidth: 2,
                    targetMarker: {
                        'type': 'path',
                        'd': 'M 10 -5 0 0 10 5 Z', // Seta ao final da linha
                        'stroke': '#333333',
                        'fill': '#333333'
                    }
                }
            }
        })
    });

    paperContainer.appendChild(paper.el);

    // Função para criar os elementos (caixas)
    function createElement(label, x, y) {
        return new shapes.standard.Rectangle({
            position: { x, y },
            size: { width: 150, height: 60 },
            attrs: {
                body: {
                    fill: '#ffffff',
                    stroke: '#333333',
                    rx: 5,
                    ry: 5,
                    'stroke-width': 1
                },
                label: {
                    text: label,
                    fill: '#333333',
                    fontFamily: 'Arial',
                    fontSize: 12,
                    fontWeight: 'bold'
                }
            }
        });
    }

    // Função para criar as conexões (links)
    function createLink(source, target, dashed = false) {
        return new shapes.standard.Link({
            source: { id: source.id },
            target: { id: target.id },
            connector: { name: 'rounded' },
            attrs: {
                line: {
                    stroke: '#333333',
                    strokeWidth: 2,
                    strokeDasharray: dashed ? '5 5' : '0',
                    targetMarker: {
                        'type': 'path',
                        'd': 'M 10 -5 0 0 10 5 Z',
                        'stroke': '#333333',
                        'fill': '#333333'
                    }
                }
            }
        });
    }

    // Criar os três elementos (caixas)
    const experimentTracking = createElement('EXPERIMENT TRACKING', 50, 50);
    const experimentation = createElement('EXPERIMENTATION', 250, 50);
    const dataVersioning = createElement('DATA VERSIONING', 150, 150);

    // Adicionar os elementos ao gráfico
    graph.addCells([experimentTracking, experimentation, dataVersioning]);

    // Criar e adicionar as conexões entre os elementos
    const link1 = createLink(experimentTracking, experimentation, false);
    const link2 = createLink(experimentation, dataVersioning, false);  // Conectando Experimentation com Data Versioning
    const link3 = createLink(dataVersioning, experimentation, false).set('connector', { name: 'rounded', args: { startDirections: ['top'], endDirections: ['bottom'] } });  // Conectando Data Versioning com a parte de baixo de Experimentation

    graph.addCells([link1, link2, link3]);

    paper.unfreeze();
});
