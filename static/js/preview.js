// Theme toggle functionality
function toggleTheme() {
    const html = document.documentElement;
    const isDark = html.classList.toggle('dark');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    updateThemeIcon(isDark);
}

function updateThemeIcon(isDark) {
    const icon = document.getElementById('theme-icon');
    if (isDark) {
        icon.innerHTML = '<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"></path></svg>';
    } else {
        icon.innerHTML = '<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path></svg>';
    }
}

// Tab switching functionality
function showTab(tabId) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.add('hidden');
    });
    
    // Remove active class from all tab buttons
    document.querySelectorAll('.tab-button').forEach(button => {
        button.classList.remove('bg-blue-600', 'text-white');
        button.classList.add('text-gray-600', 'hover:text-gray-900', 'hover:bg-gray-100');
    });
    
    // Show selected tab content
    document.getElementById(tabId).classList.remove('hidden');
    
    // Add active class to selected tab button
    const selectedButton = document.querySelector(`[onclick="showTab('${tabId}')"]`);
    selectedButton.classList.remove('text-gray-600', 'hover:text-gray-900', 'hover:bg-gray-100');
    selectedButton.classList.add('bg-blue-600', 'text-white');
}

// Sub-tab switching functionality
function showSubTab(tabId, subTabId) {
    // Hide all sub-tab contents for this tab
    document.querySelectorAll(`#${tabId} .sub-tab-content`).forEach(content => {
        content.classList.add('hidden');
    });
    
    // Remove active class from all sub-tab buttons for this tab
    document.querySelectorAll(`#${tabId} .sub-tab-button`).forEach(button => {
        button.classList.remove('bg-blue-600', 'text-white');
        button.classList.add('text-gray-600', 'hover:text-gray-900', 'hover:bg-gray-100');
    });
    
    // Show selected sub-tab content
    document.getElementById(subTabId).classList.remove('hidden');
    
    // Add active class to selected sub-tab button
    const selectedButton = document.querySelector(`[onclick="showSubTab('${tabId}', '${subTabId}')"]`);
    selectedButton.classList.remove('text-gray-600', 'hover:text-gray-900', 'hover:bg-gray-100');
    selectedButton.classList.add('bg-blue-600', 'text-white');
}

// Copy code functionality
function copyCode(codeId) {
    const codeElement = document.getElementById(codeId);
    const code = codeElement.textContent;
    
    navigator.clipboard.writeText(code).then(() => {
        const button = codeElement.nextElementSibling;
        const originalText = button.textContent;
        button.textContent = 'Copied!';
        button.classList.add('bg-green-600');
        button.classList.remove('bg-blue-600');
        
        setTimeout(() => {
            button.textContent = originalText;
            button.classList.remove('bg-green-600');
            button.classList.add('bg-blue-600');
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy code:', err);
    });
}

// Download functionality
function downloadAll() {
    var files = JSON.parse('{{ generated_files|safe|escapejs }}');
    var fileNames = files.map(function(f) { return f.class_name + '.dart'; });
    var url = "{% url 'excel_converter:download_all' %}?files=" + encodeURIComponent(JSON.stringify(fileNames));
    window.location.href = url;
}

// Initialize theme on page load
document.addEventListener('DOMContentLoaded', function() {
    const isDark = localStorage.getItem('theme') === 'dark';
    if (isDark) {
        document.documentElement.classList.add('dark');
        updateThemeIcon(true);
    }
});