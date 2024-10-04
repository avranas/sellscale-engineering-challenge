import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';

const App: React.FC = () => {
  const [response, setResponse] = useState('');
  useEffect(() => {
    const getServerData = async () => {
      try {
        const data = await fetch('/hello');
        const text = await data.text();
        console.log('text', text);
        setResponse(text);
      } catch (err) {
        console.log(err);
      }
    };
    getServerData();
  }, []);

  return (
    <div>
      <h1>Hello, World!</h1>
      <p>{response}</p>
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
