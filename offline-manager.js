// ============================================
// UNIYO LMS - Offline Manager (IndexedDB)
// ============================================

class OfflineManager {
    constructor() {
        this.dbName = 'UNIYO_OFFLINE_DB';
        this.dbVersion = 1;
        this.db = null;
        this.initialized = false;
    }
    
    async init() {
        if (this.initialized) return this.db;
        
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.dbName, this.dbVersion);
            
            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                
                if (!db.objectStoreNames.contains('lessons')) {
                    const lessonStore = db.createObjectStore('lessons', { keyPath: 'id' });
                    lessonStore.createIndex('course_code', 'course_code', { unique: false });
                }
                
                if (!db.objectStoreNames.contains('worksheets')) {
                    db.createObjectStore('worksheets', { keyPath: 'id' });
                }
                
                if (!db.objectStoreNames.contains('progress')) {
                    db.createObjectStore('progress', { keyPath: 'id', autoIncrement: true });
                }
            };
            
            request.onsuccess = (event) => {
                this.db = event.target.result;
                this.initialized = true;
                resolve(this.db);
            };
            
            request.onerror = (event) => {
                reject(event.target.error);
            };
        });
    }
    
    async saveLesson(lesson) {
        await this.init();
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['lessons'], 'readwrite');
            const store = transaction.objectStore('lessons');
            store.put(lesson);
            transaction.oncomplete = () => resolve(true);
            transaction.onerror = (event) => reject(event.target.error);
        });
    }
    
    async getLesson(lessonId) {
        await this.init();
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['lessons'], 'readonly');
            const store = transaction.objectStore('lessons');
            const request = store.get(lessonId);
            request.onsuccess = () => resolve(request.result);
            request.onerror = (event) => reject(event.target.error);
        });
    }
    
    async getAllLessons() {
        await this.init();
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction(['lessons'], 'readonly');
            const store = transaction.objectStore('lessons');
            const request = store.getAll();
            request.onsuccess = () => resolve(request.result);
            request.onerror = (event) => reject(event.target.error);
        });
    }
    
    async clearAll() {
        await this.init();
        return new Promise((resolve, reject) => {
            const stores = ['lessons', 'worksheets', 'progress'];
            let completed = 0;
            stores.forEach(storeName => {
                const transaction = this.db.transaction([storeName], 'readwrite');
                const store = transaction.objectStore(storeName);
                store.clear();
                transaction.oncomplete = () => {
                    completed++;
                    if (completed === stores.length) resolve(true);
                };
            });
        });
    }
}

const offlineManager = new OfflineManager();

function registerServiceWorker() {
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => {
            navigator.serviceWorker.register('/static/js/service-worker.js')
                .then(() => console.log('Service Worker registered'))
                .catch(() => console.log('Service Worker failed'));
        });
    }
}

window.addEventListener('online', () => {
    showToast('Connection restored', 'success');
});

window.addEventListener('offline', () => {
    showToast('You are offline', 'warning');
});

document.addEventListener('DOMContentLoaded', function() {
    registerServiceWorker();
    offlineManager.init();
});
