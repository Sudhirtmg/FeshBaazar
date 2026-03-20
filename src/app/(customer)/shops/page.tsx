"use client";
import { useEffect, useState } from "react";
import { shopService } from "@/services/shopService";
import { Shop } from "@/types";

export default function ShopsPage() {
  const [shops, setShops] = useState<Shop[]>([]);
  const [loading, setLoading] = useState(true);
  const [city, setCity] = useState("");

  const fetchShops = async () => {
    setLoading(true);
    try {
      const data = await shopService.getShops(city || undefined);
      setShops(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchShops();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
     

      <div className="max-w-4xl mx-auto px-4 py-6">
        <div className="flex gap-2 mb-6">
          <input
            type="text"
            value={city}
            onChange={(e) => setCity(e.target.value)}
            placeholder="Filter by city..."
            className="flex-1 border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
          />
          <button
            onClick={fetchShops}
            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2.5 rounded-lg text-sm font-medium transition-colors"
          >
            Search
          </button>
        </div>

        {loading ? (
          <div className="text-center py-12 text-gray-400">
            Loading shops...
          </div>
        ) : shops.length === 0 ? (
          <div className="text-center py-12 text-gray-400">No shops found.</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {shops.map((shop) => (
              <a
                key={shop.id}
                href={`/shops/${shop.slug}`}
                className="bg-white rounded-xl border border-gray-200 p-5 hover:shadow-md transition-shadow block"
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h2 className="font-semibold text-gray-900">{shop.name}</h2>
                    <p className="text-sm text-gray-500 mt-0.5">{shop.city}</p>
                  </div>
                  <span
                    className={`text-xs font-medium px-2 py-1 rounded-full ${shop.is_open ? "bg-green-50 text-green-700" : "bg-red-50 text-red-600"}`}
                  >
                    {shop.is_open ? "Open" : "Closed"}
                  </span>
                </div>
                {shop.description && (
                  <p className="text-sm text-gray-500 mb-3 line-clamp-2">
                    {shop.description}
                  </p>
                )}
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-400">{shop.address}</span>
                  <span className="text-xs text-green-600 font-medium">
                    View products →
                  </span>
                </div>
              </a>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
