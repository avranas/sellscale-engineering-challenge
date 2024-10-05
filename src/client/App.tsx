import React, { useState, useEffect } from 'react';
import StockSearch from './components/StockSearch/StockSearch';
import UserStocks from './components/UserStocks/UserStocks';
import {
  fetchUserStocks,
  fetchUserMoney,
  Stock,
} from './services/StockService';

const App: React.FC = () => {
  const [userStocks, setUserStocks] = useState<Stock[]>([]);
  const [money, setMoney] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const initialize = async () => {
      try {
        const stocks = await fetchUserStocks();
        setUserStocks(stocks);
        const moneyData = await fetchUserMoney();
        setMoney(moneyData.money);
      } catch (error) {
        console.error(error);
        setError('Failed to fetch user data');
      }
    };
    initialize();
  }, []);

  return (
    <div>
      <h1>SellScaleHood</h1>
      <StockSearch
        setError={setError}
        userStocks={userStocks}
        setUserStocks={setUserStocks}
        setMoney={setMoney}
      />
      <h2>User's Money: {money !== null ? `$${money}` : 'Loading...'}</h2>
      <UserStocks stocks={userStocks} />
      {error && error}
    </div>
  );
};

export default App;
