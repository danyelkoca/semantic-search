export async function fetchProducts(query = "") {
    const endpoint = query ? `http://localhost:8000/products?query=${encodeURIComponent(query)}` : "http://localhost:8000/products";
    const res = await fetch(endpoint);
    const data = await res.json();
    console.log(data)
    if (data.ok) {
        return data.products;
    }

    return []
}