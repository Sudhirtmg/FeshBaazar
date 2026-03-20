"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { productService } from "@/services/productService";
import { Product } from "@/types";

export default function ManageProductsPage() {
  const router = useRouter();
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [togglingId, setTogglingId] = useState<number | null>(null);

  const fetchProducts = async () => {
    try {
      const data = await productService.getMyProducts();
      setProducts(data);
    } catch (err: any) {
      if (err.response?.status === 401) router.push("/login");
      if (err.response?.status === 403) router.push("/shops");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  const handleEdit = (product: Product) => {
    setEditingProduct(product);
    setShowForm(true);
  };

  const handleToggleAvailability = async (product: Product) => {
    setTogglingId(product.id);
    try {
      const formData = new FormData();
      formData.append("is_available", product.is_available ? "false" : "true");
      formData.append("name", product.name);
      formData.append("price", String(product.price));
      formData.append("stock_quantity", String(product.stock_quantity));
      formData.append("unit", product.unit);
      await productService.updateProduct(product.id, formData);
      await fetchProducts();
    } catch (err) {
      console.error("Toggle failed:", err);
    } finally {
      setTogglingId(null);
    }
  };

  const handleFormClose = () => {
    setShowForm(false);
    setEditingProduct(null);
    fetchProducts();
  };

  if (loading)
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center text-gray-400">
        Loading...
      </div>
    );

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-6">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-xl font-bold text-gray-900">My Products</h1>
          <button
            onClick={() => {
              setEditingProduct(null);
              setShowForm(true);
            }}
            className="bg-green-600 hover:bg-green-700 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
          >
            + Add product
          </button>
        </div>

        {showForm && (
          <ProductForm product={editingProduct} onClose={handleFormClose} />
        )}

        {products.length === 0 && !showForm ? (
          <div className="text-center py-16 text-gray-400">
            <p className="mb-4">No products yet.</p>
            <button
              onClick={() => setShowForm(true)}
              className="bg-green-600 hover:bg-green-700 text-white text-sm font-medium px-6 py-2.5 rounded-lg"
            >
              Add your first product
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            {products.map((product) => (
              <div
                key={product.id}
                className="bg-white rounded-xl border border-gray-200 p-4"
              >
                <div className="flex items-start gap-4">
                  {/* ✅ Fixed: small thumbnail */}
                  {product.image ? (
                    <img
                      src={product.image}
                      alt={product.name}
                      className="w-12 h-12 rounded-lg object-cover border border-gray-100 flex-shrink-0"
                    />
                  ) : (
                    <div className="w-12 h-12 rounded-lg bg-gray-100 border border-gray-200 flex items-center justify-center flex-shrink-0">
                      <span className="text-gray-400 text-xs text-center">
                        No image
                      </span>
                    </div>
                  )}

                  {/* Product info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <div className="flex items-center gap-2 flex-wrap">
                          <p className="font-medium text-gray-900">
                            {product.name}
                          </p>
                          <span
                            className={`text-xs px-2 py-0.5 rounded-full ${
                              product.is_available
                                ? "bg-green-50 text-green-700"
                                : "bg-red-50 text-red-600"
                            }`}
                          >
                            {product.is_available ? "Available" : "Unavailable"}
                          </span>
                        </div>
                        <p className="text-sm text-green-700 font-medium mt-0.5">
                          Rs.{product.effective_price}/{product.unit}
                        </p>
                        <p className="text-xs text-gray-500 mt-0.5">
                          Stock: {product.stock_quantity} {product.unit}
                        </p>
                        {product.cut_types.length > 0 && (
                          <p className="text-xs text-gray-400 mt-0.5">
                            Cuts:{" "}
                            {product.cut_types.map((c) => c.name).join(", ")}
                          </p>
                        )}
                      </div>

                      {/* Action buttons */}
                      <div className="flex items-center gap-2 flex-shrink-0">
                        <button
                          onClick={() => handleToggleAvailability(product)}
                          disabled={togglingId === product.id}
                          className="text-xs text-gray-500 hover:text-gray-700 border border-gray-200 px-3 py-1.5 rounded-lg transition-colors disabled:opacity-50"
                        >
                          {togglingId === product.id
                            ? "Saving..."
                            : product.is_available
                            ? "Mark unavailable"
                            : "Mark available"}
                        </button>
                        <button
                          onClick={() => handleEdit(product)}
                          className="text-xs text-green-600 hover:text-green-700 border border-green-200 px-3 py-1.5 rounded-lg transition-colors"
                        >
                          Edit
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

interface ProductFormProps {
  product: Product | null;
  onClose: () => void;
}

function ProductForm({ product, onClose }: ProductFormProps) {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(
    product?.image || null
  );
  const [form, setForm] = useState({
    name: product?.name || "",
    price: product?.price || "",
    discount_price: product?.discount_price || "",
    stock_quantity: product?.stock_quantity || "",
    unit: product?.unit || "kg",
    description: product?.description || "",
    is_available: product?.is_available ?? true,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0] || null;
    setFile(selected);
    if (selected) {
      setPreview(URL.createObjectURL(selected));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const formData = new FormData();
      formData.append("name", form.name);
      formData.append("price", String(form.price));
      formData.append("stock_quantity", String(form.stock_quantity));
      formData.append("unit", form.unit);
      formData.append("description", form.description);
      formData.append("is_available", String(form.is_available));

      if (form.discount_price) {
        formData.append("discount_price", String(form.discount_price));
      }

      if (file instanceof File) {
        formData.append("image", file);
      }

      if (product) {
        await productService.updateProduct(product.id, formData);
      } else {
        await productService.createProduct(formData);
      }

      onClose();
    } catch (err: any) {
      const data = err.response?.data;
      if (typeof data === "object") {
        const messages = Object.entries(data)
          .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(", ") : v}`)
          .join(" | ");
        setError(messages);
      } else {
        setError(data || "Failed to save product.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5 mb-4">
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-semibold text-gray-900">
          {product ? "Edit product" : "Add new product"}
        </h2>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600 text-sm"
        >
          Cancel
        </button>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-3">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Product name
          </label>
          <input
            type="text"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            placeholder="e.g. Fresh Whole Chicken"
            className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
            required
          />
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Price (Rs.)
            </label>
            <input
              type="number"
              value={form.price}
              onChange={(e) => setForm({ ...form, price: e.target.value })}
              placeholder="350"
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Discount price (optional)
            </label>
            <input
              type="number"
              value={form.discount_price}
              onChange={(e) =>
                setForm({ ...form, discount_price: e.target.value })
              }
              placeholder="300"
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Stock quantity
            </label>
            <input
              type="number"
              value={form.stock_quantity}
              onChange={(e) =>
                setForm({ ...form, stock_quantity: e.target.value })
              }
              placeholder="20"
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Unit
            </label>
            <select
              value={form.unit}
              onChange={(e) => setForm({ ...form, unit: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              <option value="kg">Kilogram (kg)</option>
              <option value="piece">Piece</option>
              <option value="pack">Pack</option>
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Description (optional)
          </label>
          <input
            type="text"
            value={form.description}
            onChange={(e) =>
              setForm({ ...form, description: e.target.value })
            }
            placeholder="Fresh chicken from local farm"
            className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Product image
          </label>
          {preview && (
            <img
              src={preview}
              alt="Preview"
              className="w-24 h-24 object-cover rounded-lg border border-gray-200 mb-2"
            />
          )}
          <input
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            className="w-full text-sm"
          />
          {product?.image && !file && (
            <p className="text-xs text-gray-400 mt-1">
              Leave empty to keep current image
            </p>
          )}
        </div>

        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="available"
            checked={form.is_available}
            onChange={(e) =>
              setForm({ ...form, is_available: e.target.checked })
            }
            className="text-green-600"
          />
          <label htmlFor="available" className="text-sm text-gray-700">
            Available for ordering
          </label>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-green-600 hover:bg-green-700 text-white font-medium py-2.5 rounded-lg text-sm transition-colors disabled:opacity-50"
        >
          {loading ? "Saving..." : product ? "Update product" : "Add product"}
        </button>
      </form>
    </div>
  );
}