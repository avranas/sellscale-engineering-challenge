export interface Stock {
  currentPrice: number;
  longName: string;
  symbol: string;
  quantity: number;
}

export interface MoneyData {
  money: number;
}

export async function fetchUserStocks(): Promise<Stock[]> {
  const response = await fetch('/stocks');
  if (!response.ok) throw new Error('Failed to fetch user stocks');
  return await response.json();
}

export async function fetchUserMoney(): Promise<MoneyData> {
  const response = await fetch('/money');
  if (!response.ok) throw new Error('Failed to fetch user money');
  return await response.json();
}

export async function fetchStockData(symbol: string): Promise<Stock> {
  const response = await fetch(`/stock/${symbol}`);
  if (!response.ok) throw new Error('Stock not found');
  return await response.json();
}

export async function buyStock(
  symbol: string,
  quantity: number,
): Promise<Stock> {
  const response = await fetch('buy', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ symbol, quantity }),
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error('Failed to complete purchase: ' + text);
  }
  return await response.json();
}

export async function sellStock(
  symbol: string,
  quantity: number,
): Promise<Stock> {
  const response = await fetch('sell', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ symbol, quantity }),
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error('Failed to complete sale: ' + text);
  }
  return await response.json();
}
