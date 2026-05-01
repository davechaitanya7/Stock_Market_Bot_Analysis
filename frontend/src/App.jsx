import React, { useState, useEffect } from 'react';
import { Search, TrendingUp, Activity, Briefcase, List, Bell, Plus, X, Check, XCircle } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import * as api from './api/client';

// Signal badge component
function SignalBadge({ signal }) {
  const signalClass = `signal-${signal.toLowerCase().replace('_', '-')}`;
  return (
    <span className={`px-3 py-1 rounded-full text-sm font-semibold border ${signalClass}`}>
      {signal.replace('_', ' ')}
    </span>
  );
}

// Market indices component
function MarketIndices({ indices }) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
      {Object.entries(indices).map(([name, data]) => (
        <div key={name} className="card-gradient rounded-xl p-4 border border-slate-700">
          <p className="text-slate-400 text-sm">{name}</p>
          <p className="text-xl font-bold mt-1">{data.value?.toLocaleString('en-IN')}</p>
          <p className={`text-sm mt-1 ${data.change >= 0 ? 'text-bull' : 'text-bear'}`}>
            {data.change >= 0 ? '+' : ''}{data.change?.toFixed(2)} ({data.change_percent?.toFixed(2)}%)
          </p>
        </div>
      ))}
    </div>
  );
}

// Stock chart component
function StockChart({ data, symbol }) {
  const chartData = data?.historical_data?.slice(-30)?.map(d => ({
    date: new Date(d.date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' }),
    price: d.close
  })) || [];

  return (
    <div className="card-gradient rounded-xl p-6 border border-slate-700">
      <h3 className="text-lg font-semibold mb-4">{symbol} Price Chart</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.3}/>
                <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="date" stroke="#64748b" fontSize={12} />
            <YAxis stroke="#64748b" fontSize={12} domain={['auto', 'auto']} />
            <Tooltip
              contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
              labelStyle={{ color: '#94a3b8' }}
            />
            <Area type="monotone" dataKey="price" stroke="#0ea5e9" fillOpacity={1} fill="url(#colorPrice)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

// Analysis panel component
function AnalysisPanel({ analysis }) {
  if (!analysis) return null;

  const { technical_indicators: ti, trading_signal: ts } = analysis;

  return (
    <div className="card-gradient rounded-xl p-6 border border-slate-700">
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <Activity className="w-5 h-5" />
        AI Analysis
      </h3>

      {/* Trading Signal */}
      <div className="mb-6 p-4 bg-slate-800/50 rounded-lg">
        <div className="flex items-center justify-between mb-2">
          <span className="text-slate-400">Signal</span>
          <SignalBadge signal={ts.signal} />
        </div>
        <div className="flex items-center justify-between">
          <span className="text-slate-400">Confidence</span>
          <div className="flex items-center gap-2">
            <div className="w-32 h-2 bg-slate-700 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full ${ts.confidence > 60 ? 'bg-green-500' : ts.confidence > 40 ? 'bg-yellow-500' : 'bg-red-500'}`}
                style={{ width: `${ts.confidence}%` }}
              />
            </div>
            <span className="text-white font-medium">{ts.confidence}%</span>
          </div>
        </div>
      </div>

      {/* Reasons */}
      <div className="mb-6">
        <h4 className="text-sm font-medium text-slate-400 mb-2">Analysis Reasons</h4>
        <ul className="space-y-1">
          {ts.reasons.map((reason, idx) => (
            <li key={idx} className="text-sm text-slate-300 flex items-start gap-2">
              <span className="text-primary-500 mt-0.5">•</span>
              {reason}
            </li>
          ))}
        </ul>
      </div>

      {/* Technical Indicators */}
      <div className="grid grid-cols-2 gap-4">
        <div className="p-3 bg-slate-800/50 rounded-lg">
          <p className="text-xs text-slate-400">RSI (14)</p>
          <p className={`text-lg font-bold ${ti.rsi.signal === 'BUY' ? 'text-bull' : ti.rsi.signal === 'SELL' ? 'text-bear' : 'text-white'}`}>
            {ti.rsi.value || 'N/A'}
          </p>
          <p className="text-xs text-slate-500">{ti.rsi.interpretation}</p>
        </div>
        <div className="p-3 bg-slate-800/50 rounded-lg">
          <p className="text-xs text-slate-400">MACD</p>
          <p className={`text-lg font-bold ${ti.macd.signal_type.signal === 'BULLISH' || ti.macd.signal_type.signal === 'BUY' ? 'text-bull' : 'text-bear'}`}>
            {ti.macd.signal_type.signal}
          </p>
          <p className="text-xs text-slate-500">Histogram: {ti.macd.histogram?.toFixed(4)}</p>
        </div>
        <div className="p-3 bg-slate-800/50 rounded-lg">
          <p className="text-xs text-slate-400">SMA 50</p>
          <p className="text-lg font-bold text-white">{ti.moving_averages.sma_50 || 'N/A'}</p>
          <p className={`text-xs ${ti.moving_averages.price_vs_sma50 === 'BULLISH' ? 'text-bull' : 'text-bear'}`}>
            {ti.moving_averages.price_vs_sma50}
          </p>
        </div>
        <div className="p-3 bg-slate-800/50 rounded-lg">
          <p className="text-xs text-slate-400">Bollinger</p>
          <p className="text-lg font-bold text-white">{ti.bollinger_bands.position.replace('_', ' ')}</p>
          <p className="text-xs text-slate-500">Band position</p>
        </div>
      </div>
    </div>
  );
}

// Order form component
function OrderForm({ symbol, currentPrice, onClose, onSubmit }) {
  const [action, setAction] = useState('BUY');
  const [quantity, setQuantity] = useState(1);
  const [orderType, setOrderType] = useState('MARKET');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({ symbol, action, quantity, order_type: orderType });
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div className="card-gradient rounded-xl p-6 w-full max-w-md border border-slate-700">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Place Order</h3>
          <button onClick={onClose} className="text-slate-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm text-slate-400 mb-1">Symbol</label>
            <p className="text-white font-medium">{symbol}</p>
          </div>

          <div>
            <label className="block text-sm text-slate-400 mb-1">Current Price</label>
            <p className="text-white font-medium">₹{currentPrice?.toFixed(2)}</p>
          </div>

          <div>
            <label className="block text-sm text-slate-400 mb-2">Action</label>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setAction('BUY')}
                className={`flex-1 py-2 rounded-lg font-medium transition ${action === 'BUY' ? 'bg-bull text-white' : 'bg-slate-700 text-slate-300'}`}
              >
                BUY
              </button>
              <button
                type="button"
                onClick={() => setAction('SELL')}
                className={`flex-1 py-2 rounded-lg font-medium transition ${action === 'SELL' ? 'bg-bear text-white' : 'bg-slate-700 text-slate-300'}`}
              >
                SELL
              </button>
            </div>
          </div>

          <div>
            <label className="block text-sm text-slate-400 mb-1">Quantity</label>
            <input
              type="number"
              min="1"
              value={quantity}
              onChange={(e) => setQuantity(parseInt(e.target.value) || 1)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-primary-500"
            />
          </div>

          <div>
            <label className="block text-sm text-slate-400 mb-1">Order Type</label>
            <select
              value={orderType}
              onChange={(e) => setOrderType(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-primary-500"
            >
              <option value="MARKET">Market</option>
              <option value="LIMIT">Limit</option>
            </select>
          </div>

          <div className="pt-4 flex gap-3">
            <button
              type="submit"
              className="flex-1 bg-primary-600 hover:bg-primary-700 text-white py-2 rounded-lg font-medium transition"
            >
              Submit for Approval
            </button>
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-medium transition"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// Orders panel component
function OrdersPanel({ orders, onApprove, onReject }) {
  const pendingOrders = orders?.filter(o => o.status === 'PENDING') || [];

  return (
    <div className="card-gradient rounded-xl p-6 border border-slate-700">
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <List className="w-5 h-5" />
        Pending Orders ({pendingOrders.length})
      </h3>

      {pendingOrders.length === 0 ? (
        <p className="text-slate-500 text-sm">No pending orders</p>
      ) : (
        <div className="space-y-3">
          {pendingOrders.map(order => (
            <div key={order.id} className="p-4 bg-slate-800/50 rounded-lg border border-slate-700">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium">{order.symbol}</span>
                <span className={`px-2 py-0.5 rounded text-xs font-medium ${order.action === 'BUY' ? 'bg-bull/20 text-bull' : 'bg-bear/20 text-bear'}`}>
                  {order.action}
                </span>
              </div>
              <div className="text-sm text-slate-400">
                Qty: {order.quantity} | Type: {order.order_type}
              </div>
              <div className="flex gap-2 mt-3">
                <button
                  onClick={() => onApprove(order.id)}
                  className="flex-1 bg-green-600 hover:bg-green-700 text-white py-1.5 rounded-lg text-sm font-medium transition flex items-center justify-center gap-1"
                >
                  <Check className="w-4 h-4" /> Approve
                </button>
                <button
                  onClick={() => onReject(order.id)}
                  className="flex-1 bg-red-600 hover:bg-red-700 text-white py-1.5 rounded-lg text-sm font-medium transition flex items-center justify-center gap-1"
                >
                  <XCircle className="w-4 h-4" /> Reject
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// Watchlist component
function Watchlist({ watchlist, onRemove, onSelect }) {
  return (
    <div className="card-gradient rounded-xl p-6 border border-slate-700">
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <Bell className="w-5 h-5" />
        Watchlist
      </h3>

      {watchlist.length === 0 ? (
        <p className="text-slate-500 text-sm">No stocks in watchlist</p>
      ) : (
        <div className="space-y-2">
          {watchlist.map(symbol => (
            <div key={symbol} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg hover:bg-slate-800 transition cursor-pointer" onClick={() => onSelect(symbol)}>
              <span className="font-medium">{symbol}</span>
              <button onClick={(e) => { e.stopPropagation(); onRemove(symbol); }} className="text-slate-400 hover:text-red-400">
                <X className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// Main App component
export default function App() {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [selectedStock, setSelectedStock] = useState(null);
  const [stockData, setStockData] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [indices, setIndices] = useState({});
  const [orders, setOrders] = useState([]);
  const [watchlist, setWatchlist] = useState([]);
  const [showOrderForm, setShowOrderForm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Load market indices on mount
  useEffect(() => {
    api.getMarketIndices().then(setIndices).catch(console.error);
    api.getOrders().then(setOrders).catch(console.error);
    api.getWatchlist().then(setWatchlist).catch(console.error);
  }, []);

  // Search stocks
  useEffect(() => {
    const timer = setTimeout(async () => {
      if (searchQuery.length >= 2) {
        try {
          const results = await api.searchStocks(searchQuery);
          setSearchResults(results);
        } catch (err) {
          setSearchResults([]);
        }
      } else {
        setSearchResults([]);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Load stock data when selected
  useEffect(() => {
    if (selectedStock) {
      setLoading(true);
      setError(null);

      Promise.all([
        api.getStockData(selectedStock),
        api.getStockAnalysis(selectedStock)
      ]).then(([data, analysis]) => {
        setStockData(data);
        setAnalysis(analysis);
        setLoading(false);
      }).catch(err => {
        setError(err.message);
        setLoading(false);
      });
    }
  }, [selectedStock]);

  const handleCreateOrder = async (order) => {
    try {
      const newOrder = await api.createOrder(order);
      setOrders([...orders, newOrder]);
      alert('Order created and pending approval!');
    } catch (err) {
      alert('Failed to create order: ' + err.message);
    }
  };

  const handleApproveOrder = async (orderId) => {
    try {
      await api.approveOrder(orderId);
      setOrders(orders.map(o => o.id === orderId ? { ...o, status: 'APPROVED' } : o));
      alert('Order approved!');
    } catch (err) {
      alert('Failed to approve order: ' + err.message);
    }
  };

  const handleRejectOrder = async (orderId) => {
    try {
      await api.rejectOrder(orderId);
      setOrders(orders.map(o => o.id === orderId ? { ...o, status: 'REJECTED' } : o));
      alert('Order rejected');
    } catch (err) {
      alert('Failed to reject order: ' + err.message);
    }
  };

  const handleAddToWatchlist = async () => {
    if (selectedStock && !watchlist.includes(selectedStock)) {
      try {
        await api.addToWatchlist(selectedStock);
        setWatchlist([...watchlist, selectedStock]);
      } catch (err) {
        alert('Failed to add to watchlist');
      }
    }
  };

  const handleRemoveFromWatchlist = async (symbol) => {
    try {
      await api.removeFromWatchlist(symbol);
      setWatchlist(watchlist.filter(s => s !== symbol));
    } catch (err) {
      alert('Failed to remove from watchlist');
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      {/* Header */}
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <TrendingUp className="w-8 h-8 text-primary-500" />
              <div>
                <h1 className="text-xl font-bold">Stock Trading Bot</h1>
                <p className="text-xs text-slate-400">AI-Powered Analysis for Indian Markets</p>
              </div>
            </div>

            {/* Search */}
            <div className="relative">
              <div className="flex items-center gap-2 bg-slate-800 border border-slate-700 rounded-xl px-4 py-2 w-80">
                <Search className="w-4 h-4 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search stocks (e.g., RELIANCE, TATAMOTORS)"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="bg-transparent focus:outline-none text-white w-full"
                />
              </div>

              {/* Search results dropdown */}
              {searchResults.length > 0 && (
                <div className="absolute top-full mt-2 w-full card-gradient rounded-xl border border-slate-700 overflow-hidden z-50">
                  {searchResults.map(stock => (
                    <button
                      key={stock.symbol}
                      onClick={() => {
                        setSelectedStock(stock.symbol);
                        setSearchResults([]);
                        setSearchQuery('');
                      }}
                      className="w-full px-4 py-3 text-left hover:bg-slate-800 transition border-b border-slate-800 last:border-0"
                    >
                      <div className="font-medium">{stock.name}</div>
                      <div className="text-sm text-slate-400">{stock.symbol} • {stock.sector}</div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        {/* Market Indices */}
        <MarketIndices indices={indices} />

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main panel - Chart and Analysis */}
          <div className="lg:col-span-2 space-y-6">
            {selectedStock ? (
              <>
                {loading && (
                  <div className="card-gradient rounded-xl p-6 border border-slate-700 flex items-center justify-center h-64">
                    <div className="text-center">
                      <Activity className="w-8 h-8 text-primary-500 animate-pulse mx-auto mb-2" />
                      <p className="text-slate-400">Loading analysis...</p>
                    </div>
                  </div>
                )}

                {error && (
                  <div className="card-gradient rounded-xl p-6 border border-slate-700">
                    <p className="text-red-400">Error: {error}</p>
                  </div>
                )}

                {!loading && !error && stockData && (
                  <>
                    {/* Stock header */}
                    <div className="card-gradient rounded-xl p-6 border border-slate-700">
                      <div className="flex items-center justify-between">
                        <div>
                          <h2 className="text-2xl font-bold">{stockData.name}</h2>
                          <p className="text-slate-400">{stockData.symbol}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-3xl font-bold">₹{stockData.current_price.toFixed(2)}</p>
                          <p className={`text-lg ${stockData.change >= 0 ? 'text-bull' : 'text-bear'}`}>
                            {stockData.change >= 0 ? '+' : ''}{stockData.change.toFixed(2)} ({stockData.change_percent.toFixed(2)}%)
                          </p>
                        </div>
                      </div>
                      <div className="flex gap-3 mt-4">
                        <button
                          onClick={() => setShowOrderForm(true)}
                          className="flex-1 bg-primary-600 hover:bg-primary-700 text-white py-2 rounded-lg font-medium transition"
                        >
                          Trade
                        </button>
                        <button
                          onClick={handleAddToWatchlist}
                          className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-medium transition flex items-center gap-2"
                        >
                          <Plus className="w-4 h-4" /> Watchlist
                        </button>
                      </div>
                    </div>

                    <StockChart data={stockData} symbol={selectedStock} />
                    <AnalysisPanel analysis={analysis} />
                  </>
                )}
              </>
            ) : (
              <div className="card-gradient rounded-xl p-12 border border-slate-700 text-center">
                <TrendingUp className="w-16 h-16 text-slate-600 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-slate-400">Select a stock to analyze</h3>
                <p className="text-slate-500 mt-2">Search for NSE/BSE stocks using the search bar above</p>
              </div>
            )}
          </div>

          {/* Side panel */}
          <div className="space-y-6">
            <OrdersPanel
              orders={orders}
              onApprove={handleApproveOrder}
              onReject={handleRejectOrder}
            />
            <Watchlist
              watchlist={watchlist}
              onRemove={handleRemoveFromWatchlist}
              onSelect={setSelectedStock}
            />
          </div>
        </div>
      </main>

      {/* Order form modal */}
      {showOrderForm && (
        <OrderForm
          symbol={selectedStock}
          currentPrice={stockData?.current_price}
          onClose={() => setShowOrderForm(false)}
          onSubmit={handleCreateOrder}
        />
      )}
    </div>
  );
}
