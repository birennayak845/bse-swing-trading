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
        const response = await fetch(url);
        const data = await response.json();

        showLoading(false);

        if (data.success) {
            currentStocks = data.data;
            displayStocks(data);
            showStatus(data);
        } else {
            showError(data.error);
            console.error('API Error:', data);
        }
    } catch (error) {
        showLoading(false);
        showError(`Network error: ${error.message}`);
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

    tbody.innerHTML = currentStocks.map((stock, index) => {
        const probability = parseFloat(stock.probability_score);
        let probClass = 'probability-low';
        if (probability >= 70) probClass = 'probability-high';
        else if (probability >= 55) probClass = 'probability-medium';

        return `
            <tr onclick="showStockDetails(${index})">
                <td><span class="ticker-cell">${stock.ticker}</span></td>
                <td class="price-cell">${stock.current_price}</td>
                <td class="price-cell">${stock.entry_price}</td>
                <td class="price-cell">${stock.stop_loss}</td>
                <td class="price-cell">${stock.target_price}</td>
                <td>${stock.rr_ratio}</td>
                <td>${stock.swing_score}/100</td>
                <td><span class="probability-score ${probClass}">${stock.probability_score}</span></td>
            </tr>
        `;
    }).join('');
}

// Show stock details modal
function showStockDetails(index) {
    const stock = currentStocks[index];
    if (!stock) return;

    document.getElementById('modalTicker').textContent = stock.ticker;
    document.getElementById('modalCurrentPrice').textContent = stock.current_price;
    document.getElementById('modalEntryPrice').textContent = stock.entry_price;
    document.getElementById('modalStopLoss').textContent = stock.stop_loss;
    document.getElementById('modalTargetPrice').textContent = stock.target_price;
    document.getElementById('modalRisk').textContent = stock.risk;
    document.getElementById('modalReward').textContent = stock.reward;
    document.getElementById('modalRRatio').textContent = stock.rr_ratio;
    document.getElementById('modalSupport').textContent = stock.support;
    document.getElementById('modalResistance').textContent = stock.resistance;
    document.getElementById('modalRSI').textContent = stock.rsi;
    document.getElementById('modalMACD').textContent = stock.macd;
    document.getElementById('modalSwingScore').textContent = stock.swing_score + '/100';
    document.getElementById('modalProbability').textContent = stock.probability_score;
    document.getElementById('modalEntryTime').textContent = stock.entry_time;

    document.getElementById('stockModal').classList.add('show');
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

    // Add info icons to table headers
    document.querySelectorAll('th').forEach(th => {
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

    // Add hover listeners to info icons
    document.addEventListener('mouseover', (e) => {
        if (e.target.classList.contains('info-icon')) {
            const metric = e.target.getAttribute('data-metric');
            const info = METRIC_INFO[metric];
            if (info) {
                tooltip.textContent = info;
                tooltip.style.opacity = '1';
                positionTooltip(e, tooltip);
            }
        }
    });

    document.addEventListener('mousemove', (e) => {
        if (e.target.classList.contains('info-icon') && tooltip.style.opacity === '1') {
            positionTooltip(e, tooltip);
        }
    });

    document.addEventListener('mouseout', (e) => {
        if (e.target.classList.contains('info-icon')) {
            tooltip.style.opacity = '0';
        }
    });
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
