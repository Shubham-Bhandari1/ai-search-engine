import React, { useState } from 'react';
import './App.css';

// ── ProductCard Component ──────────────────────────
// A reusable card that displays one product
// Props: name, description, category, price, rating, score
function ProductCard({ name, description, category, price, rating, score }) {
  return (
    <div className="product-card">
      <div className="product-category">{category}</div>
      <h3 className="product-name">{name}</h3>
      <p className="product-description">{description}</p>
      <div className="product-footer">
        <span className="product-price">₹{Number(price).toLocaleString()}</span>
        <span className="product-rating">⭐ {rating}</span>
      </div>
      {score && (
        <div className="product-score">
          AI Match: {(score * 100).toFixed(0)}%
        </div>
      )}
    </div>
  );
}

// ── Main App Component ─────────────────────────────
function App() {
  // State — these are variables that when changed, 
  // automatically update the UI
  const [query, setQuery]       = useState('');       // what user typed
  const [results, setResults]   = useState([]);       // search results
  const [loading, setLoading]   = useState(false);    // show loading spinner
  const [searchType, setSearchType] = useState('keyword'); // keyword or ai
  const [searched, setSearched] = useState(false);    // has user searched yet

  // This function runs when user clicks Search
  async function handleSearch() {
    if (!query.trim()) return; // do nothing if search box is empty

    setLoading(true);   // show loading
    setSearched(true);  // mark that search happened

    // Choose which API endpoint to call
    const endpoint = searchType === 'ai'
      ? `http://localhost:8000/ai-search?q=${query}`
      : `http://localhost:8000/search?q=${query}`;

    try {
      // Call your FastAPI backend
      const response = await fetch(endpoint);
      const data = await response.json();
      setResults(data.results); // save results to state
    } catch (error) {
      console.error("Search failed:", error);
      setResults([]);
    }

    setLoading(false); // hide loading
  }

  // Run search when user presses Enter
  function handleKeyPress(e) {
    if (e.key === 'Enter') handleSearch();
  }

  return (
    <div className="app">

      {/* ── Header ── */}
      <div className="header">
        <h1>🔍 AI Search Engine</h1>
        <p>Powered by Elasticsearch + AI Semantic Search</p>
      </div>

      {/* ── Search Bar ── */}
      <div className="search-container">
        <input
          type="text"
          className="search-input"
          placeholder="Search for products..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={handleKeyPress}
        />
        <button className="search-btn" onClick={handleSearch}>
          Search
        </button>
      </div>

      {/* ── Search Type Toggle ── */}
      <div className="toggle-container">
        <button
          className={`toggle-btn ${searchType === 'keyword' ? 'active' : ''}`}
          onClick={() => setSearchType('keyword')}
        >
          🔤 Keyword Search
        </button>
        <button
          className={`toggle-btn ${searchType === 'ai' ? 'active' : ''}`}
          onClick={() => setSearchType('ai')}
        >
          🤖 AI Search
        </button>
      </div>

      {/* ── Results ── */}
      <div className="results-container">

        {/* Loading spinner */}
        {loading && <div className="loading">Searching...</div>}

        {/* No results message */}
        {!loading && searched && results.length === 0 && (
          <div className="no-results">No products found for "{query}"</div>
        )}

        {/* Results count */}
        {!loading && results.length > 0 && (
          <p className="results-count">
            Found {results.length} results for "{query}"
            {searchType === 'ai' && ' (AI Semantic Search)'}
          </p>
        )}

        {/* Product cards grid */}
        <div className="products-grid">
          {results.map((product) => (
            <ProductCard
              key={product.id}
              name={product.name}
              description={product.description}
              category={product.category}
              price={product.price}
              rating={product.rating}
              score={product.score}
            />
          ))}
        </div>
      </div>

    </div>
  );
}

export default App;