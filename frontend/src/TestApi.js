import React, { useEffect, useState } from 'react';

function TestApi() {
  const [message, setMessage] = useState('Loading...');

  useEffect(() => {
    fetch('http://localhost:5000/api/ping')
      .then((response) => response.json())
      .then((data) => {
        setMessage(data.status);
      })
      .catch((error) => {
        setMessage('Error connecting to backend');
        console.error('API error:', error);
      });
  }, []);

  return <div>Backend Status: {message}</div>;
}

export default TestApi;
