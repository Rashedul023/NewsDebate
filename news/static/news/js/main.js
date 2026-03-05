// Core utilities and initialization

// ============================================
// API Client
// ============================================
const API = {
    baseURL: '/api',
    
    async request(endpoint, options = {}) {
        try {
            const response = await fetch(`${this.baseURL}${endpoint}`, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });
            
            if (!response.ok) {
                const error = new Error(`HTTP ${response.status}`);
                error.status = response.status;
                throw error;
            }
            
            return await response.json();
        } catch (error) {
            console.error(`API Error (${endpoint}):`, error);
            throw error;
        }
    },
    
    // Articles
    getArticles(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/articles/${query ? '?' + query : ''}`);
    },
    
    getArticle(id) {
        return this.request(`/articles/${id}/`);
    },
    
    // Stats and metadata
    getStats() {
        return this.request('/articles/stats/');
    },
    
    getSources() {
        return this.request('/articles/sources/');
    },
    
    getBiasOptions() {
        return this.request('/articles/bias_options/');
    }
};

// ============================================
// Utility Functions
// ============================================
const Utils = {
    formatDate(dateString) {
        const options = { 
            year: 'numeric', 
            month: 'short', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };
        return new Date(dateString).toLocaleDateString('en-US', options);
    },
    
    getBiasClass(bias) {
        const classes = {
            'left': 'badge-left',
            'right': 'badge-right',
            'center': 'badge-center'
        };
        return classes[bias] || 'badge-unclassified';
    },
    
    getBiasDisplay(bias) {
        return bias.charAt(0).toUpperCase() + bias.slice(1);
    },
    
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};

// ============================================
// UI Helpers
// ============================================
const UI = {
    showLoading(container) {
        if (typeof container === 'string') {
            container = document.getElementById(container);
        }
        if (container) {
            container.innerHTML = `
                <div class="flex flex-col items-center justify-center py-12">
                    <div class="spinner"></div>
                    <p class="mt-4 text-gray-600">Loading...</p>
                </div>
            `;
        }
    },
    
    showError(container, message, retryFn = null) {
        if (typeof container === 'string') {
            container = document.getElementById(container);
        }
        if (container) {
            container.innerHTML = `
                <div class="bg-red-50 border-l-4 border-red-500 p-4">
                    <div class="flex">
                        <div class="flex-shrink-0">
                            <svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
                            </svg>
                        </div>
                        <div class="ml-3">
                            <p class="text-sm text-red-700">${message}</p>
                            ${retryFn ? `
                                <button onclick="(${retryFn})()" class="mt-2 text-sm text-blue-600 hover:text-blue-800">
                                    Try Again
                                </button>
                            ` : ''}
                        </div>
                    </div>
                </div>
            `;
        }
    },
    
    showEmpty(container, message) {
        if (typeof container === 'string') {
            container = document.getElementById(container);
        }
        if (container) {
            container.innerHTML = `
                <div class="text-center py-12">
                    <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"></path>
                    </svg>
                    <p class="mt-2 text-gray-600">${message}</p>
                </div>
            `;
        }
    }
};

// ============================================
// Mobile Menu
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    const menuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (menuButton && mobileMenu) {
        menuButton.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
        });
    }
});

window.API = API;

console.log('✅ main.js fully loaded with API attached to window');