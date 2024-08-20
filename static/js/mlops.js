document.addEventListener("DOMContentLoaded", function() {
    const $ = go.GraphObject.make;

    const myDiagram = $(go.Diagram, "diagramDiv", {
        initialContentAlignment: go.Spot.Center,
        "undoManager.isEnabled": true
    });

    myDiagram.nodeTemplate =
        $(go.Node, "Auto",
            { locationSpot: go.Spot.Center },
            $(go.Shape, "RoundedRectangle",
                { strokeWidth: 1, stroke: "#333333", fill: "#ffffff" },
                new go.Binding("fill", "color")),
            $(go.TextBlock,
                { margin: 8, font: "bold 12pt Arial", stroke: "#333333" },
                new go.Binding("text", "key"))
        );

    // Configura o template de link com pontos de origem e destino específicos
    myDiagram.linkTemplate =
        $(go.Link,
            { routing: go.Link.AvoidsNodes, curve: go.Link.JumpOver },
            new go.Binding("fromSpot", "fromSpot", go.Spot.parse),
            new go.Binding("toSpot", "toSpot", go.Spot.parse),
            $(go.Shape, { strokeWidth: 2, stroke: "#333333" }),
            $(go.Shape, { toArrow: "Standard", stroke: "#333333", fill: "#333333" })
        );

    myDiagram.model = new go.GraphLinksModel(
        [
            { key: "EXPERIMENT TRACKING", color: "white", loc: "0 0" },
            { key: "EXPERIMENTATION", color: "white", loc: "250 0" },
            { key: "DATA VERSIONING", color: "white", loc: "0 100" },
            { key: "CODE VERSIONING", color: "white", loc: "250 100" },
            { key: "PIPELINE ORCHESTRATION", color: "white", loc: "250 200" },
            { key: "ARTIFACT TRACKING", color: "white", loc: "250 300" },
            { key: "MODEL REGISTRY", color: "white", loc: "500 200" },
            { key: "MODEL SERVING", color: "white", loc: "700 200" },
            { key: "MODEL MONITORING", color: "white", loc: "700 300" },
            { key: "RUNTIME ENGINE", color: "white", loc: "700 0" }
        ],
        [
            { from: "EXPERIMENT TRACKING", to: "EXPERIMENTATION", fromSpot: "Right", toSpot: "Left" },
            { from: "EXPERIMENTATION", to: "CODE VERSIONING", fromSpot: "Bottom", toSpot: "Top" },
            { from: "EXPERIMENTATION", to: "DATA VERSIONING", fromSpot: "Bottom", toSpot: "Top" },
            { from: "DATA VERSIONING", to: "PIPELINE ORCHESTRATION", fromSpot: "Bottom", toSpot: "Left" },
            { from: "CODE VERSIONING", to: "PIPELINE ORCHESTRATION", fromSpot: "Bottom", toSpot: "Top" },
            { from: "PIPELINE ORCHESTRATION", to: "ARTIFACT TRACKING", fromSpot: "Bottom", toSpot: "Top" },
            { from: "PIPELINE ORCHESTRATION", to: "MODEL REGISTRY", fromSpot: "Right", toSpot: "Left" },
            { from: "MODEL REGISTRY", to: "MODEL SERVING", fromSpot: "Right", toSpot: "Left" },
            { from: "MODEL SERVING", to: "MODEL MONITORING", fromSpot: "Bottom", toSpot: "Top" }
        ]);

    myDiagram.model.nodeDataArray.forEach(function(node) {
        myDiagram.findNodeForKey(node.key).location = go.Point.parse(node.loc);
    });

    myDiagram.addDiagramListener("ObjectSingleClicked", function(e) {
        const part = e.subject.part;
        if (part instanceof go.Node) {
            updateSidebar(part.data.key);
        }
    });

    function updateSidebar(title) {
        const sidebarTitle = document.querySelector('.sidebar h5');
        const sidebarContent = document.querySelector('.sidebar');

        sidebarTitle.textContent = title;

        if (title === 'EXPERIMENT TRACKING') {
            sidebarContent.innerHTML = `
                <h5>EXPERIMENT TRACKING</h5>
                <p>Experiment Tracking is the practice of managing and documenting your experiments in machine learning projects. It helps in organizing experiments, tracking progress, and ensuring reproducibility.</p>
                
                <div class="tool-buttons">
                    <div class="tool-button">
                        <img src="/static/images/mlopsstack/mlflow.png" alt="MLFlow Logo">
                        <span>MLFlow</span>
                    </div>
                    <div class="tool-button">
                        <img src="/static/images/mlopsstack/comet.png" alt="CometML Logo">
                        <span>CometML</span>
                    </div>
                    <div class="tool-button">
                        <img src="/static/images/mlopsstack/clearml.png" alt="ClearML Logo">
                        <span>ClearML</span>
                    </div>
                    <div class="tool-button">
                        <img src="/static/images/mlopsstack/dvc.png" alt="DVC Logo">
                        <span>DVC</span>
                    </div>
                    <div class="tool-button">
                        <img src="/static/images/mlopsstack/neptune.webp" alt="Neptune Logo">
                        <span>Neptune</span>
                    </div>
                    <div class="tool-button">
                        <img src="/static/images/mlopsstack/polyaxon.png" alt="Polyaxon Logo">
                        <span>Polyaxon</span>
                    </div>
                    <div class="tool-button">
                        <img src="/static/images/mlopsstack/wandb.png" alt="W&B Logo">
                        <span>W&B</span>
                    </div>
                </div>
            `;
        } else {
            sidebarContent.innerHTML = `
                <h5>${title}</h5>
                <p>Click on a block in the diagram to see more details.</p>
            `;
        }
    }

    // Inicializa a barra lateral com uma mensagem padrão
    updateSidebar('MLOPs Stack Builder');
});
