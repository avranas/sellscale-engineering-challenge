import React, { useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client';

interface Stock {
  currentPrice: number;
  longName: string;
  symbol: string;
  quantity: number;
}

const App: React.FC = () => {
  const [response, setResponse] = useState<Stock | null>(null);
  const [userStocks, setUserStocks] = useState<Stock[]>([]);
  const [search, setSearch] = useState('');
  const [quantity, setQuantity] = useState('0');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [money, setMoney] = useState<number | null>(null); // To store user's money

  const fetchUserStocksAndMoney = async () => {
    try {
      // Fetch user stocks
      const stockRes = await fetch('/stocks');
      if (!stockRes.ok) {
        throw new Error('Failed to fetch user stocks');
      }
      const stocks = await stockRes.json();
      setUserStocks(stocks);

      // Fetch user money
      const moneyRes = await fetch('/money');
      if (!moneyRes.ok) {
        throw new Error('Failed to fetch user money');
      }
      const moneyData = await moneyRes.json();
      setMoney(moneyData.money); // Set the user's money
    } catch (err) {
      console.error(err);
      setError('Failed to fetch user data');
    }
  };

  // Fetch all of user 1's stocks and money when the component mounts
  useEffect(() => {
    fetchUserStocksAndMoney();
  }, []);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearch(e.target.value);
  };

  const handleQuantityChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.replace(/[^0-9]/g, '').replace(/^0+(?!$)/, '');
    setQuantity(value);
  };

  const getServerData = async () => {
    if (!search.trim()) {
      setError('Please enter a stock symbol.');
      return;
    }
    setError(null);
    setLoading(true);

    try {
      const res = await fetch(`/stock/${search}`);
      if (!res.ok) {
        throw new Error('Stock not found');
      }
      const json = await res.json();
      setResponse(json);
    } catch (err) {
      console.error(err);
      setError('Failed to fetch stock data');
      setResponse(null);
    } finally {
      setLoading(false);
    }
  };

  const buyStock = async () => {
    if (!response) return;
    const body = JSON.stringify({
      symbol: response.symbol,
      quantity: Number(quantity),
    });

    try {
      const res = await fetch('buy', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: body,
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error('Failed to complete purchase: ' + text);
      }

      const json = await res.json();
      console.log('Purchase result:', json);
      fetchUserStocksAndMoney();
    } catch (err) {
      if (err instanceof Error) {
        console.error(err);
        setError(err.message);
      } else {
        console.error('An unexpected error occurred', err);
        setError('An unexpected error occurred');
      }
    }
  };

  const sellStock = async () => {
    if (!response) return;
    const body = JSON.stringify({
      symbol: response.symbol,
      quantity: Number(quantity),
    });

    try {
      const res = await fetch('sell', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: body,
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error('Failed to complete sale: ' + text);
      }

      const json = await res.json();
      console.log('Sale result:', json);
      fetchUserStocksAndMoney(); // Refresh stocks and money
    } catch (err) {
      if (err instanceof Error) {
        console.error(err);
        setError(err.message);
      } else {
        console.error('An unexpected error occurred', err);
        setError('An unexpected error occurred');
      }
    }
  };

  // Check if the user owns the stock
  const userOwnsStock = (symbol: string) => {
    return userStocks.some((stock) => stock.symbol === symbol && stock.quantity > 0);
  };

  return (
    <div>
      <h1>SellScaleHood</h1>

      {/* Display User's Money */}
      <h2>User's Money: {money !== null ? `$${money}` : 'Loading...'}</h2>

      {/* Stock Search and Buy Section */}
      <input
        type="text"
        id="search"
        name="search"
        className="search"
        value={search}
        onChange={handleSearchChange}
        placeholder="Enter stock symbol"
      />
      <button onClick={getServerData} disabled={loading}>
        {loading ? 'Searching...' : 'Search'}
      </button>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {response && (
        <div>
          <p>Company: {response.longName}</p>
          <p>Price: {response.currentPrice}</p>
          <div className="buy-container">
            <label htmlFor="quantity">Quantity</label>
            <input
              id="quantity"
              name="quantity"
              className="quantity"
              value={quantity}
              onChange={handleQuantityChange}
              type="number"
              min="0"
            />
            <button onClick={buyStock} disabled={Number(quantity) <= 0}>
              BUY
            </button>

            {/* Conditionally render the Sell button if the user owns the stock */}
            {userOwnsStock(response.symbol) && (
              <button onClick={sellStock} disabled={Number(quantity) <= 0}>
                SELL
              </button>
            )}
          </div>
          <p>
            <strong>
              Total cost: {response.currentPrice * Number(quantity)}
            </strong>
          </p>
        </div>
      )}

      {/* User's Stocks Table */}
      <h2>Your Stocks</h2>
      {userStocks.length > 0 ? (
        <table>
          <thead>
            <tr>
              <th>Symbol</th>
              <th>Quantity</th>
            </tr>
          </thead>
          <tbody>
            {userStocks.map((stock) => (
              <tr key={stock.symbol}>
                <td>{stock.symbol}</td>
                <td>{stock.quantity}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p>No stocks available</p>
      )}
    </div>
  );
};

const container = document.querySelector('#root');
if (container) {
  const root = createRoot(container);
  root.render(<App />);
} else {
  console.error('Failed to find the root element');
}
