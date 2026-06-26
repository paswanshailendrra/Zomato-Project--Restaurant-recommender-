import { useState, useEffect } from "react";
import { Search, Loader2 } from "lucide-react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export default function SearchForm({ onSearch, isLoading }) {
  const [locations, setLocations] = useState([]);
  const [cuisines, setCuisines] = useState([]);
  const [location, setLocation] = useState("");
  const [cuisine, setCuisine] = useState("");
  const [budget, setBudget] = useState("medium");
  const [minRating, setMinRating] = useState(4.0);

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/v1/locations`)
      .then((res) => res.json())
      .then((data) => setLocations(data.locations || []))
      .catch((err) => console.error("Failed to load locations", err));

    fetch(`${API_BASE_URL}/api/v1/cuisines`)
      .then((res) => res.json())
      .then((data) => setCuisines(data.cuisines || []))
      .catch((err) => console.error("Failed to load cuisines", err));
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!location) return;
    onSearch({ location, budget, min_rating: minRating, ...(cuisine && { cuisine }) });
  };

  return (
    <form onSubmit={handleSubmit} className="glass-panel rounded-xl p-8 relative overflow-hidden mt-8 max-w-4xl mx-auto neon-border">
      <div className="absolute top-0 right-0 p-4 opacity-20">
        <Search className="w-16 h-16 text-primary" />
      </div>
      <h2 className="font-headline-md text-headline-md text-primary mb-6 flex items-center gap-2">
        <span>Curate Your Experience</span>
      </h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 relative z-10">
        <div className="flex flex-col gap-2">
          <label className="font-label-caps text-label-caps text-on-surface-variant">LOCATION</label>
          <select 
            value={location} 
            onChange={(e) => setLocation(e.target.value)}
            required
            className="w-full bg-surface-container-highest border border-outline-variant rounded-lg p-3 text-on-surface focus:outline-none focus:border-primary transition-colors appearance-none"
          >
            <option value="" disabled>Select a location...</option>
            {locations.map((loc) => (
              <option key={loc} value={loc}>{loc}</option>
            ))}
          </select>
        </div>

        <div className="flex flex-col gap-2">
          <label className="font-label-caps text-label-caps text-on-surface-variant">CUISINE (OPTIONAL)</label>
          <select 
            value={cuisine} 
            onChange={(e) => setCuisine(e.target.value)}
            className="w-full bg-surface-container-highest border border-outline-variant rounded-lg p-3 text-on-surface focus:outline-none focus:border-primary transition-colors appearance-none"
          >
            <option value="">Any Cuisine</option>
            {cuisines.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>

        <div className="flex flex-col gap-2">
          <label className="font-label-caps text-label-caps text-on-surface-variant">BUDGET</label>
          <select 
            value={budget} 
            onChange={(e) => setBudget(e.target.value)}
            className="w-full bg-surface-container-highest border border-outline-variant rounded-lg p-3 text-on-surface focus:outline-none focus:border-primary transition-colors appearance-none"
          >
            <option value="low">Low (₹0 - ₹500)</option>
            <option value="medium">Medium (₹500 - ₹1000)</option>
            <option value="high">High (₹1000 - ₹2000)</option>
            <option value="very high">Premium (₹2000+)</option>
          </select>
        </div>

        <div className="flex flex-col gap-2">
          <label className="font-label-caps text-label-caps text-on-surface-variant">MIN RATING: {minRating.toFixed(1)}</label>
          <input 
            type="range" 
            min="3.0" 
            max="5.0" 
            step="0.1" 
            value={minRating}
            onChange={(e) => setMinRating(parseFloat(e.target.value))}
            className="w-full mt-2 accent-primary"
          />
        </div>
      </div>

      <div className="mt-8 flex justify-end">
        <button 
          type="submit" 
          disabled={isLoading || !location}
          className="px-8 py-3 flex items-center gap-2 rounded-full bg-gradient-to-r from-primary-container to-secondary-container text-white font-label-caps text-label-caps hover:shadow-[0_0_20px_rgba(0,210,255,0.4)] disabled:opacity-50 disabled:cursor-not-allowed transition-all"
        >
          {isLoading ? (
            <><Loader2 className="w-5 h-5 animate-spin" /> SYNTHESIZING...</>
          ) : (
            <>INITIATE SEARCH</>
          )}
        </button>
      </div>
    </form>
  );
}
