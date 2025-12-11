// Global variables
let allStocks = [];
const API_BASE = '/api';

// DOM Elements
const stocksBody = document.getElementById('stocksBody');
const loadingIndicator = document.getElementById('loadingIndicator');
const refreshBtn = document.getElementById('refreshBtn');
const probabilityFilter = document.getElementById('probabilityFilter');
const probabilityValue = document.getElementById('probabilityValue');
const detailsModal = document.getElementById('detailsModal');
const closeBtn = document.querySelector('.close');
const lastUpdate = document.getElementById('lastUpdate');

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    loadTopStocks();
    
    refreshBtn.addEventListener('click', () => {
        loadTopStocks(true);
    });
    
    probabilityFilter.addEventListener('change', (e) => {
        probabilityValue.textContent = e.target.value + '%';
        filterAndDisplayStocks();
    });
    
    closeBtn.addEventListener('click', () => {
        detailsModal.style.display = 'none';
    });
    
    window.addEventListener('click', (e) => {
        if (e.target === detailsModal) {
            detailsModal.style.display = 'none';
        }
    });
});

/**
 * Load top stocks from API
 */
async function loadTopStocks(refresh = false) {
    try {
        showLoading(true);
        const minProbability = parseFloat(probabilityFilter.value);
        
        const url = `${API_BASE}/top-stocks?min_probability=${minProbability}&refresh=${refresh}`;
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            allStocks = result.data;
            displayStocks(allStocks);
            updateLastUpdate(result.timestamp);
            
            if (refresh) {
                showNotification('Data refreshed successfully!', 'success');
            }
        } else {
            throw new Error(result.error || 'Failed to load stocks');
        }
    } catch (error) {
        console.error('Error loading stocks:', error);
        showNotification('Error loading stocks: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

/**
 * Display stocks in table
 */
function displayStocks(stocks) {
    stocksBody.innerHTML = '';
    
    if (!stocks || stocks.length === 0) {
        stocksBody.innerHTML = '<tr><td colspan="13" class="text-center">No stocks found matching criteria</td></tr>';
        return;
    }
    
    stocks.forEach((stock, index) => {
        const row = createStockRow(stock, index + 1);
        stocksBody.appendChild(row);
    });
}

/**
 * Create a table row for a stock
 */
function createStockRow(stock, rank) {
    const row = document.createElement('tr');
    
    const probabilityScore = parseFloat(stock.probability_score);
    const probabilityClass = getProbabilityClass(probabilityScore);
    
    row.innerHTML = `
        <td class="text-center font-bold">${rank}</td>
        <td class="ticker">${stock.ticker}</td>
        <td class="company-name">${stock.name}</td>
        <td>${stock.sector}</td>
        <td class="price">${stock.current_price}</td>
        <td class="price">${stock.entry_price}</td>
        <td class="price negative">${stock.stop_loss}</td>
        <td class="price positive">${stock.target_price}</td>
        <td class="text-right">${stock.rr_ratio}</td>
        <td>${stock.entry_time}</td>
        <td class="text-center swing-score">${stock.swing_score}</td>
        <td class="text-center probability ${probabilityClass}">${stock.probability_score}</td>
        <td class="text-center">
            <div class="action-buttons">
                <button class="action-btn action-btn-info" onclick="showStockDetails('${stock.ticker}')">
                    <i class="fas fa-info-circle"></i> Details
                </button>
                <button class="action-btn action-btn-watch" onclick="addToWatchlist('${stock.ticker}')">
                    <i class="fas fa-star"></i> Watch
                </button>
            </div>
        </td>
    `;
    
    return row;
}

/**
 * Get probability badge class based on score
 */
function getProbabilityClass(score) {
    if (score >= 70) return 'high-probability';
    if (score >= 50) return 'medium-probability';
    return 'low-probability';
}

/**
 * Show stock details in modal
 */
async function showStockDetails(ticker) {
    try {
        showLoading(true);
        const response = await fetch(`${API_BASE}/stock/${ticker}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            const stock = result.data;
            const modalBody = document.getElementById('modalBody');
            
            modalBody.innerHTML = `
                <h2>${stock.ticker} - ${stock.name}</h2>
                <p class="subtitle mb-20">Sector: ${stock.sector}</p>
                
                <div class="modal-details">
                    <div class="detail-section">
                        <h3><i class="fas fa-chart-bar"></i> Price Information</h3>
                        <div class="detail-item">
                            <label>Current Price:</label>
                            <value>${stock.current_price}</value>
                        </div>
                        <div class="detail-item">
                            <label>Entry Price:</label>
                            <value>${stock.entry_price}</value>
                        </div>
                        <div class="detail-item">
                            <label>Stop Loss:</label>
                            <value>${stock.stop_loss}</value>
                        </div>
                        <div class="detail-item">
                            <label>Target Price:</label>
                            <value>${stock.target_price}</value>
                        </div>
                        <div class="detail-item">
                            <label>Support Level:</label>
                            <value>${stock.support}</value>
                        </div>
                        <div class="detail-item">
                            <label>Resistance Level:</label>
                            <value>${stock.resistance}</value>
                        </div>
                    </div>
                    
                    <div class="detail-section">
                        <h3><i class="fas fa-bullseye"></i> Trade Setup</h3>
                        <div class="detail-item">
                            <label>Risk Amount:</label>
                            <value>${stock.risk}</value>
                        </div>
                        <div class="detail-item">
                            <label>Reward Amount:</label>
                            <value>${stock.reward}</value>
                        </div>
                        <div class="detail-item">
                            <label>Risk/Reward Ratio:</label>
                            <value>${stock.rr_ratio}</value>
                        </div>
                        <div class="detail-item">
                            <label>Entry Time:</label>
                            <value>${stock.entry_time}</value>
                        </div>
                    </div>
                    
                    <div class="detail-section">
                        <h3><i class="fas fa-star"></i> Technical Indicators</h3>
                        <div class="detail-item">
                            <label>RSI:</label>
                            <value>${stock.rsi}</value>
                        </div>
                        <div class="detail-item">
                            <label>MACD:</label>
                            <value>${stock.macd}</value>
                        </div>
                        <div class="detail-item">
                            <label>Swing Score:</label>
                            <value>${stock.swing_score}/100</value>
                        </div>
                        <div class="detail-item">
                            <label>P/E Ratio:</label>
                            <value>${stock.pe_ratio}</value>
                        </div>
                    </div>
                    
                    <div class="detail-section">
                        <h3><i class="fas fa-percentage"></i> Probability Analysis</h3>
                        <div class="detail-item">
                            <label>Win Probability:</label>
                            <value>${stock.probability_score}</value>
                        </div>
                        <h4 style="margin-top: 15px; margin-bottom: 10px;">Why This Stock?</h4>
                        <ul class="reason-list">
                            ${stock.reasons.map(reason => `<li>${reason}</li>`).join('')}
                        </ul>
                    </div>
                </div>
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid var(--border-color);">
                    <h4>Disclaimer</h4>
                    <p style="font-size: 12px; color: var(--secondary-color); margin-top: 10px;">
                        This analysis is for educational purposes only. Always conduct your own research and consult with a 
                        financial advisor before making trading decisions. Past performance is not indicative of future results.
                        The market can be unpredictable, and losses are possible.
                    </p>
                </div>
            `;
            
            detailsModal.style.display = 'block';
        } else {
            throw new Error(result.error || 'Failed to load stock details');
        }
    } catch (error) {
        console.error('Error loading stock details:', error);
        showNotification('Error loading details: ' + error.message, 'error');
    } finally {
        showLoading(false);
    }
}

/**
 * Add stock to watchlist
 */
async function addToWatchlist(ticker) {
    try {
        const response = await fetch(`${API_BASE}/watchlist`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ ticker })
        });
        
        const result = await response.json();
        
        if (result.success) {
            showNotification(`${ticker} added to watchlist!`, 'success');
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        console.error('Error adding to watchlist:', error);
        showNotification('Error adding to watchlist: ' + error.message, 'error');
    }
}

/**
 * Filter and display stocks
 */
function filterAndDisplayStocks() {
    const minProbability = parseFloat(probabilityFilter.value);
    const filtered = allStocks.filter(stock => {
        const prob = parseFloat(stock.probability_score);
        return prob >= minProbability;
    });
    displayStocks(filtered);
}

/**
 * Show/hide loading indicator
 */
function showLoading(show) {
    loadingIndicator.style.display = show ? 'block' : 'none';
}

/**
 * Show notification
 */
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#1e40af'};
        color: white;
        border-radius: 6px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        z-index: 10000;
        animation: slideIn 0.3s ease;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

/**
 * Update last update time
 */
function updateLastUpdate(timestamp) {
    const date = new Date(timestamp);
    const timeString = date.toLocaleTimeString();
    const dateString = date.toLocaleDateString();
    lastUpdate.textContent = `${dateString} ${timeString}`;
}

/**
 * Add fadeOut animation
 */
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeOut {
        from { opacity: 1; transform: translateY(0); }
        to { opacity: 0; transform: translateY(-10px); }
    }
`;
document.head.appendChild(style);
