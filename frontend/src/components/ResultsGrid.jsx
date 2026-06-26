import RestaurantCard from "./RestaurantCard";

export default function ResultsGrid({ response }) {
  if (!response) return null;

  return (
    <div className="flex flex-col gap-12 mt-12 w-full max-w-container-max mx-auto relative z-10">
      {response.summary && (
        <p className="font-body-lg text-body-lg text-on-surface-variant max-w-3xl mb-8">
          {response.summary}
        </p>
      )}

      {response.recommendations && response.recommendations.length > 0 && (
        <section className="grid grid-cols-1 md:grid-cols-12 gap-8">
          {response.recommendations.map((rec, index) => (
            <RestaurantCard key={rec.id} recommendation={rec} index={index} />
          ))}
        </section>
      )}
    </div>
  );
}
