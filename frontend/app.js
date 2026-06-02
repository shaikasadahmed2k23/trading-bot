/**
 * Frontend Application - Binance Futures Trading Bot
 * 
 * Handles:
 * - Form management and validation
 * - API communication with the Flask backend
 * - UI state management
 * - Real-time status updates
 */

// ────────────────────────────────────────────────────────────────────────────
// Configuration
// ────────────────────────────────────────────────────────────────────────────

const API_BASE_URL = 'http://localhost:5000/api';
const API_TIMEOUT = 30000; // 30 seconds
const HEALTH_CHECK_INTERVAL = 5000; // 5 seconds

// ────────────────────────────────────────────────────────────────────────────
// DOM Elements
// ────────────────────────────────────────────────────────────────────────────

const orderForm = document.getElementById('orderForm');
const symbolInput = document.getElementById('symbol');
const sideInputs = document.querySelectorAll('input[name="side"]');
const typeSelect = document.getElementById('type');
const quantityInput = document.getElementById('quantity');
const priceInput = document.getElementById('price');
const stopPriceInput = document.getElementById('stopPrice');
const priceGroup = document.getElementById('priceGroup');
const stopPriceGroup = document.getElementById('stopPriceGroup');
const submitBtn = orderForm.querySelector('button[type="submit"]');

const summarySection = document.getElementById('summarySection');
const responseSection = document.getElementById('responseSection');
const loadingIndicator = document.getElementById('loadingIndicator');

const statusDot = document.getElementById('statusDot');
const statusText = document.getElementById('statusText');
const apiStatus = document.getElementById('apiStatus');

// ────────────────────────────────────────────────────────────────────────────
// State Management
// ────────────────────────────────────────────────────────────────────────────

let isOnline = false;
let isSubmitting = false;

// ────────────────────────────────────────────────────────────────────────────
// API Functions
// ────────────────────────────────────────────────────────────────────────────

/**
 * Make an API request with timeout and error handling
 */
async function apiRequest(endpoint, method = 'GET', data = null) {
    try {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            },
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT);

        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            signal: controller.signal,
        });

        clearTimeout(timeoutId);

        const responseData = await response.json();

        if (!response.ok) {
            throw new Error(
                responseData.error || 
                `API request failed with status ${response.status}`
            );
        }

        return responseData;
    } catch (error) {
        if (error.name === 'AbortError') {
            throw new Error('Request timeout. Server may be unavailable.');
        }
        throw error;
    }
}

/**
 * Check API health status
 */
async function checkApiHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`, {
            method: 'GET',
        });
        const data = await response.json();
        
        if (response.ok && data.status === 'ok') {
            setOnlineStatus(true);
            return true;
        } else {
            setOnlineStatus(false);
            return false;
        }
    } catch (error) {
        console.error('Health check failed:', error);
        setOnlineStatus(false);
        return false;
    }
}

/**
 * Update online/offline status
 */
function setOnlineStatus(online) {
    isOnline = online;
    const statusDotClass = online ? 'online' : 'offline';
    const statusTxtContent = online ? 'Connected' : 'Disconnected';
    const apiStatusContent = online ? '✅ Online' : '⚠️ Offline';

    statusDot.className = `status-dot ${statusDotClass}`;
    statusText.textContent = statusTxtContent;
    apiStatus.textContent = apiStatusContent;
    
    // Enable/disable form
    submitBtn.disabled = !online;
    if (!online) {
        submitBtn.title = 'API server is offline';
    } else {
        submitBtn.title = '';
    }
}

/**
 * Place an order via the API
 */
async function placeOrder(orderData) {
    try {
        showLoading(true);
        const response = await apiRequest('/orders/place', 'POST', orderData);
        
        if (response.success) {
            showSuccess(response);
            return true;
        } else {
            showError(response.error || 'Unknown error occurred');
            return false;
        }
    } catch (error) {
        showError(error.message);
        return false;
    } finally {
        showLoading(false);
    }
}

// ────────────────────────────────────────────────────────────────────────────
// Form Handling
// ────────────────────────────────────────────────────────────────────────────

/**
 * Handle order type change to show/hide conditional fields
 */
function handleOrderTypeChange() {
    const selectedType = typeSelect.value;

    // Reset fields
    priceGroup.style.display = 'none';
    stopPriceGroup.style.display = 'none';
    priceInput.required = false;
    stopPriceInput.required = false;

    // Show conditional fields based on order type
    if (selectedType === 'LIMIT') {
        priceGroup.style.display = 'block';
        priceInput.required = true;
    } else if (selectedType === 'STOP_MARKET') {
        stopPriceGroup.style.display = 'block';
        stopPriceInput.required = true;
    }
}

/**
 * Validate form inputs
 */
function validateForm() {
    const symbol = symbolInput.value.trim().toUpperCase();
    const side = document.querySelector('input[name="side"]:checked')?.value;
    const type = typeSelect.value;
    const quantity = quantityInput.value;
    const price = priceInput.value;
    const stopPrice = stopPriceInput.value;

    // Basic validation
    if (!symbol || !side || !type || !quantity) {
        showError('Please fill in all required fields');
        return null;
    }

    if (isNaN(quantity) || quantity <= 0) {
        showError('Quantity must be a positive number');
        return null;
    }

    if (type === 'LIMIT') {
        if (!price || isNaN(price) || price <= 0) {
            showError('Price is required and must be positive for LIMIT orders');
            return null;
        }
    }

    if (type === 'STOP_MARKET') {
        if (!stopPrice || isNaN(stopPrice) || stopPrice <= 0) {
            showError('Stop price is required and must be positive for STOP_MARKET orders');
            return null;
        }
    }

    // Return validated order data
    const orderData = {
        symbol,
        side,
        type,
        quantity: parseFloat(quantity),
    };

    if (type === 'LIMIT') {
        orderData.price = parseFloat(price);
    } else if (type === 'STOP_MARKET') {
        orderData.stopPrice = parseFloat(stopPrice);
    }

    return orderData;
}

/**
 * Update summary display
 */
function updateSummary(orderData) {
    document.getElementById('summarySymbol').textContent = orderData.symbol;
    document.getElementById('summarySide').textContent = orderData.side;
    document.getElementById('summaryType').textContent = orderData.type;
    document.getElementById('summaryQuantity').textContent = orderData.quantity;

    // Show/hide price and stopPrice in summary
    const summaryPriceItem = document.getElementById('summaryPriceItem');
    const summaryStopPriceItem = document.getElementById('summaryStopPriceItem');

    summaryPriceItem.style.display = 'none';
    summaryStopPriceItem.style.display = 'none';

    if (orderData.price) {
        document.getElementById('summaryPrice').textContent = orderData.price;
        summaryPriceItem.style.display = 'block';
    }

    if (orderData.stopPrice) {
        document.getElementById('summaryStopPrice').textContent = orderData.stopPrice;
        summaryStopPriceItem.style.display = 'block';
    }

    summarySection.style.display = 'block';
}

/**
 * Handle form submission
 */
orderForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    if (isSubmitting || !isOnline) {
        return;
    }

    const orderData = validateForm();
    if (!orderData) {
        return;
    }

    isSubmitting = true;
    submitBtn.disabled = true;

    // Show summary
    updateSummary(orderData);

    // Place order
    const success = await placeOrder(orderData);

    isSubmitting = false;
    submitBtn.disabled = false;

    if (success) {
        // Reset form after success
        setTimeout(() => resetForm(), 2000);
    }
});

// ────────────────────────────────────────────────────────────────────────────
// UI Updates
// ────────────────────────────────────────────────────────────────────────────

/**
 * Show loading indicator
 */
function showLoading(show = true) {
    loadingIndicator.style.display = show ? 'flex' : 'none';
}

/**
 * Show success message
 */
function showSuccess(response) {
    responseSection.style.display = 'block';
    const responseTitle = document.getElementById('responseTitle');
    const responseMessage = document.getElementById('responseMessage');

    responseTitle.textContent = '✅ Order Placed Successfully';
    responseTitle.className = 'card-title';

    const message = response.message || 'Your order has been placed successfully!';
    responseMessage.textContent = message;
    responseMessage.className = 'response-message';

    // Scroll to response
    setTimeout(() => {
        responseSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
}

/**
 * Show error message
 */
function showError(message) {
    responseSection.style.display = 'block';
    const responseTitle = document.getElementById('responseTitle');
    const responseMessage = document.getElementById('responseMessage');

    responseTitle.textContent = '❌ Order Failed';
    responseTitle.className = 'card-title error';

    responseMessage.textContent = message || 'An error occurred while placing the order.';
    responseMessage.className = 'response-message error';

    // Scroll to response
    setTimeout(() => {
        responseSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
}

/**
 * Reset form to initial state
 */
function resetForm() {
    orderForm.reset();
    symbolInput.focus();
    summarySection.style.display = 'none';
    responseSection.style.display = 'none';
    handleOrderTypeChange();
}

// ────────────────────────────────────────────────────────────────────────────
// Initialization
// ────────────────────────────────────────────────────────────────────────────

/**
 * Initialize the application
 */
function init() {
    // Initial health check
    checkApiHealth();

    // Periodic health checks
    setInterval(checkApiHealth, HEALTH_CHECK_INTERVAL);

    // Handle order type changes
    typeSelect.addEventListener('change', handleOrderTypeChange);

    // Auto-uppercase symbol input
    symbolInput.addEventListener('input', (e) => {
        e.target.value = e.target.value.toUpperCase();
    });

    // Focus on symbol input
    symbolInput.focus();

    console.log('🤖 Trading Bot Frontend initialized');
    console.log(`API URL: ${API_BASE_URL}`);
}

// Start when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
