// API configuration
const API_BASE = '/api';
let currentStocks = [];

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    loadStocks(false);
    setupEventListeners();
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

// Show status message
function showStatus(data) {
    const statusBox = document.getElementById('statusBox');
    const lastUpdate = document.getElementById('lastUpdate');

    if (data.timestamp) {
        const date = new Date(data.timestamp);
        lastUpdate.textContent = date.toLocaleString();
    }

    statusBox.style.display = 'flex';

    if (data.from_cache) {
        const warningBox = document.getElementById('warningBox');
        warningBox.style.display = 'flex';
        document.getElementById('warningMessage').textContent = 
            `Using cached data (${data.total_cached || data.count} stocks fetched on ${new Date(data.timestamp).toLocaleString()})`;
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

// Close modal on Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeModal();
    }
});
