// PolicyEdgeAI Frontend Application

// API Configuration
const API_URL = 'http://localhost:8000';

// DOM Elements
const navigationLinks = document.querySelectorAll('nav a');
const pages = document.querySelectorAll('.page');

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    // Initialize navigation
    initNavigation();
    
    // Initialize page-specific functionality
    initDashboard();
    initControlsPage();
    initMappingPage();
    initAnalysisPage();
    initUploadPage();
});

// Navigation Functionality
function initNavigation() {
    navigationLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Remove active class from all links
            navigationLinks.forEach(navLink => {
                navLink.classList.remove('active');
            });
            
            // Add active class to clicked link
            link.classList.add('active');
            
            // Show the corresponding page
            const pageId = link.getAttribute('data-page');
            pages.forEach(page => {
                page.classList.remove('active');
                if (page.id === pageId) {
                    page.classList.add('active');
                }
            });
        });
    });
}

// Dashboard Page
function initDashboard() {
    // Fetch dashboard stats
    fetchDashboardStats();
    
    // Add some demo activity items
    addActivityItem('Application initialized');
}

async function fetchDashboardStats() {
    try {
        // Fetch controls to calculate stats
        const response = await fetch(`${API_URL}/controls/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({})
        });
        
        if (!response.ok) {
            throw new Error('Failed to fetch controls');
        }
        
        const controls = await response.json();
        
        // Calculate dashboard stats
        const totalControls = controls.length;
        
        // Count unique frameworks
        const frameworks = new Set();
        controls.forEach(control => {
            frameworks.add(control.framework);
        });
        
        // Count mappings
        let totalMappings = 0;
        controls.forEach(control => {
            totalMappings += control.mapped_to.length;
        });
        
        // Update dashboard stats
        document.getElementById('total-controls').textContent = totalControls;
        document.getElementById('total-frameworks').textContent = frameworks.size;
        document.getElementById('total-mappings').textContent = totalMappings;
        
        // Add activity item
        addActivityItem(`Loaded ${totalControls} controls from ${frameworks.size} frameworks`);
        
    } catch (error) {
        console.error('Error fetching dashboard stats:', error);
        addActivityItem(`Error: ${error.message}`, 'error');
    }
}

function addActivityItem(description, type = 'info') {
    const activityList = document.getElementById('recent-activity');
    const activityItem = document.createElement('li');
    activityItem.className = `activity-item ${type}`;
    
    const timeSpan = document.createElement('span');
    timeSpan.className = 'activity-time';
    timeSpan.textContent = getCurrentTime();
    
    const descSpan = document.createElement('span');
    descSpan.className = 'activity-desc';
    descSpan.textContent = description;
    
    activityItem.appendChild(timeSpan);
    activityItem.appendChild(descSpan);
    
    // Add to the beginning of the list
    if (activityList.firstChild) {
        activityList.insertBefore(activityItem, activityList.firstChild);
    } else {
        activityList.appendChild(activityItem);
    }
}

function getCurrentTime() {
    const now = new Date();
    const hours = now.getHours().toString().padStart(2, '0');
    const minutes = now.getMinutes().toString().padStart(2, '0');
    return `${hours}:${minutes}`;
}

// Controls Page
function initControlsPage() {
    const searchButton = document.getElementById('search-controls');
    const frameworkFilter = document.getElementById('framework-filter');
    const familyFilter = document.getElementById('family-filter');
    const keywordSearch = document.getElementById('keyword-search');
    
    // Load control families for the selected framework
    frameworkFilter.addEventListener('change', () => {
        loadControlFamilies(frameworkFilter.value);
    });
    
    // Search controls when button is clicked
    searchButton.addEventListener('click', () => {
        searchControls();
    });
    
    // Also search when Enter key is pressed in the search box
    keywordSearch.addEventListener('keyup', (e) => {
        if (e.key === 'Enter') {
            searchControls();
        }
    });
    
    // Initialize by loading all controls
    searchControls();
}

async function loadControlFamilies(framework) {
    try {
        const familyFilter = document.getElementById('family-filter');
        
        // Clear existing options
        familyFilter.innerHTML = '<option value="">All Families</option>';
        
        if (!framework) {
            return;
        }
        
        // Fetch controls for the selected framework
        const response = await fetch(`${API_URL}/controls/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                framework: framework
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to fetch controls');
        }
        
        const controls = await response.json();
        
        // Extract unique families
        const families = new Set();
        controls.forEach(control => {
            if (control.family) {
                families.add(control.family);
            }
        });
        
        // Add family options
        families.forEach(family => {
            const option = document.createElement('option');
            option.value = family;
            option.textContent = family;
            familyFilter.appendChild(option);
        });
        
    } catch (error) {
        console.error('Error loading control families:', error);
        addActivityItem(`Error: ${error.message}`, 'error');
    }
}

async function searchControls() {
    try {
        const frameworkFilter = document.getElementById('framework-filter');
        const familyFilter = document.getElementById('family-filter');
        const keywordSearch = document.getElementById('keyword-search');
        const controlsList = document.getElementById('controls-list');
        
        // Show loading state
        controlsList.innerHTML = '<tr><td colspan="5">Loading controls...</td></tr>';
        
        // Prepare search request
        const searchRequest = {
            framework: frameworkFilter.value,
            family: familyFilter.value,
            keyword: keywordSearch.value
        };
        
        // Fetch controls
        const response = await fetch(`${API_URL}/controls/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(searchRequest)
        });
        
        if (!response.ok) {
            throw new Error('Failed to fetch controls');
        }
        
        const controls = await response.json();
        
        // Clear existing controls
        controlsList.innerHTML = '';
        
        if (controls.length === 0) {
            controlsList.innerHTML = '<tr><td colspan="5">No controls found</td></tr>';
            return;
        }
        
        // Add controls to the table
        controls.forEach(control => {
            const row = document.createElement('tr');
            
            const idCell = document.createElement('td');
            idCell.textContent = control.id;
            
            const titleCell = document.createElement('td');
            titleCell.textContent = control.title;
            
            const frameworkCell = document.createElement('td');
            frameworkCell.textContent = control.framework;
            
            const familyCell = document.createElement('td');
            familyCell.textContent = control.family || '-';
            
            const actionsCell = document.createElement('td');
            const viewButton = document.createElement('button');
            viewButton.className = 'btn btn-primary';
            viewButton.textContent = 'View';
            viewButton.addEventListener('click', () => {
                showControlDetails(control);
            });
            actionsCell.appendChild(viewButton);
            
            row.appendChild(idCell);
            row.appendChild(titleCell);
            row.appendChild(frameworkCell);
            row.appendChild(familyCell);
            row.appendChild(actionsCell);
            
            controlsList.appendChild(row);
        });
        
        // Add activity item
        addActivityItem(`Found ${controls.length} controls matching search criteria`);
        
    } catch (error) {
        console.error('Error searching controls:', error);
        addActivityItem(`Error: ${error.message}`, 'error');
    }
}

function showControlDetails(control) {
    const modal = document.getElementById('control-modal');
    const controlId = document.getElementById('modal-control-id');
    const controlTitle = document.getElementById('modal-control-title');
    const controlFramework = document.getElementById('modal-control-framework');
    const controlFamily = document.getElementById('modal-control-family');
    const controlSource = document.getElementById('modal-control-source');
    const controlDescription = document.getElementById('modal-control-description');
    const controlMappings = document.getElementById('modal-control-mappings');
    
    // Set control details
    controlId.textContent = control.id;
    controlTitle.textContent = control.title;
    controlFramework.textContent = control.framework;
    controlFamily.textContent = control.family || '-';
    controlSource.textContent = control.source;
    controlDescription.textContent = control.description;
    
    // Set control mappings
    controlMappings.innerHTML = '';
    if (control.mapped_to && control.mapped_to.length > 0) {
        control.mapped_to.forEach(mapping => {
            const mappingItem = document.createElement('li');
            mappingItem.textContent = `${mapping.framework}: ${mapping.control_ids ? mapping.control_ids.join(', ') : '-'}`;
            controlMappings.appendChild(mappingItem);
        });
    } else {
        const noMappings = document.createElement('li');
        noMappings.textContent = 'No mappings found';
        controlMappings.appendChild(noMappings);
    }
    
    // Show the modal
    modal.style.display = 'block';
    
    // Set up close button
    const closeButton = modal.querySelector('.close');
    closeButton.addEventListener('click', () => {
        modal.style.display = 'none';
    });
    
    // Close modal when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
}

// Mapping Page
function initMappingPage() {
    const sourceFramework = document.getElementById('source-framework');
    const targetFramework = document.getElementById('target-framework');
    
    // Load controls when framework selection changes
    sourceFramework.addEventListener('change', () => {
        loadFrameworkControls(sourceFramework.value, 'source-controls');
    });
    
    targetFramework.addEventListener('change', () => {
        loadFrameworkControls(targetFramework.value, 'target-controls');
    });
    
    // Initialize with default selections
    loadFrameworkControls(sourceFramework.value, 'source-controls');
    loadFrameworkControls(targetFramework.value, 'target-controls');
    
    // Set up mapping buttons
    const createMappingButton = document.getElementById('create-mapping');
    createMappingButton.addEventListener('click', createMapping);
    
    const removeMappingButton = document.getElementById('remove-mapping');
    removeMappingButton.addEventListener('click', removeMapping);
}

async function loadFrameworkControls(framework, containerId) {
    try {
        const controlsContainer = document.getElementById(containerId);
        
        // Show loading
        controlsContainer.innerHTML = '<div class="controls-placeholder">Loading controls...</div>';
        
        // Fetch controls for the framework
        const response = await fetch(`${API_URL}/controls/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                framework: framework
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to fetch controls');
        }
        
        const controls = await response.json();
        
        // Clear container
        controlsContainer.innerHTML = '';
        
        if (controls.length === 0) {
            controlsContainer.innerHTML = '<div class="controls-placeholder">No controls found</div>';
            return;
        }
        
        // Create a list of controls
        const controlsList = document.createElement('ul');
        controlsList.className = 'selectable-controls';
        
        controls.forEach(control => {
            const controlItem = document.createElement('li');
            controlItem.className = 'control-item';
            controlItem.setAttribute('data-id', control.id);
            controlItem.textContent = `${control.id}: ${control.title}`;
            
            // Make controls selectable
            controlItem.addEventListener('click', () => {
                // Toggle selection
                controlItem.classList.toggle('selected');
            });
            
            controlsList.appendChild(controlItem);
        });
        
        controlsContainer.appendChild(controlsList);
        
    } catch (error) {
        console.error(`Error loading ${framework} controls:`, error);
        addActivityItem(`Error: ${error.message}`, 'error');
    }
}

function createMapping() {
    // Get selected controls
    const sourceControls = getSelectedControls('source-controls');
    const targetControls = getSelectedControls('target-controls');
    
    if (sourceControls.length === 0 || targetControls.length === 0) {
        alert('Please select at least one control from each framework');
        return;
    }
    
    // In a real application, this would send a request to create mappings
    // For demo purposes, just show a message
    alert(`Created mapping between ${sourceControls.join(', ')} and ${targetControls.join(', ')}`);
    addActivityItem(`Created mapping between ${sourceControls.length} source and ${targetControls.length} target controls`);
}

function removeMapping() {
    // Get selected controls
    const sourceControls = getSelectedControls('source-controls');
    const targetControls = getSelectedControls('target-controls');
    
    if (sourceControls.length === 0 || targetControls.length === 0) {
        alert('Please select at least one control from each framework');
        return;
    }
    
    // In a real application, this would send a request to remove mappings
    // For demo purposes, just show a message
    alert(`Removed mapping between ${sourceControls.join(', ')} and ${targetControls.join(', ')}`);
    addActivityItem(`Removed mapping between ${sourceControls.length} source and ${targetControls.length} target controls`);
}

function getSelectedControls(containerId) {
    const container = document.getElementById(containerId);
    const selectedControls = container.querySelectorAll('.control-item.selected');
    
    return Array.from(selectedControls).map(control => control.getAttribute('data-id'));
}

// Analysis Page
function initAnalysisPage() {
    const runAnalysisButton = document.getElementById('run-analysis');
    runAnalysisButton.addEventListener('click', runGapAnalysis);
}

async function runGapAnalysis() {
    try {
        const framework1 = document.getElementById('analysis-framework1').value;
        const framework2 = document.getElementById('analysis-framework2').value;
        
        if (framework1 === framework2) {
            alert('Please select different frameworks for comparison');
            return;
        }
        
        // Show loading state
        document.getElementById('framework1-count').textContent = 'Loading...';
        document.getElementById('framework2-count').textContent = 'Loading...';
        document.getElementById('unmapped-count').textContent = 'Loading...';
        document.getElementById('gap-percentage').textContent = 'Loading...';
        document.getElementById('unmapped-list').innerHTML = '<tr><td colspan="3">Loading...</td></tr>';
        document.getElementById('summary-container').innerHTML = '<p>Generating summary...</p>';
        
        // Fetch gap analysis
        const response = await fetch(`${API_URL}/analysis/gap`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                framework1: framework1,
                framework2: framework2
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to perform gap analysis');
        }
        
        const result = await response.json();
        
        // Update analysis results
        document.getElementById('framework1-count').textContent = result.total_controls_framework1;
        document.getElementById('framework2-count').textContent = result.total_controls_framework2;
        document.getElementById('unmapped-count').textContent = result.unmapped_controls.length;
        document.getElementById('gap-percentage').textContent = `${result.gap_percentage.toFixed(1)}%`;
        
        // Update unmapped controls table
        const unmappedList = document.getElementById('unmapped-list');
        unmappedList.innerHTML = '';
        
        if (result.unmapped_controls.length === 0) {
            unmappedList.innerHTML = '<tr><td colspan="3">No unmapped controls found</td></tr>';
        } else {
            result.unmapped_controls.forEach(control => {
                const row = document.createElement('tr');
                
                const idCell = document.createElement('td');
                idCell.textContent = control.id;
                
                const titleCell = document.createElement('td');
                titleCell.textContent = control.title;
                
                const familyCell = document.createElement('td');
                familyCell.textContent = control.family || '-';
                
                row.appendChild(idCell);
                row.appendChild(titleCell);
                row.appendChild(familyCell);
                
                unmappedList.appendChild(row);
            });
        }
        
        // Generate summary
        generateSummary(framework1, framework2, result);
        
        // Add activity item
        addActivityItem(`Completed gap analysis between ${framework1} and ${framework2}`);
        
    } catch (error) {
        console.error('Error performing gap analysis:', error);
        addActivityItem(`Error: ${error.message}`, 'error');
    }
}

async function generateSummary(framework1, framework2, gapResult) {
    try {
        // Get unmapped control IDs for the search
        const unmappedIds = gapResult.unmapped_controls.map(control => control.id);
        
        // In a real implementation, this would request an AI-generated summary
        // For demo purposes, create a simple summary
        const summaryText = `
            <h4>Gap Analysis Summary: ${framework1} to ${framework2}</h4>
            <p>There are ${gapResult.total_controls_framework1} controls in ${framework1} and ${gapResult.total_controls_framework2} controls in ${framework2}.</p>
            <p>${gapResult.unmapped_controls.length} controls (${gapResult.gap_percentage.toFixed(1)}%) from ${framework1} do not have mappings to ${framework2}.</p>
            
            <h4>Key Gap Areas:</h4>
            <ul>
                ${generateGapAreas(gapResult.unmapped_controls)}
            </ul>
            
            <p>Organizations should focus on addressing these gaps to ensure comprehensive compliance coverage.</p>
        `;
        
        document.getElementById('summary-container').innerHTML = summaryText;
        
    } catch (error) {
        console.error('Error generating summary:', error);
        document.getElementById('summary-container').innerHTML = `<p>Error generating summary: ${error.message}</p>`;
    }
}

function generateGapAreas(unmappedControls) {
    // Group controls by family
    const familyGroups = {};
    
    unmappedControls.forEach(control => {
        const family = control.family || 'Other';
        if (!familyGroups[family]) {
            familyGroups[family] = [];
        }
        familyGroups[family].push(control);
    });
    
    // Generate HTML for key gap areas
    let html = '';
    for (const family in familyGroups) {
        html += `<li><strong>${family}</strong>: ${familyGroups[family].length} unmapped controls</li>`;
    }
    
    return html;
}

// Upload Page
function initUploadPage() {
    // NIST document upload
    const nistFileInput = document.getElementById('nist-file');
    const nistFileName = document.getElementById('nist-file-name');
    const uploadNistButton = document.getElementById('upload-nist');
    
    nistFileInput.addEventListener('change', () => {
        nistFileName.textContent = nistFileInput.files[0] ? nistFileInput.files[0].name : 'No file chosen';
    });
    
    uploadNistButton.addEventListener('click', () => {
        uploadDocument('nist', nistFileInput, 'nist-upload-result');
    });
    
    // HIPAA document upload
    const hipaaFileInput = document.getElementById('hipaa-file');
    const hipaaFileName = document.getElementById('hipaa-file-name');
    const uploadHipaaButton = document.getElementById('upload-hipaa');
    
    hipaaFileInput.addEventListener('change', () => {
        hipaaFileName.textContent = hipaaFileInput.files[0] ? hipaaFileInput.files[0].name : 'No file chosen';
    });
    
    uploadHipaaButton.addEventListener('click', () => {
        uploadDocument('hipaa', hipaaFileInput, 'hipaa-upload-result');
    });
}

async function uploadDocument(type, fileInput, resultContainerId) {
    try {
        const file = fileInput.files[0];
        
        if (!file) {
            alert('Please select a file to upload');
            return;
        }
        
        // Check if file is a PDF
        if (file.type !== 'application/pdf') {
            alert('Please upload a PDF file');
            return;
        }
        
        // Show uploading status
        const resultContainer = document.getElementById(resultContainerId);
        resultContainer.className = 'upload-result';
        resultContainer.innerHTML = 'Uploading and processing document...';
        
        // Create form data
        const formData = new FormData();
        formData.append('file', file);
        
        // Determine endpoint
        const endpoint = type === 'nist' ? '/upload/nist' : '/upload/hipaa';
        
        // Upload file
        const response = await fetch(`${API_URL}${endpoint}`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Failed to upload document');
        }
        
        const result = await response.json();
        
        // Show success message
        resultContainer.className = 'upload-result upload-success';
        resultContainer.innerHTML = `
            <p>${result.message}</p>
            <p>Found ${type === 'nist' ? result.controls_found : result.regulations_found} ${type === 'nist' ? 'controls' : 'regulations'}</p>
        `;
        
        // Reset file input
        fileInput.value = '';
        document.getElementById(type === 'nist' ? 'nist-file-name' : 'hipaa-file-name').textContent = 'No file chosen';
        
        // Add activity item
        addActivityItem(`Uploaded ${type.toUpperCase()} document: ${file.name}`);
        
        // Refresh dashboard stats
        fetchDashboardStats();
        
    } catch (error) {
        console.error(`Error uploading ${type} document:`, error);
        
        // Show error message
        const resultContainer = document.getElementById(resultContainerId);
        resultContainer.className = 'upload-result upload-error';
        resultContainer.innerHTML = `<p>Error: ${error.message}</p>`;
        
        addActivityItem(`Error uploading ${type.toUpperCase()} document: ${error.message}`, 'error');
    }
}