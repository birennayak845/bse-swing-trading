'use client';

import { useState } from 'react';
import { StockData } from '@/lib/api';

interface StockCardProps {
  stock: StockData;
  rank: number;
}

export default function StockCard({ stock, rank }: StockCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const probabilityScore = parseFloat(stock.probability_score);
  const swingScore = parseFloat(stock.swing_score);
  const rsi = typeof stock.rsi === 'string' ? parseFloat(stock.rsi) : stock.rsi;

  return (
    <div
      onClick={() => setIsExpanded(!isExpanded)}
      className="border border-gray-200 dark:border-gray-800 rounded-lg p-4 hover:border-gray-300 dark:hover:border-gray-700 transition-all cursor-pointer hover:shadow-md"
    >
      {/* Compact Header - Always Visible */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3 flex-1">
          <span className="text-lg font-bold text-gray-400">#{rank}</span>
          <div className="flex-1">
            <h3 className="font-semibold text-base">{stock.name || stock.ticker}</h3>
            <p className="text-xs text-gray-500">{stock.ticker}</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="text-right">
            <div className="text-xs text-gray-500">Entry</div>
            <div className="text-sm font-semibold">{stock.entry_price}</div>
          </div>
          <div className="text-right">
            <div className="text-xs text-gray-500">Target</div>
            <div className="text-sm font-semibold text-green-600">{stock.target_price}</div>
          </div>
          <div className="text-right">
            <div className={`text-lg font-bold ${
              probabilityScore >= 70 ? 'text-green-600' :
              probabilityScore >= 50 ? 'text-yellow-600' :
              'text-orange-600'
            }`}>
              {stock.probability_score}
            </div>
          </div>
          <div className="text-gray-400">
            <svg
              className={`w-5 h-5 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </div>
      </div>

      {/* Expanded Details */}
      {isExpanded && (
        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700 space-y-4">
          {/* Price Information */}
          <div className="grid grid-cols-3 gap-3">
            <div className="bg-gray-50 dark:bg-gray-900 rounded p-3">
              <div className="text-xs text-gray-500 uppercase mb-1">Current</div>
              <div className="text-sm font-semibold">{stock.current_price}</div>
            </div>
            <div className="bg-green-50 dark:bg-green-950 rounded p-3">
              <div className="text-xs text-gray-500 uppercase mb-1">Target</div>
              <div className="text-sm font-semibold text-green-600">{stock.target_price}</div>
              <div className="text-xs text-green-600 mt-1">+{stock.reward}</div>
            </div>
            <div className="bg-red-50 dark:bg-red-950 rounded p-3">
              <div className="text-xs text-gray-500 uppercase mb-1">Stop Loss</div>
              <div className="text-sm font-semibold text-red-600">{stock.stop_loss}</div>
              <div className="text-xs text-red-600 mt-1">-{stock.risk}</div>
            </div>
          </div>

          {/* Technical Indicators */}
          <div className="grid grid-cols-4 gap-3 text-xs">
            <div className="text-center">
              <div className="text-gray-500 mb-1">RSI</div>
              <div className={`font-bold text-sm ${
                rsi < 30 ? 'text-green-600' :
                rsi > 70 ? 'text-red-600' :
                'text-gray-600'
              }`}>
                {isNaN(rsi) ? 'N/A' : rsi.toFixed(1)}
              </div>
            </div>
            <div className="text-center">
              <div className="text-gray-500 mb-1">Swing Score</div>
              <div className="font-bold text-sm">{swingScore.toFixed(1)}</div>
            </div>
            <div className="text-center">
              <div className="text-gray-500 mb-1">R:R Ratio</div>
              <div className="font-bold text-sm">{stock.rr_ratio}</div>
            </div>
            <div className="text-center">
              <div className="text-gray-500 mb-1">Sector</div>
              <div className="font-medium text-xs truncate">{stock.sector || 'N/A'}</div>
            </div>
          </div>

          {/* Support & Resistance */}
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-blue-50 dark:bg-blue-950 rounded p-2">
              <div className="text-xs text-gray-500 mb-1">Support</div>
              <div className="font-semibold text-sm">{stock.support}</div>
            </div>
            <div className="bg-purple-50 dark:bg-purple-950 rounded p-2">
              <div className="text-xs text-gray-500 mb-1">Resistance</div>
              <div className="font-semibold text-sm">{stock.resistance}</div>
            </div>
          </div>

          {/* Entry Timing */}
          <div className="bg-gray-50 dark:bg-gray-900 rounded p-3">
            <div className="text-xs text-gray-500 uppercase mb-1">Entry Timing</div>
            <div className="text-sm font-medium">{stock.entry_time}</div>
          </div>
        </div>
      )}
    </div>
  );
}
