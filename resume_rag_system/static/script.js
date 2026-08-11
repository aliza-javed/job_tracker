/**
 * script.js
 * Frontend logic for Resume Analyzer & RAG System
 */

// ============================================================
// RESUME ANALYZER
// ============================================================

document.addEventListener('DOMContentLoaded', function() {
    
    // Resume form handler
    const resumeForm = document.getElementById('resumeForm');
    if (resumeForm) {
        resumeForm.addEventListener('submit', handleResumeSubmit);
    }
    
    // RAG query handler
    const ragForm = document.getElementById('ragForm');
    if (ragForm) {
        ragForm.addEventListener('submit', handleRagSubmit);
    }
    
    // File input display
    const fileInput = document.getElementById('resumeFile');
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const fileName = e.target.files[0]?.name || 'No file selected';
            document.getElementById('fileName').textContent = fileName;
        });
    }
});


/**
 * Handle resume form submission
 * FIX: Proper FormData handling
 */
async function handleResumeSubmit(e) {
    e.preventDefault();
    
    const fileInput = document.getElementById('resumeFile');
    const submitBtn = document.getElementById('submitBtn');
    const resultsDiv = document.getElementById('results');
    
    // Validate file selected
    if (!fileInput.files || fileInput.files.length === 0) {
        showError('Please select a file first');
        return;
    }
    
    const file = fileInput.files[0];
    
    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
        showError('File too large. Maximum size is 10MB.');
        return;
    }
    
    // Create FormData - IMPORTANT: key must be 'file' (matches backend)
    const formData = new FormData();
    formData.append('file', file);
    
    // Show loading
    submitBtn.disabled = true;
    submitBtn.textContent = 'Analyzing...';
    resultsDiv.innerHTML = '<div class="loading">Analyzing resume...</div>';
    
    try {
        // Send request
        const response = await fetch('/api/analyze-resume', {
            method: 'POST',
            body: formData
            // DO NOT set Content-Type header - browser sets it automatically
        });
        
        // FIX: Check response before parsing JSON
        const contentType = response.headers.get('content-type');
        
        if (!contentType || !contentType.includes('application/json')) {
            const text = await response.text();
            console.error('Non-JSON response:', text.substring(0, 200));
            throw new Error('Server returned non-JSON response');
        }
        
        const data = await response.json();
        
        if (data.success) {
            displayResults(data);
        } else {
            showError(data.error || 'Analysis failed');
        }
        
    } catch (error) {
        console.error('Error:', error);
        showError('Network error: ' + error.message);
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Upload & Analyze';
    }
}


/**
 * Handle RAG query submission
 */
async function handleRagSubmit(e) {
    e.preventDefault();
    
    const queryInput = document.getElementById('queryInput');
    const submitBtn = document.getElementById('submitBtn');
    const resultsDiv = document.getElementById('ragResults');
    
    const query = queryInput.value.trim();
    
    if (!query) {
        showError('Please enter a question');
        return;
    }
    
    submitBtn.disabled = true;
    submitBtn.textContent = 'Thinking...';
    resultsDiv.innerHTML = '<div class="loading">Processing your question...</div>';
    
    try {
        const response = await fetch('/api/rag-query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query: query })
        });
        
        // Check content type
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const text = await response.text();
            console.error('Non-JSON RAG response:', text.substring(0, 200));
            throw new Error('Server returned non-JSON response');
        }
        
        const data = await response.json();
        
        if (data.success) {
            displayRagResults(data);
        } else {
            showError(data.error || 'Query failed');
        }
        
    } catch (error) {
        console.error('RAG Error:', error);
        showError('Network error: ' + error.message);
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Ask Question';
    }
}


/**
 * Display analysis results
 */
function displayResults(data) {
    const resultsDiv = document.getElementById('results');
    
    let html = `
        <div class="results-container">
            <h2>📊 Analysis Results</h2>
            
            <div class="overall-score">
                <h3>Overall Score: ${data.overall_score}/100</h3>
                <p>Ranking: ${data.ranking}</p>
            </div>
            
            <div class="sections">
    `;
    
    // Display each section
    for (const [sectionName, section] of Object.entries(data.sections)) {
        html += `
            <div class="section" data-section="${sectionName}">
                <h3>${sectionName} - Score: ${section.score}/100</h3>
                <ul>
                    ${section.feedback.map(f => `<li>${f}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    html += `
            </div>
            
            <div class="suggestions">
                <h3>💡 Suggestions</h3>
                <ul>
                    ${data.suggestions.map(s => `<li>${s}</li>`).join('')}
                </ul>
            </div>
        </div>
    `;
    
    resultsDiv.innerHTML = html;
}


/**
 * Display RAG query results
 */
function displayRagResults(data) {
    const resultsDiv = document.getElementById('ragResults');
    
    resultsDiv.innerHTML = `
        <div class="rag-result">
            <h3>🤖 Answer</h3>
            <p>${data.answer}</p>
            <small>Query: ${data.query}</small>
        </div>
    `;
}


/**
 * Show error message
 */
function showError(message) {
    const resultsDiv = document.getElementById('results') || document.getElementById('ragResults');
    resultsDiv.innerHTML = `<div class="error">❌ ${message}</div>`;
    console.error(message);
}