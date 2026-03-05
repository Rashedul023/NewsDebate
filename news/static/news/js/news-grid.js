const NewsGrid = {
    container: null,
    currentPage: 1,
    hasMore: true,
    isLoading: false,
    filters: {},
    
    init(containerId) {
        this.container = document.getElementById(containerId);
        this.loadSources();
        this.loadStats();
        this.load();
    },
    
    async load(reset = true) {
        if (this.isLoading || (!reset && !this.hasMore)) return;
        
        this.isLoading = true;
        
        if (reset) {
            this.currentPage = 1;
            UI.showLoading(this.container);
        }
        
        try {
            const params = {
                page: this.currentPage,
                ...this.filters
            };
            
            const data = await API.getArticles(params);
            
            if (reset) {
                this.container.innerHTML = '';
            }
            
            this.renderArticles(data.results);
            this.hasMore = !!data.next;
            this.updateLoadMoreButton();
            
        } catch (error) {
            UI.showError(this.container, 'Failed to load articles', () => this.load(reset));
        } finally {
            this.isLoading = false;
        }
    },
    
    renderArticles(articles) {
        if (articles.length === 0 && this.currentPage === 1) {
            UI.showEmpty(this.container, 'No articles found');
            return;
        }
        
        articles.forEach(article => {
            this.container.appendChild(this.createCard(article));
        });
    },
    
    createCard(article) {
        const card = document.createElement('div');
        card.className = 'article-card bg-white rounded-xl shadow-md overflow-hidden border border-gray-100';
        
        const biasClass = Utils.getBiasClass(article.bias_label);
        const date = Utils.formatDate(article.published_at);
        const biasDisplay = Utils.getBiasDisplay(article.bias_label);
        
        card.innerHTML = `
            ${article.image_url ? 
                `<img src="${article.image_url}" alt="${article.title}" 
                      class="w-full h-48 object-cover" 
                      onerror="this.onerror=null; this.parentElement.innerHTML='<div class=\'w-full h-48 bg-gray-200 flex items-center justify-center\'><span class=\'text-gray-400\'>Image failed to load</span></div>';">` : 
                `<div class="w-full h-48 bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
                    <span class="text-gray-400">📰 No image</span>
                 </div>`
            }
            <div class="p-6">
                <div class="flex items-center justify-between mb-3">
                    <span class="text-sm font-medium text-gray-600">${article.source_name}</span>
                    <span class="text-xs px-3 py-1 rounded-full font-medium ${biasClass}">
                        ${biasDisplay}
                    </span>
                </div>
                <h3 class="font-bold text-xl mb-3 line-clamp-2">${article.title}</h3>
                <div class="flex items-center justify-between pt-4 border-t border-gray-100">
                    <span class="text-sm text-gray-500">${date}</span>
                    <a href="/article/${article.id}/" class="inline-flex items-center text-blue-600 hover:text-blue-800 font-medium">
                        Read More 
                        <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                        </svg>
                    </a>
                </div>
            </div>
        `;
        
        return card;
    },
    
    async loadSources() {
        try {
            const sources = await API.getSources();
            const sourceFilter = document.getElementById('sourceFilter');
            const footerSources = document.getElementById('footer-sources');
            
            if (sourceFilter) {
                sources.forEach(source => {
                    const option = document.createElement('option');
                    option.value = source;
                    option.textContent = source;
                    sourceFilter.appendChild(option);
                });
            }
            
            if (footerSources) {
                footerSources.innerHTML = sources.slice(0, 5)
                    .map(s => `<li class="text-gray-300">📰 ${s}</li>`)
                    .join('');
            }
        } catch (error) {
            console.error('Failed to load sources:', error);
        }
    },
    
    async loadStats() {
        try {
            const stats = await API.getStats();
            
            // Update footer
            const totalEl = document.getElementById('total-articles');
            if (totalEl) {
                totalEl.textContent = `Articles: ${stats.total_articles}`;
            }
            
            // Update stats bar if it exists
            const statsBar = document.getElementById('stats-bar');
            if (statsBar) {
                statsBar.innerHTML = `
                    <div class="bg-blue-50 p-4 rounded-lg text-center">
                        <div class="text-2xl font-bold text-blue-600">${stats.total_articles}</div>
                        <div class="text-sm">Total</div>
                    </div>
                    <div class="bg-green-50 p-4 rounded-lg text-center">
                        <div class="text-2xl font-bold text-green-600">${stats.last_7_days_added}</div>
                        <div class="text-sm">This Week</div>
                    </div>
                    <div class="bg-purple-50 p-4 rounded-lg text-center">
                        <div class="text-2xl font-bold text-purple-600">${stats.by_source.length}</div>
                        <div class="text-sm">Sources</div>
                    </div>
                    <div class="bg-orange-50 p-4 rounded-lg text-center">
                        <div class="text-2xl font-bold text-orange-600">${stats.average_bias_score}</div>
                        <div class="text-sm">Avg Bias</div>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Failed to load stats:', error);
        }
    },
    
    updateLoadMoreButton() {
        const btn = document.getElementById('loadMoreBtn');
        if (btn) {
            btn.disabled = !this.hasMore;
            btn.textContent = this.hasMore ? 'Load More Articles' : 'No More Articles';
            btn.classList.toggle('opacity-50', !this.hasMore);
        }
    },
    
    applyFilters(newFilters) {
        this.filters = { ...this.filters, ...newFilters };
        this.load(true);
    },
    
    loadMore() {
        if (!this.isLoading && this.hasMore) {
            this.currentPage++;
            this.load(false);
        }
    }
};