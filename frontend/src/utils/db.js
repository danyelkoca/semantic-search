
import { backendReady } from "$stores/main";

export async function fetchProducts(query = "") {
    const endpoint = query ? `http://localhost:8000/products?query=${encodeURIComponent(query)}` : "http://localhost:8000/products";
    try {
        const res = await fetch(endpoint);
        const data = await res.json();
        console.log(data);
        if (data.ok) {
            return data.products;
        }
        return [];
    } catch (error) {
        console.log("Products not fetched yet (backend might not be ready)");
        return [];
    }
}



export async function waitForBackendReady() {
    const healthUrl = "http://localhost:8000/health";

    while (true) {
        try {
            const res = await fetch(healthUrl);
            const data = await res.json();
            if (data.ok && data.ingestion_complete) {
                console.log("✅ Backend ready!");
                backendReady.set(true);
                break;
            } else {
                console.log("⏳ Backend not ready, waiting...");
            }
        } catch (error) {
            console.log("⏳ Backend not reachable yet, retrying...");
        }
        await new Promise((resolve) => setTimeout(resolve, 3000)); // Wait 3 seconds before retry
    }
}