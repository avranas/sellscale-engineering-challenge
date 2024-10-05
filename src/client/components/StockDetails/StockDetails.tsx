import React, { useState } from 'react';
import {
  Stock,
  buyStock,
  sellStock,
  fetchUserStocks,
  fetchUserMoney,
} from '../../services/StockService';
import './StockDetails.css';

interface StockDetailsProps {
  stock: Stock | null;
  userStocks: Stock[];
  setUserStocks: (stocks: Stock[]) => void;
  setMoney: (money: number) => void;
}

// Displays information about the stock, with options to buy or sell
const StockDetails: React.FC<StockDetailsProps> = ({
  stock,
  userStocks,
  setUserStocks,
  setMoney,
}) => {
  const [quantity, setQuantity] = useState<number>(0);

  const handleQuantityChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuantity(parseInt(e.target.value));
  };

  const userOwnsStock = (symbol: string): boolean => {
    return userStocks.some((s) => s.symbol === symbol && s.quantity > 0);
  };

  const handleBuy = async () => {
    if (!stock) return;
    try {
      const result = await buyStock(stock.symbol, quantity);
      console.log('Purchase result:', result);
      // Re-fetch stocks and money to reflect new state
      const updatedStocks = await fetchUserStocks();
      setUserStocks(updatedStocks);
      const moneyData = await fetchUserMoney();
      setMoney(moneyData.money);
    } catch (error) {
      console.error(error);
    }
  };

  const handleSell = async () => {
    if (!stock) return;
    try {
      const result = await sellStock(stock.symbol, quantity);
      console.log('Sale result:', result);
      // Re-fetch stocks and money to reflect new state
      const updatedStocks = await fetchUserStocks();
      setUserStocks(updatedStocks);
      const moneyData = await fetchUserMoney();
      setMoney(moneyData.money);
    } catch (error) {
      console.error(error);
    }
  };

  return (
    stock && (
      <div>
        <p>Company: {stock.longName}</p>
        <p>Price: {stock.currentPrice}</p>
        <div className="buy-container">
          <label htmlFor="quantity">Quantity</label>
          <input
            id="quantity"
            name="quantity"
            type="number"
            min="0"
            value={quantity}
            onChange={handleQuantityChange}
          />
          <button onClick={handleBuy} disabled={quantity <= 0}>
            BUY
          </button>
          {userOwnsStock(stock.symbol) && (
            <button onClick={handleSell} disabled={quantity <= 0}>
              SELL
            </button>
          )}
          <p>
            <strong>Total cost: ${stock.currentPrice * quantity}</strong>
          </p>
        </div>
      </div>
    )
  );
};

export default StockDetails;
