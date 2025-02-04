function clearCache(type) {
    const button = document.querySelector('#cacheDropdown');
    const icon = button.querySelector('i');
    const originalClass = icon.className;
    
    // Show loading state
    button.disabled = true;
    icon.className = 'bi bi-arrow-repeat spin';

    // Make API request
    fetch(`/api/cache/clear/${type}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // If we're on a page that might need refreshing after cache clear
            if (window.location.pathname === '/storage' || window.location.pathname === '/pipelines') {
                window.location.reload();
            }
        } else {
            console.error('Cache clear failed:', data.message);
            alert('Failed to clear cache: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Cache clear error:', error);
        alert('Failed to clear cache: ' + error.message);
    })
    .finally(() => {
        // Restore button state
        button.disabled = false;
        icon.className = originalClass;
    });
}

// Add CSS for spin animation
const style = document.createElement('style');
style.textContent = `
    .spin {
        animation: spin 1s linear infinite;
    }
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style);
