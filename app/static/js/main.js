/**
 * JavaScript principal para Biblioteca Personal
 */

// Confirmación de eliminación
document.addEventListener('DOMContentLoaded', function() {
    // Confirmación para eliminar
    const deleteButtons = document.querySelectorAll('[data-confirm-delete]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const message = this.dataset.confirmDelete || '¿Estás seguro de que quieres eliminar este elemento?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

    // Popovers
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    const popoverList = [...popoverTriggerList].map(popoverTriggerEl => new bootstrap.Popover(popoverTriggerEl));
});

/**
 * Previsualizar imagen antes de subir
 */
function previewImage(input, targetId) {
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const target = document.getElementById(targetId);
            if (target) {
                target.innerHTML = `<img src="${e.target.result}" class="img-fluid" alt="Preview">`;
            }
        };
        reader.readAsDataURL(input.files[0]);
    }
}

// Event listener para preview de imágenes
document.addEventListener('DOMContentLoaded', function() {
    const coverFileInput = document.getElementById('cover_file');
    if (coverFileInput) {
        coverFileInput.addEventListener('change', function() {
            previewImage(this, 'coverPreview');
        });
    }
});

/**
 * Buscar libro en Google Books
 */
async function searchGoogleBooks(query) {
    try {
        const response = await fetch(`/api/search-books?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error searching Google Books:', error);
        return { success: false, error: error.message };
    }
}

/**
 * Obtener información de libro por ISBN
 */
async function getBookByISBN(isbn) {
    try {
        const response = await fetch(`/api/google-books/${isbn}`);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error getting book by ISBN:', error);
        return { success: false, error: error.message };
    }
}

/**
 * Formatear fecha
 */
function formatDate(dateString, format = 'dd/mm/yyyy') {
    if (!dateString) return '';
    const date = new Date(dateString);
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();

    switch (format) {
        case 'dd/mm/yyyy':
            return `${day}/${month}/${year}`;
        case 'mm/dd/yyyy':
            return `${month}/${day}/${year}`;
        case 'yyyy-mm-dd':
            return `${year}-${month}-${day}`;
        default:
            return dateString;
    }
}

/**
 * Truncar texto
 */
function truncateText(text, length = 100) {
    if (!text || text.length <= length) return text;
    return text.substring(0, length).trim() + '...';
}

/**
 * Sanitizar ISBN
 */
function sanitizeISBN(isbn) {
    if (!isbn) return '';
    return isbn.replace(/[^0-9X]/gi, '');
}

/**
 * Validar ISBN-10 o ISBN-13
 */
function validateISBN(isbn) {
    isbn = sanitizeISBN(isbn);

    if (isbn.length === 10) {
        return validateISBN10(isbn);
    } else if (isbn.length === 13) {
        return validateISBN13(isbn);
    }

    return false;
}

function validateISBN10(isbn) {
    let sum = 0;
    for (let i = 0; i < 9; i++) {
        if (isbn[i] < '0' || isbn[i] > '9') return false;
        sum += (10 - i) * parseInt(isbn[i]);
    }
    const checksum = isbn[9] === 'X' ? 10 : parseInt(isbn[9]);
    sum += checksum;
    return sum % 11 === 0;
}

function validateISBN13(isbn) {
    let sum = 0;
    for (let i = 0; i < 13; i++) {
        if (isbn[i] < '0' || isbn[i] > '9') return false;
        sum += (i % 2 === 0 ? 1 : 3) * parseInt(isbn[i]);
    }
    return sum % 10 === 0;
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
 * Exportar utilidades globalmente
 */
window.BibliotecaUtils = {
    searchGoogleBooks,
    getBookByISBN,
    formatDate,
    truncateText,
    sanitizeISBN,
    validateISBN,
    debounce,
    previewImage
};
