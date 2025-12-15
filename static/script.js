// API configuration
const API_BASE = '/api';
let currentStocks = [];

// Metric definitions for tooltips
const METRIC_INFO = {
    'Ticker': 'Stock Symbol: BSE/NSE stock ticker code (e.g., RELIANCE.BO)',
    'Current Price': 'Current Market Price: Latest trading price of the stock',
    'Entry': 'Entry Price: Recommended price to buy the stock based on technical analysis',
    'Stop Loss': 'Stop Loss Price: Exit point to limit losses if trade goes wrong. Risk management tool',
    'Target': 'Target Price: Expected price level to sell for profit',
    'Risk/Reward': 'Risk-Reward Ratio: Expected reward divided by risk. Higher is better (e.g., 2:1 means ₹2 gain for every ₹1 risk)',
    'Swing Score': 'Overall trading score (0-100): Combines multiple technical indicators. Higher = Better opportunity',
    'Probability': 'Success probability (%): Statistical likelihood of reaching target price based on technical analysis',
    'RSI': 'Relative Strength Index (0-100): Measures momentum. Below 30 = Oversold (Buy signal), Above 70 = Overbought (Sell signal)',
    'MACD': 'Moving Average Convergence Divergence: Trend indicator. Positive = Bullish, Negative = Bearish',
    'Support': 'Support Level: Price floor where stock tends to bounce back up. Good entry point',
    'Resistance': 'Resistance Level: Price ceiling where stock tends to fall back down. Target/exit point',
    'Entry Time': 'Best Entry Timing: When to enter the trade for optimal results',
    'Risk': 'Potential Loss: Amount you could lose if stop loss is hit',
    'Reward': 'Potential Gain: Amount you could gain if target is reached'
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    loadStocks(false);
    setupEventListeners();
    initializeTooltips();
});

// Setup event listeners
function setupEventListeners() {
    document.getElementById('refreshBtn').addEventListener('click', () => {
        loadStocks(true);
    });

    document.getElementById('probabilityFilter').addEventListener('change', (e) => {
        document.getElementById('probabilityValue').textContent = e.target.value + '%';
        loadStocks(true);
    });

    document.getElementById('countFilter').addEventListener('change', () => {
        loadStocks(false);
    });

    // Close modal when clicking outside
    document.getElementById('stockModal').addEventListener('click', (e) => {
        if (e.target.id === 'stockModal') {
            closeModal();
        }
    });
}

// Load stocks from API
async function loadStocks(refresh) {
    const minProb = document.getElementById('probabilityFilter').value;
    const count = document.getElementById('countFilter').value;

    showLoading(true);
    hideAllMessages();

    try {
        const url = `${API_BASE}/top-stocks?min_probability=${minProb}&count=${count}&refresh=${refresh}`;

        // Set timeout for mobile browsers
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 second timeout

        const response = await fetch(url, { signal: controller.signal });
        clearTimeout(timeoutId);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        showLoading(false);

        if (data.success) {
            currentStocks = data.data || [];
            displayStocks(data);
            showStatus(data);
        } else {
            showError(data.error || 'Unknown error occurred');
            console.error('API Error:', data);
        }
    } catch (error) {
        showLoading(false);
        if (error.name === 'AbortError') {
            showError('Request timeout. Please try again or reduce the number of stocks.');
        } else {
            showError(`Failed to load data: ${error.message}`);
        }
        console.error('Fetch error:', error);
    }
}

// Display stocks in table
function displayStocks(data) {
    const tbody = document.getElementById('stocksBody');
    const emptyState = document.getElementById('emptyState');

    if (!currentStocks || currentStocks.length === 0) {
        tbody.innerHTML = '';
        emptyState.style.display = 'block';
        document.getElementById('stocksContainer').style.display = 'none';
        return;
    }

    document.getElementById('stocksContainer').style.display = 'block';
    emptyState.style.display = 'none';

    // Use DocumentFragment for better performance
    const fragment = document.createDocumentFragment();

    currentStocks.forEach((stock, index) => {
        const probability = parseFloat(stock.probability_score);
        let probClass = 'probability-low';
        if (probability >= 70) probClass = 'probability-high';
        else if (probability >= 55) probClass = 'probability-medium';

        const row = document.createElement('tr');
        row.onclick = () => showStockDetails(index);
        row.innerHTML = `
            <td><span class="ticker-cell">${stock.ticker || 'N/A'}</span></td>
            <td class="price-cell">${stock.current_price || 'N/A'}</td>
            <td class="price-cell">${stock.entry_price || 'N/A'}</td>
            <td class="price-cell">${stock.stop_loss || 'N/A'}</td>
            <td class="price-cell">${stock.target_price || 'N/A'}</td>
            <td>${stock.rr_ratio || 'N/A'}</td>
            <td>${stock.swing_score || 'N/A'}/100</td>
            <td><span class="probability-score ${probClass}">${stock.probability_score || 'N/A'}</span></td>
        `;
        fragment.appendChild(row);
    });

    // Clear and append in one operation
    tbody.innerHTML = '';
    tbody.appendChild(fragment);
}

// Show stock details modal
function showStockDetails(index) {
    try {
        const stock = currentStocks[index];
        if (!stock) return;

        // Safely set text content with fallback values
        const setText = (id, value) => {
            const element = document.getElementById(id);
            if (element) element.textContent = value || 'N/A';
        };

        setText('modalTicker', stock.ticker);
        setText('modalCurrentPrice', stock.current_price);
        setText('modalEntryPrice', stock.entry_price);
        setText('modalStopLoss', stock.stop_loss);
        setText('modalTargetPrice', stock.target_price);
        setText('modalRisk', stock.risk);
        setText('modalReward', stock.reward);
        setText('modalRRatio', stock.rr_ratio);
        setText('modalSupport', stock.support);
        setText('modalResistance', stock.resistance);
        setText('modalRSI', stock.rsi);
        setText('modalMACD', stock.macd);
        setText('modalSwingScore', (stock.swing_score || 'N/A') + (stock.swing_score ? '/100' : ''));
        setText('modalProbability', stock.probability_score);
        setText('modalEntryTime', stock.entry_time);

        document.getElementById('stockModal').classList.add('show');
    } catch (error) {
        console.error('Error showing stock details:', error);
    }
}

// Close modal
function closeModal() {
    document.getElementById('stockModal').classList.remove('show');
}

// Show loading indicator
function showLoading(show) {
    document.getElementById('loadingIndicator').style.display = show ? 'block' : 'none';
}

// Format date to IST
function formatToIST(dateString) {
    const date = new Date(dateString);
    // Convert to IST (UTC+5:30)
    return date.toLocaleString('en-IN', {
        timeZone: 'Asia/Kolkata',
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: true
    }) + ' IST';
}

// Show status message
function showStatus(data) {
    const statusBox = document.getElementById('statusBox');
    const lastUpdate = document.getElementById('lastUpdate');
    const warningBox = document.getElementById('warningBox');

    if (data.timestamp) {
        lastUpdate.textContent = formatToIST(data.timestamp);
    }

    statusBox.style.display = 'flex';

    // Handle demo data message
    if (data.is_demo) {
        warningBox.style.display = 'flex';
        document.getElementById('warningMessage').textContent = 
            'Showing demo data. Click "Refresh Data" to fetch live market data.';
    }
    // Handle cached data message
    else if (data.from_cache) {
        warningBox.style.display = 'flex';
        document.getElementById('warningMessage').textContent =
            `Using cached data (${data.total_cached || data.count} stocks fetched on ${formatToIST(data.timestamp)})`;
    }
    // Handle any other messages
    else if (data.message) {
        warningBox.style.display = 'flex';
        document.getElementById('warningMessage').textContent = data.message;
    }
}

// Show error message
function showError(errorMessage) {
    const errorBox = document.getElementById('errorBox');
    document.getElementById('errorTitle').textContent = 'Failed to Load Real Data';
    document.getElementById('errorMessage').textContent = errorMessage;
    errorBox.style.display = 'flex';
    document.getElementById('stocksContainer').style.display = 'none';
    document.getElementById('emptyState').style.display = 'block';
}

// Hide all message boxes
function hideAllMessages() {
    document.getElementById('statusBox').style.display = 'none';
    document.getElementById('errorBox').style.display = 'none';
    document.getElementById('warningBox').style.display = 'none';
}

// Initialize tooltips
function initializeTooltips() {
    // Check if already initialized to prevent duplicates
    if (document.getElementById('metric-tooltip')) {
        return;
    }

    // Create tooltip element
    const tooltip = document.createElement('div');
    tooltip.id = 'metric-tooltip';
    tooltip.style.cssText = `
        position: fixed;
        background: rgba(0, 0, 0, 0.95);
        color: #fff;
        padding: 12px 16px;
        border-radius: 8px;
        font-size: 0.9em;
        max-width: 350px;
        z-index: 10000;
        pointer-events: none;
        opacity: 0;
        transition: opacity 0.2s ease;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
        line-height: 1.5;
    `;
    document.body.appendChild(tooltip);

    // Add info icons to table headers (only once)
    setTimeout(() => {
        document.querySelectorAll('th').forEach(th => {
            // Skip if already has info icon
            if (th.querySelector('.info-icon')) return;

            const text = th.textContent.trim();
            if (METRIC_INFO[text]) {
                th.innerHTML = `
                    ${text}
                    <i class="info-icon" data-metric="${text}" style="
                        display: inline-block;
                        width: 16px;
                        height: 16px;
                        border-radius: 50%;
                        background: rgba(102, 126, 234, 0.3);
                        color: #667eea;
                        font-size: 11px;
                        line-height: 16px;
                        text-align: center;
                        margin-left: 4px;
                        cursor: help;
                        font-style: normal;
                        font-weight: bold;
                        border: 1px solid rgba(102, 126, 234, 0.5);
                    ">i</i>
                `;
            }
        });
    }, 100);

    // Use event delegation for better performance
    let tooltipTimeout;
    document.body.addEventListener('mouseover', (e) => {
        if (e.target.classList.contains('info-icon')) {
            clearTimeout(tooltipTimeout);
            const metric = e.target.getAttribute('data-metric');
            const info = METRIC_INFO[metric];
            if (info) {
                tooltip.textContent = info;
                tooltip.style.opacity = '1';
                positionTooltip(e, tooltip);
            }
        }
    }, true);

    document.body.addEventListener('mouseout', (e) => {
        if (e.target.classList.contains('info-icon')) {
            tooltipTimeout = setTimeout(() => {
                tooltip.style.opacity = '0';
            }, 100);
        }
    }, true);
}

// Position tooltip near cursor
function positionTooltip(e, tooltip) {
    const offset = 15;
    let left = e.pageX + offset;
    let top = e.pageY + offset;

    // Prevent tooltip from going off-screen
    const tooltipRect = tooltip.getBoundingClientRect();
    if (left + tooltipRect.width > window.innerWidth) {
        left = e.pageX - tooltipRect.width - offset;
    }
    if (top + tooltipRect.height > window.innerHeight) {
        top = e.pageY - tooltipRect.height - offset;
    }

    tooltip.style.left = left + 'px';
    tooltip.style.top = top + 'px';
}

// Close modal on Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeModal();
    }
});
