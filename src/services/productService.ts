// src/services/productService.ts
import api from "@/lib/api";
import { Product } from "@/types";

interface ProductFilters {
  shop?: number;
  category?: string;
  city?: string;
}

export const productService = {
  getProducts: async (filters?: ProductFilters): Promise<Product[]> => {
    const res = await api.get("/api/products/", { params: filters });
    return res.data;
  },

  getProduct: async (id: number): Promise<Product> => {
    const res = await api.get(`/api/products/${id}/`);
    return res.data;
  },

  getMyProducts: async (): Promise<Product[]> => {
    const res = await api.get("/api/products/my-products/");
    return res.data;
  },

  createProduct: async (data: FormData): Promise<Product> => {
    const res = await api.post("/api/products/create/", data);
    // ✅ Do NOT manually set Content-Type — axios sets it automatically
    // with the correct boundary when you pass FormData
    return res.data;
  },

  updateProduct: async (id: number, data: FormData): Promise<Product> => {
    const res = await api.patch(`/api/products/${id}/update/`, data);
    // ✅ Same here — let axios handle the multipart boundary automatically
    return res.data;
  },

  deleteProduct: async (id: number): Promise<void> => {
    await api.delete(`/api/products/${id}/delete/`);
  },

  getCategories: async () => {
    const res = await api.get("/api/products/categories/");
    return res.data;
  },
};