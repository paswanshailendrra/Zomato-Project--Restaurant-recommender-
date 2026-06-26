import { Star, Terminal } from "lucide-react";

export default function RestaurantCard({ recommendation, index }) {
  return (
    <div className={`glass-card rounded-xl p-1 ${index === 0 ? "md:col-span-12 neon-border" : "md:col-span-6"}`}>
      <div className="bg-surface-container/50 rounded-lg p-6 md:p-8 flex flex-col h-full justify-between">
        <div className="flex flex-col gap-4">
          <div className="flex justify-between items-start">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <div className={`px-3 py-1 rounded-full font-label-caps text-label-caps border ${index === 0 ? "border-primary/50 text-primary glow-text" : "border-secondary/30 text-secondary"}`}>
                  RANK #{recommendation.rank}
                </div>
              </div>
              <h2 className={`${index === 0 ? "font-display-lg-mobile md:font-display-lg text-display-lg-mobile md:text-display-lg" : "font-headline-md text-headline-md"} text-on-surface`}>
                {recommendation.name}
              </h2>
              <div className="flex gap-2 mt-3 flex-wrap">
                {recommendation.cuisines.map((c, i) => (
                  <span key={i} className="px-3 py-1 bg-secondary/15 text-secondary rounded-full font-code-sm text-code-sm">
                    {c}
                  </span>
                ))}
                <span className="px-3 py-1 bg-surface-variant text-on-surface-variant rounded-full font-code-sm text-code-sm">
                  {recommendation.estimated_cost ? `~₹${recommendation.estimated_cost}` : "Cost N/A"}
                </span>
              </div>
            </div>
            
            <div className="flex items-center gap-1 bg-surface-container-high rounded-full px-4 py-2 border border-outline-variant">
              <Star className={`w-5 h-5 ${index === 0 ? "text-primary fill-primary" : "text-secondary fill-secondary"}`} />
              <span className={`font-headline-sm text-headline-sm ${index === 0 ? "text-primary" : "text-secondary"}`}>
                {recommendation.rating.toFixed(1)}
              </span>
            </div>
          </div>

          <div className="bg-surface-container-highest/50 rounded-lg p-4 border border-outline-variant/30 mt-4">
            <div className="flex items-center gap-2 mb-2">
              <Terminal className="w-4 h-4 text-primary" />
              <span className="font-label-caps text-label-caps text-on-surface-variant">AI Explanation Matrix</span>
            </div>
            <p className="terminal-text text-code-sm leading-relaxed whitespace-pre-wrap">
              {recommendation.explanation}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
