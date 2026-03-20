// src/app/(shop-owner)/dashboard/settings/page.tsx:
"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { shopService } from "@/services/shopService";
import { Shop, ShopSchedule } from "@/types";

const DAYS = [
  "Monday",
  "Tuesday",
  "Wednesday",
  "Thursday",
  "Friday",
  "Saturday",
  "Sunday",
];

const DEFAULT_SCHEDULE: Omit<ShopSchedule, "id" | "weekday_name">[] = DAYS.map(
  (_, i) => ({
    weekday: i,
    is_active: true,
    morning_open: "06:00",
    morning_close: "11:00",
    afternoon_open: i < 6 ? "14:00" : null,
    afternoon_close: i < 6 ? "18:00" : null,
  }),
);

export default function ShopSettingsPage() {
  const router = useRouter();
  const [expandedDay, setExpandedDay] = useState<number | null>(null)
  const [shop, setShop] = useState<Shop | null>(null);
  const [loading, setLoading] = useState(true);
  const [savingInfo, setSavingInfo] = useState(false);
  const [savingSched, setSavingSched] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [logoFile, setLogoFile] = useState<File | null>(null);
  const [logoPreview, setLogoPreview] = useState<string | null>(null);
  const [schedule, setSchedule] =
    useState<Omit<ShopSchedule, "id" | "weekday_name">[]>(DEFAULT_SCHEDULE);

  const [form, setForm] = useState({
    name: "",
    description: "",
    address: "",
    city: "",
    phone: "",
    is_temporarily_closed: false,
    temporary_close_note: "",
  });

  useEffect(() => {
    const load = async () => {
      try {
        const [shopData, schedData] = await Promise.all([
          shopService.getMyShop(),
          shopService.getSchedule(),
        ]);

        setShop(shopData);
        setForm({
          name: shopData.name || "",
          description: shopData.description || "",
          address: shopData.address || "",
          city: shopData.city || "",
          phone: shopData.phone || "",
          is_temporarily_closed: shopData.is_temporarily_closed,
          temporary_close_note: shopData.temporary_close_note || "",
        });
        if (shopData.logo) setLogoPreview(shopData.logo);

        // Map schedule from API — fill missing days with defaults
        const mapped = DAYS.map((_, i) => {
          const found = schedData.find((s) => s.weekday === i);
          if (found)
            return {
              weekday: found.weekday,
              is_active: found.is_active,
              morning_open: found.morning_open || "",
              morning_close: found.morning_close || "",
              afternoon_open: found.afternoon_open || "",
              afternoon_close: found.afternoon_close || "",
            };
          return DEFAULT_SCHEDULE[i];
        });
        setSchedule(mapped);
      } catch (err: any) {
        if (err.response?.status === 401) router.push("/login");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [router]);

  const handleLogoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    setLogoFile(file);
    if (file) setLogoPreview(URL.createObjectURL(file));
  };

  const updateSlot = (
    dayIndex: number,
    field: keyof Omit<ShopSchedule, "id" | "weekday_name">,
    value: string | boolean | null,
  ) => {
    setSchedule((prev) =>
      prev.map((s, i) => (i === dayIndex ? { ...s, [field]: value } : s)),
    );
  };

  const handleSaveInfo = async (e: React.FormEvent) => {
    e.preventDefault();
    setSavingInfo(true);
    setError("");
    setSuccess("");

    try {
      const formData = new FormData();
      formData.append("name", form.name);
      formData.append("description", form.description);
      formData.append("address", form.address);
      formData.append("city", form.city);
      formData.append("phone", form.phone);
      formData.append(
        "is_temporarily_closed",
        String(form.is_temporarily_closed),
      );
      formData.append("temporary_close_note", form.temporary_close_note);
      if (logoFile instanceof File) formData.append("logo", logoFile);

      const updated = await shopService.updateMyShop(formData);
      setShop(updated);
      setLogoFile(null);
      setSuccess("Shop info saved.");
      setTimeout(() => setSuccess(""), 3000);
    } catch (err: any) {
      const data = err.response?.data;
      if (typeof data === "object") {
        setError(
          Object.entries(data)
            .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(", ") : v}`)
            .join(" | "),
        );
      } else {
        setError("Failed to save.");
      }
    } finally {
      setSavingInfo(false);
    }
  };

  const handleSaveSchedule = async () => {
    setSavingSched(true);
    setError("");
    setSuccess("");
    try {
      const payload = schedule.map((s) => ({
        weekday: s.weekday,
        is_active: s.is_active,
        morning_open: s.morning_open || null,
        morning_close: s.morning_close || null,
        afternoon_open: s.afternoon_open || null,
        afternoon_close: s.afternoon_close || null,
      }));
      await shopService.updateSchedule(payload);
      setSuccess("Schedule saved.");
      setTimeout(() => setSuccess(""), 3000);
    } catch {
      setError("Failed to save schedule.");
    } finally {
      setSavingSched(false);
    }
  };

  if (loading)
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center text-gray-400">
        Loading...
      </div>
    );

  if (!shop)
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center text-gray-400">
        No shop found.
      </div>
    );

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-2xl mx-auto px-4 py-6 space-y-6">
        <h1 className="text-xl font-bold text-gray-900">Shop settings</h1>

        {/* Verification banner */}
        {!shop.is_verified ? (
          <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl">
            <p className="text-sm font-medium text-amber-800">
              Pending admin verification
            </p>
            <p className="text-xs text-amber-600 mt-1">
              Your shop won't be visible to customers until verified by admin.
            </p>
          </div>
        ) : (
          <div className="p-4 bg-green-50 border border-green-200 rounded-xl flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-green-800">
                Shop verified and live
              </p>
              <p className="text-xs text-green-600 mt-1">
                Visible to customers.
              </p>
            </div>
            <span className="text-xs px-2 py-1 rounded-full font-medium bg-green-100 text-green-700">
              {shop.is_open ? "Open now" : "Closed now"}
            </span>
          </div>
        )}

        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
            {error}
          </div>
        )}
        {success && (
          <div className="p-3 bg-green-50 border border-green-200 rounded-lg text-green-700 text-sm">
            {success}
          </div>
        )}

        {/* ── SHOP INFO FORM ── */}
        <form
          onSubmit={handleSaveInfo}
          className="bg-white rounded-xl border border-gray-200 p-5 space-y-4"
        >
          <h2 className="font-semibold text-gray-900">Basic information</h2>

          {/* Logo */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Shop logo
            </label>
            {logoPreview && (
              <img
                src={logoPreview}
                alt="Logo"
                className="w-20 h-20 rounded-xl object-cover border border-gray-200 mb-2"
              />
            )}
            <input
              type="file"
              accept="image/*"
              onChange={handleLogoChange}
              className="w-full text-sm"
            />
            {shop.logo && !logoFile && (
              <p className="text-xs text-gray-400 mt-1">
                Leave empty to keep current logo
              </p>
            )}
          </div>

          {/* Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Shop name
            </label>
            <input
              type="text"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
              required
            />
          </div>

          {/* Phone */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Shop phone
            </label>
            <input
              type="text"
              value={form.phone}
              onChange={(e) => setForm({ ...form, phone: e.target.value })}
              placeholder="9800000000"
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>

          {/* Address + City */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Address
              </label>
              <input
                type="text"
                value={form.address}
                onChange={(e) => setForm({ ...form, address: e.target.value })}
                placeholder="Hattiban, Lalitpur"
                className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                City
              </label>
              <input
                type="text"
                value={form.city}
                onChange={(e) => setForm({ ...form, city: e.target.value })}
                placeholder="Lalitpur"
                className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
              />
            </div>
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description (optional)
            </label>
            <textarea
              value={form.description}
              onChange={(e) =>
                setForm({ ...form, description: e.target.value })
              }
              placeholder="Tell customers about your shop..."
              rows={3}
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500 resize-none"
            />
          </div>

          {/* Temporary closure */}
          <div className="border border-gray-200 rounded-lg p-4 space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-900">
                  Close shop today
                </p>
                <p className="text-xs text-gray-500">
                  Overrides schedule — shop shows as closed to customers
                </p>
              </div>
              <div
                className={`w-12 h-6 rounded-full transition-colors cursor-pointer ${form.is_temporarily_closed ? "bg-red-500" : "bg-gray-300"}`}
                onClick={() =>
                  setForm({
                    ...form,
                    is_temporarily_closed: !form.is_temporarily_closed,
                  })
                }
              >
                <div
                  className={`w-5 h-5 bg-white rounded-full shadow mt-0.5 transition-transform ${form.is_temporarily_closed ? "translate-x-6" : "translate-x-0.5"}`}
                />
              </div>
            </div>
            {form.is_temporarily_closed && (
              <input
                type="text"
                value={form.temporary_close_note}
                onChange={(e) =>
                  setForm({ ...form, temporary_close_note: e.target.value })
                }
                placeholder="Reason (optional) — e.g. Public holiday"
                className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-red-400"
              />
            )}
          </div>

          <button
            type="submit"
            disabled={savingInfo}
            className="w-full bg-green-600 hover:bg-green-700 text-white font-medium py-2.5 rounded-lg text-sm transition-colors disabled:opacity-50"
          >
            {savingInfo ? "Saving..." : "Save shop info"}
          </button>
        </form>

        
        {/* ── WEEKLY SCHEDULE ── */}
        {/* ── WEEKLY SCHEDULE ── */}
<div className="bg-white rounded-xl border border-gray-200 p-5">
    <h2 className="font-semibold text-gray-900 mb-1">Weekly schedule</h2>
    <p className="text-xs text-gray-500 mb-4">Set your hours or close a day</p>

    <div className="space-y-2">
        {schedule.map((slot, i) => (
            <div
                key={i}
                className={`rounded-lg border transition-colors ${
                    slot.is_active
                        ? 'border-gray-200'
                        : 'border-red-100 bg-red-50'
                }`}
            >
                {/* ── Top row — day name + hours summary + buttons ── */}
                <div className="flex items-center justify-between px-3 py-2.5 gap-2">
                    <div className="flex items-center gap-3 min-w-0 flex-1">
                        <span className={`text-sm font-medium w-24 flex-shrink-0 ${
                            slot.is_active ? 'text-gray-900' : 'text-red-400 line-through'
                        }`}>
                            {DAYS[i]}
                        </span>
                        {slot.is_active ? (
                            <span className="text-xs text-gray-500 truncate">
                                {slot.morning_open
                                    ? `${slot.morning_open}–${slot.morning_close}`
                                    : '—'
                                }
                                {slot.afternoon_open
                                    ? `  ·  ${slot.afternoon_open}–${slot.afternoon_close}`
                                    : ''
                                }
                            </span>
                        ) : (
                            <span className="text-xs text-red-400 font-medium">
                                Closed all day
                            </span>
                        )}
                    </div>

                    <div className="flex items-center gap-2 flex-shrink-0">
                        {/* ✅ Close/Open day button — always visible */}
                        {slot.is_active ? (
                            <button
                                type="button"
                                onClick={() => updateSlot(i, 'is_active', false)}
                                className="text-xs text-red-500 hover:text-red-700 border border-red-200 hover:border-red-400 hover:bg-red-50 px-2.5 py-1 rounded-lg transition-colors"
                            >
                                Close day
                            </button>
                        ) : (
                            <button
                                type="button"
                                onClick={() => updateSlot(i, 'is_active', true)}
                                className="text-xs text-green-600 hover:text-green-700 border border-green-200 hover:border-green-400 hover:bg-green-50 px-2.5 py-1 rounded-lg transition-colors"
                            >
                                Open day
                            </button>
                        )}

                        {/* Edit hours button */}
                        {slot.is_active && (
                            <button
                                type="button"
                                onClick={() => setExpandedDay(expandedDay === i ? null : i)}
                                className="text-xs text-gray-500 hover:text-gray-700 border border-gray-200 px-2.5 py-1 rounded-lg transition-colors"
                            >
                                {expandedDay === i ? 'Done' : 'Edit hours'}
                            </button>
                        )}
                    </div>
                </div>

                {/* ── Expanded editor — only when editing hours ── */}
                {slot.is_active && expandedDay === i && (
                    <div className="px-3 pb-3 pt-1 border-t border-gray-100 space-y-3">
                        {/* Morning */}
                        <div>
                            <p className="text-xs font-medium text-gray-500 mb-1.5">
                                Morning hours
                            </p>
                            <div className="flex items-center gap-2">
                                <input
                                    type="time"
                                    value={slot.morning_open || ''}
                                    onChange={e => updateSlot(i, 'morning_open', e.target.value)}
                                    className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                                />
                                <span className="text-gray-400 text-sm flex-shrink-0">to</span>
                                <input
                                    type="time"
                                    value={slot.morning_close || ''}
                                    onChange={e => updateSlot(i, 'morning_close', e.target.value)}
                                    className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                                />
                            </div>
                        </div>

                        {/* Afternoon */}
                        <div>
                            <div className="flex items-center justify-between mb-1.5">
                                <p className="text-xs font-medium text-gray-500">
                                    Afternoon hours
                                </p>
                                <button
                                    type="button"
                                    onClick={() => {
                                        const has = slot.afternoon_open
                                        updateSlot(i, 'afternoon_open',  has ? null : '14:00')
                                        updateSlot(i, 'afternoon_close', has ? null : '18:00')
                                    }}
                                    className="text-xs text-green-600 hover:text-green-700 font-medium"
                                >
                                    {slot.afternoon_open ? 'Remove afternoon' : '+ Add afternoon'}
                                </button>
                            </div>
                            {slot.afternoon_open ? (
                                <div className="flex items-center gap-2">
                                    <input
                                        type="time"
                                        value={slot.afternoon_open || ''}
                                        onChange={e => updateSlot(i, 'afternoon_open', e.target.value)}
                                        className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                                    />
                                    <span className="text-gray-400 text-sm flex-shrink-0">to</span>
                                    <input
                                        type="time"
                                        value={slot.afternoon_close || ''}
                                        onChange={e => updateSlot(i, 'afternoon_close', e.target.value)}
                                        className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                                    />
                                </div>
                            ) : (
                                <p className="text-xs text-gray-400">No afternoon slot</p>
                            )}
                        </div>
                    </div>
                )}
            </div>
        ))}
    </div>

    <button
        onClick={handleSaveSchedule}
        disabled={savingSched}
        className="w-full mt-4 bg-green-600 hover:bg-green-700 text-white font-medium py-2.5 rounded-lg text-sm transition-colors disabled:opacity-50"
    >
        {savingSched ? 'Saving...' : 'Save schedule'}
    </button>
</div>
      
      </div>
    </div>
  );
}
