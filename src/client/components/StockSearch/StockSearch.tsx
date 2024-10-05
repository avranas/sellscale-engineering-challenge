import React, { useState } from 'react';
import { fetchStockData, Stock } from '../../services/StockService';
import StockDetails from '../StockDetails/StockDetails';
import './StockSearch.css';

interface StockSearchProps {
  setError: (error: string | null) => void;
  userStocks: Stock[];
  setUserStocks: (stocks: Stock[]) => void;
  setMoney: (money: number) => void;
}

// Stock search bar
const StockSearch: React.FC<StockSearchProps> = ({
  setError,
  userStocks,
  setUserStocks,
  setMoney,
}) => {
  const [search, setSearch] = useState('');
  const [response, setResponse] = useState<Stock | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearch(e.target.value);
  };

  const getServerData = async () => {
    if (!search.trim()) {
      setError('Please enter a stock symbol.');
      return;
    }
    setError(null);
    setLoading(true);

    try {
      const stockData = await fetchStockData(search);
      setResponse(stockData);
    } catch (error) {
      console.error(error);
      setError('Failed to fetch stock data');
      setResponse(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
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
      {response && (
        <StockDetails
          stock={response}
          userStocks={userStocks}
          setUserStocks={setUserStocks}
          setMoney={setMoney}
        />
      )}
    </div>
  );
};

export default StockSearch;
