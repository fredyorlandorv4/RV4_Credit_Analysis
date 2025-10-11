// Debug JavaScript for testing training buttons
// This file can be used in browser console to test training functions

// Test function to check if training endpoints work
function debugTraining() {
    console.log('Testing training endpoints...');
    
    // Test sample training
    console.log('Testing sample training...');
    fetch('/api/train/sample', {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        console.log('Sample training response status:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('Sample training response:', data);
    })
    .catch(error => {
        console.error('Sample training error:', error);
    });
    
    // Test database training
    console.log('Testing database training...');
    fetch('/api/train/database', {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        console.log('Database training response status:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('Database training response:', data);
    })
    .catch(error => {
        console.error('Database training error:', error);
    });
    
    // Test model info
    console.log('Testing model info...');
    fetch('/api/model/info', {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        console.log('Model info response status:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('Model info response:', data);
    })
    .catch(error => {
        console.error('Model info error:', error);
    });
}

// Test if training functions exist
function checkTrainingFunctions() {
    console.log('Checking if training functions exist...');
    console.log('trainFromDatabase function:', typeof trainFromDatabase);
    console.log('trainFromSample function:', typeof trainFromSample);
    console.log('startTraining function:', typeof startTraining);
    
    // Check if modal elements exist
    console.log('Train model modal:', document.getElementById('trainModelModal') ? 'Found' : 'Not found');
    console.log('Training progress:', document.getElementById('trainingProgress') ? 'Found' : 'Not found');
    console.log('Training results:', document.getElementById('trainingResults') ? 'Found' : 'Not found');
}

// Run checks when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, running training checks...');
    checkTrainingFunctions();
});

console.log('Debug script loaded. Run debugTraining() to test endpoints or checkTrainingFunctions() to check UI elements.');
