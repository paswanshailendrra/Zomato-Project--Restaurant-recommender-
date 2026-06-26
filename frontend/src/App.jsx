import { useState } from "react";
import SearchForm from "./components/SearchForm";
import ResultsGrid from "./components/ResultsGrid";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

function App() {
  const [response, setResponse] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSearch = async (preferences) => {
    setIsLoading(true);
    setError(null);
    setResponse(null);

    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/recommend`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(preferences),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        let errMsg = `API error: ${res.status} ${res.statusText}`;
        if (errData.detail) {
          errMsg = typeof errData.detail === 'string'
            ? errData.detail
            : Array.isArray(errData.detail)
              ? errData.detail.map(e => e.msg || JSON.stringify(e)).join('; ')
              : JSON.stringify(errData.detail);
        }
        throw new Error(errMsg);
      }

      const data = await res.json();
      setResponse(data);
    } catch (err) {
      console.error(err);
      setError(err.message || "Failed to fetch recommendations. Ensure the backend server is running and API keys are set.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <div className="ambient-light bg-light-1"></div>
      <div className="ambient-light bg-light-2"></div>

      <header className="bg-surface/40 backdrop-blur-xl docked full-width top-0 sticky border-b border-white/10 shadow-[0px_0px_15px_rgba(71,214,255,0.2)] z-50">
        <div className="flex justify-between items-center px-margin-mobile md:px-margin-desktop py-4 w-full max-w-container-max mx-auto">
          <div className="font-headline-md text-headline-md font-bold tracking-tighter text-primary">Epicurean AI</div>

        </div>
      </header>

      <main className="flex-grow w-full px-margin-mobile md:px-margin-desktop py-12 relative z-10 flex flex-col gap-12">
        <SearchForm onSearch={handleSearch} isLoading={isLoading} />
        
        {error && (
          <div className="max-w-4xl mx-auto w-full bg-error-container text-on-error-container p-6 rounded-xl font-code-sm">
            {error}
          </div>
        )}

        <ResultsGrid response={response} />
      </main>

      <footer className="bg-surface-container-lowest/60 backdrop-blur-md w-full rounded-t-xl border-t border-white/5 mt-24">
        <div className="flex flex-col md:flex-row justify-between items-center px-margin-mobile md:px-margin-desktop py-gutter w-full max-w-container-max mx-auto gap-4">
          <div className="font-headline-sm text-headline-sm text-on-surface">Epicurean AI</div>
          <div className="font-label-caps text-label-caps text-on-surface-variant text-center">© 2026 Epicurean AI. Powered by Groq</div>
          <div className="flex gap-6">
            <a className="font-label-caps text-label-caps text-on-surface-variant hover:text-secondary-fixed transition-colors" href="#">Privacy Policy</a>
            <a className="font-label-caps text-label-caps text-on-surface-variant hover:text-secondary-fixed transition-colors" href="#">Terms of Service</a>
          </div>
        </div>
      </footer>
    </>
  );
}

export default App;
