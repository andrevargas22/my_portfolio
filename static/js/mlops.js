document.addEventListener("DOMContentLoaded", function () {
    const experimentTrackingBlock = document.getElementById('experiment-tracking');
    const sidebar = document.getElementById('sidebar');
    const infoModal = document.getElementById('infoModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');
    const modalLogo = document.getElementById('modalLogo');
    const addToStackBtn = document.getElementById('addToStackBtn');
    let selectedTool = '';

    function setModalContent(toolName, logoSrc, description) {
        selectedTool = toolName;
        modalTitle.textContent = selectedTool;
        modalLogo.src = logoSrc;
        modalBody.innerHTML = description;
        infoModal.style.display = 'block';
    }

    document.getElementById('mlflowButton').addEventListener('click', function() {
        setModalContent(
            'MLFlow',
            '/static/images/mlopsstack/mlflow.png',
            `<p><strong>MLFlow</strong> is an open-source platform to manage the ML lifecycle, including experimentation, reproducibility, and deployment.</p>
            <p><strong>Advantages:</strong> Scalable, integrates with many tools, strong community support.</p>
            <p><strong>Disadvantages:</strong> Requires setup and infrastructure, may have a steep learning curve for beginners.</p>
            <p><a href="https://mlflow.org" target="_blank">Visit MLFlow website</a></p>`
        );
    });

    document.getElementById('cometmlButton').addEventListener('click', function() {
        setModalContent(
            'CometML',
            '/static/images/mlopsstack/comet.png',
            `<p><strong>CometML</strong> is a meta machine learning platform that allows data scientists and engineers to track, compare, explain, and optimize experiments and models across the model's entire lifecycle.</p>
            <p><strong>Advantages:</strong> User-friendly, cloud-based, integrates with popular ML libraries.</p>
            <p><strong>Disadvantages:</strong> May incur costs for extensive use, limited offline capabilities.</p>
            <p><a href="https://www.comet.ml" target="_blank">Visit CometML website</a></p>`
        );
    });

    document.getElementById('dvcButton').addEventListener('click', function() {
        setModalContent(
            'DVC',
            '/static/images/mlopsstack/dvc.png',
            `<p><strong>DVC (Data Version Control)</strong> is a version control system for machine learning projects that tracks data files and models.</p>
            <p><strong>Advantages:</strong> Integrates with Git, easy data and model versioning, scalable.</p>
            <p><strong>Disadvantages:</strong> Learning curve for non-Git users, requires additional setup.</p>
            <p><a href="https://dvc.org/" target="_blank">Visit DVC website</a></p>`
        );
    });

    document.getElementById('clearmlButton').addEventListener('click', function() {
        setModalContent(
            'ClearML',
            '/static/images/mlopsstack/clearml.png',
            `<p><strong>ClearML</strong> is an open-source platform for experiment tracking, orchestrating, and automating machine learning pipelines.</p>
            <p><strong>Advantages:</strong> Open-source, flexible, integrates with many frameworks.</p>
            <p><strong>Disadvantages:</strong> Setup complexity, requires understanding of pipeline management.</p>
            <p><a href="https://clear.ml/" target="_blank">Visit ClearML website</a></p>`
        );
    });

    document.getElementById('wandbButton').addEventListener('click', function() {
        setModalContent(
            'Weights & Biases (W&B)',
            '/static/images/mlopsstack/wandb.png',
            `<p><strong>Weights & Biases (W&B)</strong> is a tool for tracking machine learning experiments and visualizing metrics in real-time.</p>
            <p><strong>Advantages:</strong> User-friendly interface, integrates with many ML frameworks, collaborative.</p>
            <p><strong>Disadvantages:</strong> Advanced features require payment, requires account creation.</p>
            <p><a href="https://wandb.ai" target="_blank">Visit W&B website</a></p>`
        );
    });

    document.getElementById('neptuneButton').addEventListener('click', function() {
        setModalContent(
            'Neptune.ai',
            '/static/images/mlopsstack/neptune.webp',
            `<p><strong>Neptune.ai</strong> is a platform for experiment tracking and model management, designed for data scientists and ML engineers.</p>
            <p><strong>Advantages:</strong> Real-time metrics tracking, integrates with multiple ML frameworks, flexible.</p>
            <p><strong>Disadvantages:</strong> Some features are paid, requires learning for advanced use cases.</p>
            <p><a href="https://neptune.ai" target="_blank">Visit Neptune.ai website</a></p>`
        );
    });

    document.getElementById('polyaxonButton').addEventListener('click', function() {
        setModalContent(
            'Polyaxon',
            '/static/images/mlopsstack/polyaxon.png',
            `<p><strong>Polyaxon</strong> is an open-source platform for managing and monitoring machine learning experiments, designed for cloud and on-premises deployment.</p>
            <p><strong>Advantages:</strong> Great for Kubernetes environments, highly customizable, supports large-scale workflows.</p>
            <p><strong>Disadvantages:</strong> Setup complexity, may require substantial resources for large deployments.</p>
            <p><a href="https://polyaxon.com" target="_blank">Visit Polyaxon website</a></p>`
        );
    });

    // Add selected tool to the stack
    addToStackBtn.addEventListener('click', function() {
        const userSelectionDiv = experimentTrackingBlock.querySelector('.user-selection');
        userSelectionDiv.innerHTML = `
            <div class="stack-item">
                <img src="${modalLogo.src}" alt="${selectedTool} Logo">
                <span>${selectedTool}</span>
            </div>
        `;
        infoModal.style.display = 'none';
    });

    // Close the modal
    document.querySelector('.close').addEventListener('click', function() {
        infoModal.style.display = 'none';
    });

    window.addEventListener('click', function(event) {
        if (event.target == infoModal) {
            infoModal.style.display = 'none';
        }
    });
});
