'use client';

import { useState, useEffect } from 'react';
import { fetchTopStocks, StockData } from '@/lib/api';
import StockCard from '@/components/StockCard';
import LoadingSkeleton from '@/components/LoadingSkeleton';

export default function Home() {
  const [stocks, setStocks] = useState<StockData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [limit, setLimit] = useState(10);
  const [minProbability, setMinProbability] = useState(40);
  const [lastUpdated, setLastUpdated] = useState<string>('');
  const [fromCache, setFromCache] = useState(false);

  const loadStocks = async (refresh: boolean = false) => {
    setLoading(true);
    setError(null);

    const response = await fetchTopStocks(limit, minProbability, refresh);

    if (response.success) {
      // Deduplicate stocks by ticker (keep first occurrence)
      const uniqueStocks = response.data.filter(
        (stock, index, self) =>
          index === self.findIndex((s) => s.ticker === stock.ticker)
      );
      setStocks(uniqueStocks);
      setLastUpdated(new Date(response.timestamp).toLocaleString());
      setFromCache(response.from_cache);
      setError(null);
    } else {
      setError(response.error || 'Failed to fetch stocks');
      setStocks([]);
    }

    setLoading(false);
  };

  useEffect(() => {
    loadStocks();
  }, [limit, minProbability]);

  const handleRefresh = () => {
    loadStocks(true);
  };

  return (
    <div className="min-h-screen bg-white dark:bg-black">
      {/* Header */}
      <header className="border-b border-gray-200 dark:border-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-3xl font-bold tracking-tight">Swing Trading Analyzer</h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            AI-powered stock predictions for swing trading with optimal entry and exit points
          </p>
        </div>
      </header>

      {/* Controls */}
      <div className="border-b border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-950">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-wrap items-center gap-4">
            {/* Number of Stocks */}
            <div className="flex items-center gap-2">
              <label htmlFor="limit" className="text-sm font-medium">
                Stocks:
              </label>
              <select
                id="limit"
                value={limit}
                onChange={(e) => setLimit(Number(e.target.value))}
                className="border border-gray-300 dark:border-gray-700 rounded-md px-3 py-1.5 text-sm bg-white dark:bg-black focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value={5}>5</option>
                <option value={10}>10</option>
                <option value={15}>15</option>
                <option value={20}>20</option>
                <option value={25}>25</option>
                <option value={30}>30</option>
              </select>
            </div>

            {/* Min Probability */}
            <div className="flex items-center gap-2">
              <label htmlFor="probability" className="text-sm font-medium">
                Min Probability:
              </label>
              <select
                id="probability"
                value={minProbability}
                onChange={(e) => setMinProbability(Number(e.target.value))}
                className="border border-gray-300 dark:border-gray-700 rounded-md px-3 py-1.5 text-sm bg-white dark:bg-black focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value={30}>30%</option>
                <option value={40}>40%</option>
                <option value={50}>50%</option>
                <option value={60}>60%</option>
                <option value={70}>70%</option>
              </select>
            </div>

            {/* Refresh Button */}
            <button
              onClick={handleRefresh}
              disabled={loading}
              className="ml-auto border border-gray-300 dark:border-gray-700 rounded-md px-4 py-1.5 text-sm font-medium hover:bg-gray-100 dark:hover:bg-gray-900 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Loading...' : 'Refresh'}
            </button>

            {/* Last Updated */}
            {lastUpdated && (
              <div className="text-xs text-gray-500">
                Updated: {lastUpdated}
                {fromCache && <span className="ml-2">(cached)</span>}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 p-4 border border-red-200 dark:border-red-900 bg-red-50 dark:bg-red-950 rounded-lg">
            <h3 className="font-semibold text-red-900 dark:text-red-200 mb-1">Error</h3>
            <p className="text-sm text-red-700 dark:text-red-300">{error}</p>
            <p className="text-xs text-red-600 dark:text-red-400 mt-2">
              Make sure the Flask backend is running on http://localhost:5000
            </p>
          </div>
        )}

        {loading ? (
          <LoadingSkeleton />
        ) : stocks.length === 0 ? (
          <div className="text-center py-12">
            <h3 className="text-lg font-semibold mb-2">No stocks found</h3>
            <p className="text-gray-600 dark:text-gray-400">
              Try adjusting your filters or check back later
            </p>
          </div>
        ) : (
          <>
            <div className="mb-6">
              <h2 className="text-xl font-semibold">
                Top {stocks.length} Stocks for Swing Trading
              </h2>
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                Ranked by probability of hitting target price
              </p>
            </div>

            <div className="space-y-2">
              {stocks.map((stock, index) => (
                <StockCard key={`${stock.ticker}-${index}`} stock={stock} rank={index + 1} />
              ))}
            </div>
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 dark:border-gray-800 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-sm text-gray-600 dark:text-gray-400">
            <p className="font-semibold mb-2">Risk Disclaimer</p>
            <p className="text-xs">
              This tool is for educational and analytical purposes only. It is NOT financial advice.
              Stock market trading involves substantial risk. You can lose more than your initial investment.
              Always conduct your own research and consult with a licensed financial advisor before trading.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
