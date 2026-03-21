"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Cookies from "js-cookie";
import useAuthStore from "@/store/authStore";
import { authService } from "@/services/authService";

export default function RegisterPage() {
  const router = useRouter();
  const setUser = useAuthStore((state) => state.setUser);

  const [form, setForm] = useState({
    phone: "",
    email: "",
    password: "",
    role: "customer",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const res = await authService.register(form);
      Cookies.set("access_token", res.tokens.access, { expires: 1 });
      Cookies.set("refresh_token", res.tokens.refresh, { expires: 30 });
      setUser(res.user);
      //-------------------------change start-------------------------
      if (res.user.role === "shop_owner") {
        router.push("/dashboard/settings"); // ✅ go to settings to fill shop info
        //-------------------------change end-------------------------
      } else {
        router.push("/shops");
      }
    } catch (err: any) {
      const data = err.response?.data;
      if (data?.phone) setError(data.phone[0]);
      else if (data?.email) setError(data.email[0]);
      else if (data?.password) setError(data.password[0]);
      else setError("Registration failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 w-full max-w-md p-8">
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-8 h-8 bg-green-600 rounded-lg flex items-center justify-center">
              <span className="text-white text-sm font-bold">F</span>
            </div>
            <h1 className="text-xl font-bold text-gray-900">FreshBazaar</h1>
          </div>
          <p className="text-gray-500 text-sm">Create your account</p>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Phone number
            </label>
            <input
              type="text"
              value={form.phone}
              onChange={(e) => setForm({ ...form, phone: e.target.value })}
              placeholder="+9779800000001"
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email{" "}
              <span className="text-gray-400 font-normal">(optional)</span>
            </label>
            <input
              type="email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              placeholder="you@example.com"
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <input
              type="password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              placeholder="At least 6 characters"
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
              required
              minLength={6}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              I am a
            </label>
            <div className="flex gap-3">
              <button
                type="button"
                onClick={() => setForm({ ...form, role: "customer" })}
                className={`flex-1 py-2.5 rounded-lg border-2 text-sm font-medium transition-colors ${
                  form.role === "customer"
                    ? "border-green-600 bg-green-50 text-green-700"
                    : "border-gray-200 text-gray-600"
                }`}
              >
                Customer
              </button>
              <button
                type="button"
                onClick={() => setForm({ ...form, role: "shop_owner" })}
                className={`flex-1 py-2.5 rounded-lg border-2 text-sm font-medium transition-colors ${
                  form.role === "shop_owner"
                    ? "border-green-600 bg-green-50 text-green-700"
                    : "border-gray-200 text-gray-600"
                }`}
              >
                Shop owner
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-green-600 hover:bg-green-700 text-white font-medium py-2.5 rounded-lg text-sm transition-colors disabled:opacity-50"
          >
            {loading ? "Creating account..." : "Create account"}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-gray-500">
          Already have an account?{" "}
          <a
            href="/login"
            className="text-green-600 font-medium hover:underline"
          >
            Sign in
          </a>
        </p>
      </div>
    </div>
  );
}
