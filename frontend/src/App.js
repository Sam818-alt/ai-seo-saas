import React, { useState, useEffect } from 'react';
import GenerateBlog from './components/GenerateBlog';
import BlogList from './components/BlogList';
import Pricing from './components/Pricing';

export default function App() {
  const [blogs, setBlogs] = useState([]);
  const [selected, setSelected] = useState(null);
  const [apiStatus, setApiStatus] = useState('Checking...');

  // ✅ Ping the backend API when the app loads
  useEffect(() => {
    fetch('http://localhost:5000/api/ping')
      .then(res => res.json())
      .then(data => {
        setApiStatus(`✅ Backend: ${data.status}`);
      })
      .catch(err => {
        console.error('Backend API error:', err);
        setApiStatus('❌ Backend not connected');
      });
  }, []);

  return (
    <div>
      <h2>AI SEO Blog Generator (v6) — Payments Integrated</h2>

      {/* ✅ Show backend connection status */}
      <p style={{ fontSize: '14px', color: apiStatus.startsWith('✅') ? 'green' : 'red' }}>
        {apiStatus}
      </p>

      <GenerateBlog
        onCreate={(b) => {
          setBlogs([b, ...blogs]);
          setSelected(b);
        }}
      />
      <Pricing userId={'demo-user'} />
      <div style={{ display: 'flex', gap: 20, marginTop: 20 }}>
        <div style={{ flex: 1 }}>
          <BlogList blogs={blogs} onSelect={(b) => setSelected(b)} />
        </div>
        <div style={{ flex: 2 }}>
          {selected ? (
            <div>
              <h3>Selected Blog</h3>
              <pre style={{ whiteSpace: 'pre-wrap' }}>
                {JSON.stringify(selected, null, 2)}
              </pre>
            </div>
          ) : (
            <div>Select a blog</div>
          )}
        </div>
      </div>
    </div>
  );
}



