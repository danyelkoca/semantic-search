import { error } from "@sveltejs/kit";

export const load = async ({ params, fetch }) => {
  const productID = params.slug;
  console.log(productID)

  const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;
  const res = await fetch(`${BACKEND_URL}/products?product_id=${encodeURIComponent(productID)}`);

  if (!res.ok) {
    throw error(404, "Product not found");
  }

  const data = await res.json();
  console.log(data)
  if (!data.ok) {
    throw error(404, data.error || "Product not found");
  }

  return {
    product: data.product
  };
};