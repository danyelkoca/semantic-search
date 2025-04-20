import { error } from "@sveltejs/kit";

export const load = async ({ url, fetch }) => {
    const query = url.searchParams.get("query");
    const queryType = url.searchParams.get("query_type") || "vector";
    console.log(query, queryType);
    if (!query) {
        return { products: [], query, queryType }; // Empty state if no query
    }

    const res = await fetch(`/api/products?query=${encodeURIComponent(query)}&query_type=${encodeURIComponent(queryType)}`);

    if (!res.ok) {
        throw error(404, "Products not found");
    }

    const data = await res.json();
    if (!data.ok) {
        throw error(404, data.error || "Products not found");
    }

    return {
        products: data.products,
        query,
        queryType
    };
};
