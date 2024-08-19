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

    myDiagram.linkTemplate =
        $(go.Link,
            { routing: go.Link.AvoidsNodes, curve: go.Link.JumpOver },
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
            { key: "RUNTIME ENGINE", color: "white", loc: "700 0" } // Desconectado, apenas posicionado
        ],
        [
            { from: "EXPERIMENT TRACKING", to: "EXPERIMENTATION" },
            { from: "EXPERIMENTATION", to: "CODE VERSIONING" },
            { from: "EXPERIMENTATION", to: "DATA VERSIONING" },
            { from: "DATA VERSIONING", to: "PIPELINE ORCHESTRATION" },
            { from: "CODE VERSIONING", to: "PIPELINE ORCHESTRATION" },
            { from: "PIPELINE ORCHESTRATION", to: "ARTIFACT TRACKING" },
            { from: "PIPELINE ORCHESTRATION", to: "MODEL REGISTRY" },
            { from: "MODEL REGISTRY", to: "MODEL SERVING" },
            { from: "MODEL SERVING", to: "MODEL MONITORING" }
            // "RUNTIME ENGINE" removido das conexões
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
        const sidebarContent = document.querySelector('.sidebar p');

        if (!sidebarTitle || !sidebarContent) {
            console.error('Elementos da barra lateral não encontrados!');
            return;
        }

        sidebarTitle.textContent = title;

        if (title === 'EXPERIMENT TRACKING') {
            sidebarContent.innerHTML = `
                <div>
                    <h6>Available Tools:</h6>
                    <ul>
                        <li><a href="#">MLFlow</a></li>
                        <li><a href="#">CometML</a></li>
                    </ul>
                </div>
            `;
        } else {
            sidebarContent.innerHTML = '<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>';
        }
    }
});
