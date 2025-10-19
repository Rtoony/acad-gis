/**
 * ACAD=GIS Shared Components
 * Version: 1.0
 * 
 * Reusable React components and utility functions for all tools.
 * Import this file after React and before your tool-specific code.
 */

const { useState, useEffect } = React;

// ============================================
// API CONFIGURATION
// ============================================

const API_BASE_URL = 'http://localhost:8000/api';

// ============================================
// API HELPER FUNCTIONS
// ============================================

const api = {
    async get(endpoint) {
        const response = await fetch(`${API_BASE_URL}${endpoint}`);
        if (!response.ok) throw new Error(`API Error: ${response.statusText}`);
        return response.json();
    },
    
    async post(endpoint, data) {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!response.ok) throw new Error(`API Error: ${response.statusText}`);
        return response.json();
    },
    
    async put(endpoint, data) {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!response.ok) throw new Error(`API Error: ${response.statusText}`);
        return response.json();
    },
    
    async delete(endpoint) {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'DELETE'
        });
        if (!response.ok) throw new Error(`API Error: ${response.statusText}`);
        return response.json();
    },
    
    async upload(endpoint, formData) {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            body: formData
        });
        if (!response.ok) throw new Error(`API Error: ${response.statusText}`);
        return response.json();
    },
    
    async checkHealth() {
        try {
            await this.get('/health');
            return true;
        } catch (error) {
            return false;
        }
    }
};

// ============================================
// SHARED COMPONENTS
// ============================================

/**
 * API Status Indicator Component
 */
function ApiStatus() {
    const [connected, setConnected] = useState(false);
    const [checking, setChecking] = useState(true);

    useEffect(() => {
        checkConnection();
        const interval = setInterval(checkConnection, 30000); // Check every 30s
        return () => clearInterval(interval);
    }, []);

    const checkConnection = async () => {
        const isConnected = await api.checkHealth();
        setConnected(isConnected);
        setChecking(false);
    };

    if (checking) {
        return (
            <div className="status-indicator" style={{ background: 'rgba(59, 130, 246, 0.2)' }}>
                <i className="fas fa-spinner fa-spin"></i>
                <span>Checking API...</span>
            </div>
        );
    }

    return (
        <div className={`status-indicator ${connected ? 'status-online' : 'status-offline'}`}>
            <span className="status-dot"></span>
            <span>{connected ? 'API Connected' : 'API Offline'}</span>
        </div>
    );
}

/**
 * Loading Spinner Component
 */
function LoadingSpinner({ text = 'Loading...' }) {
    return (
        <div className="text-center" style={{ padding: '3rem' }}>
            <div className="spinner" style={{ margin: '0 auto' }}></div>
            <p className="loading-text mt-md">{text}</p>
        </div>
    );
}

/**
 * Full Page Loading Overlay
 */
function LoadingOverlay({ text = 'Loading...' }) {
    return (
        <div className="loading-overlay">
            <div className="spinner"></div>
            <p className="loading-text">{text}</p>
        </div>
    );
}

/**
 * Alert Component
 */
function Alert({ type = 'info', message, icon, onClose }) {
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-triangle',
        warning: 'fa-exclamation-circle',
        info: 'fa-info-circle'
    };

    return (
        <div className={`alert alert-${type}`}>
            <i className={`fas ${icon || icons[type]}`}></i>
            <span style={{ flex: 1 }}>{message}</span>
            {onClose && (
                <button 
                    onClick={onClose}
                    className="btn-icon btn-ghost"
                    style={{ marginLeft: 'auto' }}
                >
                    <i className="fas fa-times"></i>
                </button>
            )}
        </div>
    );
}

/**
 * Modal Component
 */
function Modal({ isOpen, onClose, title, children, footer, size = 'medium' }) {
    if (!isOpen) return null;

    const sizes = {
        small: '400px',
        medium: '600px',
        large: '900px'
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div 
                className="modal-content" 
                style={{ maxWidth: sizes[size] }}
                onClick={(e) => e.stopPropagation()}
            >
                <div className="modal-header">
                    <h2 className="modal-title">{title}</h2>
                    <button onClick={onClose} className="btn-icon btn-ghost">
                        <i className="fas fa-times"></i>
                    </button>
                </div>
                <div className="modal-body">
                    {children}
                </div>
                {footer && (
                    <div className="modal-footer">
                        {footer}
                    </div>
                )}
            </div>
        </div>
    );
}

/**
 * Confirmation Dialog Component
 */
function ConfirmDialog({ isOpen, onClose, onConfirm, title, message, confirmText = 'Confirm', cancelText = 'Cancel', danger = false }) {
    const [loading, setLoading] = useState(false);

    const handleConfirm = async () => {
        setLoading(true);
        try {
            await onConfirm();
            onClose();
        } catch (error) {
            console.error('Confirmation error:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Modal 
            isOpen={isOpen} 
            onClose={onClose} 
            title={title}
            size="small"
            footer={
                <>
                    <button className="btn btn-ghost" onClick={onClose} disabled={loading}>
                        {cancelText}
                    </button>
                    <button 
                        className={`btn ${danger ? 'btn-danger' : 'btn-primary'}`}
                        onClick={handleConfirm}
                        disabled={loading}
                    >
                        {loading ? (
                            <>
                                <i className="fas fa-spinner fa-spin"></i>
                                Processing...
                            </>
                        ) : confirmText}
                    </button>
                </>
            }
        >
            <p>{message}</p>
        </Modal>
    );
}

/**
 * Empty State Component
 */
function EmptyState({ icon, title, message, action }) {
    return (
        <div className="card text-center" style={{ padding: '3rem' }}>
            <i className={`fas fa-${icon}`} style={{ fontSize: '4rem', color: 'var(--color-text-muted)', marginBottom: '1rem' }}></i>
            <h3 style={{ marginBottom: '0.5rem' }}>{title}</h3>
            <p style={{ color: 'var(--color-text-secondary)', marginBottom: action ? '1.5rem' : 0 }}>
                {message}
            </p>
            {action}
        </div>
    );
}

/**
 * Stats Card Component
 */
function StatCard({ icon, label, value, color = 'blue' }) {
    const colors = {
        blue: { bg: 'rgba(59, 130, 246, 0.2)', text: '#3b82f6' },
        green: { bg: 'rgba(16, 185, 129, 0.2)', text: '#10b981' },
        orange: { bg: 'rgba(245, 158, 11, 0.2)', text: '#f59e0b' },
        purple: { bg: 'rgba(168, 85, 247, 0.2)', text: '#a855f7' },
        red: { bg: 'rgba(239, 68, 68, 0.2)', text: '#ef4444' }
    };

    const colorStyle = colors[color];

    return (
        <div className="card">
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div>
                    <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.875rem' }}>
                        {label}
                    </p>
                    <p style={{ fontSize: '2rem', fontWeight: 'bold', marginTop: '0.5rem' }}>
                        {value}
                    </p>
                </div>
                <div 
                    style={{ 
                        width: '60px', 
                        height: '60px', 
                        borderRadius: 'var(--radius-lg)',
                        background: colorStyle.bg,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                    }}
                >
                    <i className={`fas fa-${icon}`} style={{ fontSize: '1.75rem', color: colorStyle.text }}></i>
                </div>
            </div>
        </div>
    );
}

/**
 * Header Component with Navigation
 */
function Header({ title, subtitle, showBackButton = false, backUrl = '../tool_launcher.html', rightContent }) {
    return (
        <header className="header">
            <div className="header-content">
                <div className="header-title">
                    {showBackButton && (
                        <a href={backUrl} className="btn btn-ghost btn-icon">
                            <i className="fas fa-arrow-left"></i>
                        </a>
                    )}
                    <i className="fas fa-drafting-compass" style={{ fontSize: '2rem' }}></i>
                    <div>
                        <h1 className="orbitron neon-blue">{title}</h1>
                        {subtitle && <p className="header-subtitle">{subtitle}</p>}
                    </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-md)' }}>
                    {rightContent}
                    <ApiStatus />
                </div>
            </div>
        </header>
    );
}

/**
 * Footer Component
 */
function Footer() {
    return (
        <footer className="footer">
            ACAD=GIS © 2025 • CAD Database Management System
        </footer>
    );
}

/**
 * Search Bar Component
 */
function SearchBar({ placeholder = 'Search...', value, onChange, onClear }) {
    return (
        <div style={{ position: 'relative', width: '100%' }}>
            <i 
                className="fas fa-search" 
                style={{ 
                    position: 'absolute', 
                    left: '1rem', 
                    top: '50%', 
                    transform: 'translateY(-50%)',
                    color: 'var(--color-text-secondary)'
                }}
            ></i>
            <input
                type="text"
                className="form-input"
                placeholder={placeholder}
                value={value}
                onChange={(e) => onChange(e.target.value)}
                style={{ paddingLeft: '2.5rem', paddingRight: value ? '2.5rem' : '1rem' }}
            />
            {value && (
                <button
                    onClick={onClear}
                    className="btn-icon btn-ghost"
                    style={{ 
                        position: 'absolute', 
                        right: '0.5rem', 
                        top: '50%', 
                        transform: 'translateY(-50%)'
                    }}
                >
                    <i className="fas fa-times"></i>
                </button>
            )}
        </div>
    );
}

/**
 * Badge Component
 */
function Badge({ children, color = 'blue', icon }) {
    const colors = {
        blue: { bg: 'rgba(59, 130, 246, 0.2)', text: '#3b82f6', border: 'rgba(59, 130, 246, 0.3)' },
        green: { bg: 'rgba(16, 185, 129, 0.2)', text: '#10b981', border: 'rgba(16, 185, 129, 0.3)' },
        orange: { bg: 'rgba(245, 158, 11, 0.2)', text: '#f59e0b', border: 'rgba(245, 158, 11, 0.3)' },
        red: { bg: 'rgba(239, 68, 68, 0.2)', text: '#ef4444', border: 'rgba(239, 68, 68, 0.3)' },
        gray: { bg: 'rgba(148, 163, 184, 0.2)', text: '#94a3b8', border: 'rgba(148, 163, 184, 0.3)' }
    };

    const style = colors[color];

    return (
        <span 
            style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.25rem',
                padding: '0.25rem 0.75rem',
                borderRadius: '999px',
                fontSize: '0.75rem',
                fontWeight: 600,
                background: style.bg,
                color: style.text,
                border: `1px solid ${style.border}`
            }}
        >
            {icon && <i className={`fas fa-${icon}`}></i>}
            {children}
        </span>
    );
}

/**
 * Toast Notification System
 */
const ToastManager = {
    container: null,
    
    init() {
        if (!this.container) {
            this.container = document.createElement('div');
            this.container.style.cssText = `
                position: fixed;
                top: 1rem;
                right: 1rem;
                z-index: 10000;
                display: flex;
                flex-direction: column;
                gap: 0.5rem;
            `;
            document.body.appendChild(this.container);
        }
    },
    
    show(message, type = 'info', duration = 3000) {
        this.init();
        
        const toast = document.createElement('div');
        toast.className = `alert alert-${type}`;
        toast.style.cssText = `
            min-width: 300px;
            animation: slideInRight 0.3s ease;
        `;
        
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-triangle',
            warning: 'fa-exclamation-circle',
            info: 'fa-info-circle'
        };
        
        toast.innerHTML = `
            <i class="fas ${icons[type]}"></i>
            <span style="flex: 1">${message}</span>
            <button class="btn-icon btn-ghost" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        this.container.appendChild(toast);
        
        if (duration > 0) {
            setTimeout(() => {
                toast.style.animation = 'slideOutRight 0.3s ease';
                setTimeout(() => toast.remove(), 300);
            }, duration);
        }
    },
    
    success(message, duration) {
        this.show(message, 'success', duration);
    },
    
    error(message, duration) {
        this.show(message, 'error', duration);
    },
    
    warning(message, duration) {
        this.show(message, 'warning', duration);
    },
    
    info(message, duration) {
        this.show(message, 'info', duration);
    }
};

// Add animation styles
if (!document.getElementById('toast-animations')) {
    const style = document.createElement('style');
    style.id = 'toast-animations';
    style.textContent = `
        @keyframes slideInRight {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOutRight {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(400px);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

/**
 * Format date to readable string
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Debounce function for search inputs
 */
function debounce(func, wait) {
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

/**
 * Copy text to clipboard
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        ToastManager.success('Copied to clipboard!');
        return true;
    } catch (error) {
        ToastManager.error('Failed to copy to clipboard');
        return false;
    }
}

/**
 * Download file from data
 */
function downloadFile(data, filename, type = 'text/plain') {
    const blob = new Blob([data], { type });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}
