import React from 'react';
import { Stock } from '../../services/StockService';
import './UserStocks.css';

interface UserStocksProps {
  stocks: Stock[];
}

// Display the stocks that the user owns in a table
const UserStocks: React.FC<UserStocksProps> = ({ stocks }) => {
  return (
    <div>
      <h2>Your Stocks</h2>
      {stocks.length > 0 ? (
        <table>
          <thead>
            <tr>
              <th>Symbol</th>
              <th>Quantity</th>
            </tr>
          </thead>
          <tbody>
            {stocks.map((stock) => (
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

export default UserStocks;
