import { error } from "@sveltejs/kit";

export const load = async ({ params, fetch }) => {
  const productID = params.slug;
  console.log(productID)

  const res = await fetch(`http://localhost:8000/products?product_id=${encodeURIComponent(productID)}`);

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