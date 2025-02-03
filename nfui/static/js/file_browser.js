const createFileBrowser = (options = {}) => {
    const {
        showDownloadButton = true,
        onFileSelect = null,
        showContentViewer = true
    } = options;

    return {
        delimiters: ['${', '}'],
    data() {
        return {
            currentBackend: '',
            currentPath: '',
            loading: false,
            items: [],
            selectedFile: null,
            fileContent: null,
            currentPage: 1,
            pageSize: 25,
            selectedMetadata: ['size'],
            showTime: false,
            sortBy: 'name',
            sortDirection: 'asc',
            showDownloadButton,
            showContentViewer
        };
    },
    computed: {
        pathParts() {
            return this.currentPath.split('/').filter(p => p);
        },
        totalPages() {
            return Math.ceil(this.items.length / this.pageSize);
        },
        sortedItems() {
            return [...this.items].sort((a, b) => {
                let aVal = a[this.sortBy];
                let bVal = b[this.sortBy];
                const modifier = this.sortDirection === 'asc' ? 1 : -1;
                
                // Handle special cases for name sorting
                if (this.sortBy === 'name' || this.sortBy === 'name-numeric') {
                    // Directories always come first
                    if (a.type !== b.type) {
                        return a.type === 'directory' ? -1 : 1;
                    }
                    
                    if (this.sortBy === 'name-numeric') {
                        // Extract numbers and text parts
                        const splitName = (name) => {
                            const parts = name.toLowerCase().match(/([^0-9]+)|([0-9]+)/g) || [];
                            return parts.map(part => isNaN(part) ? part : Number(part));
                        };
                        
                        const aParts = splitName(a.name);
                        const bParts = splitName(b.name);
                        
                        // Compare parts
                        for (let i = 0; i < Math.min(aParts.length, bParts.length); i++) {
                            if (aParts[i] !== bParts[i]) {
                                // If both parts are numbers, compare numerically
                                if (typeof aParts[i] === 'number' && typeof bParts[i] === 'number') {
                                    return (aParts[i] - bParts[i]) * modifier;
                                }
                                // Otherwise compare as strings
                                return (aParts[i] > bParts[i] ? 1 : -1) * modifier;
                            }
                        }
                        return aParts.length - bParts.length;
                    } else {
                        aVal = a.name.toLowerCase();
                        bVal = b.name.toLowerCase();
                    }
                }
                
                // Handle null/undefined values
                if (!aVal && !bVal) return 0;
                if (!aVal) return 1;
                if (!bVal) return -1;
                
                // Compare based on type
                if (this.sortBy === 'size') {
                    aVal = a.type === 'directory' ? -1 : (a.size || 0);
                    bVal = b.type === 'directory' ? -1 : (b.size || 0);
                } else if (this.sortBy.includes('date')) {
                    aVal = new Date(aVal).getTime();
                    bVal = new Date(bVal).getTime();
                }
                
                // Apply sort direction
                return aVal > bVal ? modifier : -modifier;
            });
        },
        paginatedItems() {
            const start = (this.currentPage - 1) * this.pageSize;
            const end = start + this.pageSize;
            return this.sortedItems.slice(start, end);
        }
    },
    methods: {
        getPathUpTo(index) {
            return this.pathParts.slice(0, index + 1).join('/');
        },
        async loadDirectory(backend, path) {
            this.currentBackend = backend;
            this.currentPath = path;
            this.loading = true;
            this.selectedFile = null;
            this.fileContent = null;
            
            try {
                const response = await fetch(`/api/storage/${backend}/list?path=${path}`);
                const data = await response.json();
                this.items = data.items;
                this.currentPage = 1;
            } catch (error) {
                console.error('Error loading directory:', error);
                this.items = [];
            } finally {
                this.loading = false;
            }
        },
        async viewFile(file) {
            if (onFileSelect) {
                onFileSelect(file);
                return;
            }

            if (!this.showContentViewer) {
                return;
            }

            this.selectedFile = file;
            this.fileContent = null;
            
            try {
                const response = await fetch(`/api/storage/download?storage=${this.currentBackend}&path=${this.currentPath}/${file.name}`);
                this.fileContent = await response.text();
            } catch (error) {
                console.error('Error loading file content:', error);
                this.fileContent = 'Error loading file content';
            }
        },
        nextPage() {
            if (this.currentPage < this.totalPages) {
                this.currentPage++;
            }
        },
        previousPage() {
            if (this.currentPage > 1) {
                this.currentPage--;
            }
        },
        changePageSize(size) {
            this.pageSize = size;
            this.currentPage = 1;
        },
        changePage(page) {
            this.currentPage = page;
        },
        formatSize(item) {
            if (item.type === 'directory') return 'N/A';
            
            const size = item.size ?? 0;
            if (size === 0) return '0 B';
            
            const units = ['B', 'KB', 'MB', 'GB', 'TB'];
            let value = size;
            let unitIndex = 0;
            
            while (value >= 1024 && unitIndex < units.length - 1) {
                value /= 1024;
                unitIndex++;
            }
            
            return `${value.toFixed(1)} ${units[unitIndex]}`;
        },
        formatDate(timestamp) {
            if (!timestamp) return '';
            const date = new Date(timestamp);
            const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
            const month = months[date.getMonth()];
            const dd = String(date.getDate()).padStart(2, '0');
            const yyyy = date.getFullYear();
            
            if (this.showTime) {
                const hh = String(date.getHours()).padStart(2, '0');
                const min = String(date.getMinutes()).padStart(2, '0');
                const ss = String(date.getSeconds()).padStart(2, '0');
                return `${month} ${dd}, ${yyyy} ${hh}:${min}:${ss}`;
            }
            
            return `${month} ${dd}, ${yyyy}`;
        },
        toggleTimeDisplay() {
            this.showTime = !this.showTime;
        },
        toggleSortDirection() {
            this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
            this.currentPage = 1;
        }
    }
    }
};

// Export the component factory
export default createFileBrowser;
