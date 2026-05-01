const API_BASE = 'http://localhost:8000/api';

export async function searchStocks(query) {
  const res = await fetch(`${API_BASE}/stocks/search?q=${encodeURIComponent(query)}`);
  if (!res.ok) throw new Error('Search failed');
  return res.json();
}

export async function getStockData(symbol) {
  const res = await fetch(`${API_BASE}/stocks/${encodeURIComponent(symbol)}/data`);
  if (!res.ok) throw new Error('Failed to fetch stock data');
  return res.json();
}

export async function getStockAnalysis(symbol) {
  const res = await fetch(`${API_BASE}/stocks/${encodeURIComponent(symbol)}/analysis`);
  if (!res.ok) throw new Error('Failed to fetch analysis');
  return res.json();
}

export async function getMarketIndices() {
  const res = await fetch(`${API_BASE}/market/indices`);
  if (!res.ok) throw new Error('Failed to fetch indices');
  return res.json();
}

export async function createOrder(order) {
  const res = await fetch(`${API_BASE}/orders`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(order),
  });
  if (!res.ok) throw new Error('Failed to create order');
  return res.json();
}

export async function getOrders(status) {
  const url = status ? `${API_BASE}/orders?status=${status}` : `${API_BASE}/orders`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch orders');
  return res.json();
}

export async function approveOrder(orderId) {
  const res = await fetch(`${API_BASE}/orders/${orderId}/approve`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to approve order');
  return res.json();
}

export async function rejectOrder(orderId) {
  const res = await fetch(`${API_BASE}/orders/${orderId}/reject`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to reject order');
  return res.json();
}

export async function getWatchlist() {
  const res = await fetch(`${API_BASE}/watchlist`);
  if (!res.ok) throw new Error('Failed to fetch watchlist');
  return res.json();
}

export async function addToWatchlist(symbol) {
  const res = await fetch(`${API_BASE}/watchlist/${encodeURIComponent(symbol)}`, { method: 'POST' });
  if (!res.ok) throw new Error('Failed to add to watchlist');
  return res.json();
}

export async function removeFromWatchlist(symbol) {
  const res = await fetch(`${API_BASE}/watchlist/${encodeURIComponent(symbol)}`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Failed to remove from watchlist');
  return res.json();
}
