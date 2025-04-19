
import { backendReady } from "$stores/main";

export async function fetchProducts(query = "") {
    const endpoint = query ? `api/products?query=${encodeURIComponent(query)}` : `api/products`;
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

    while (true) {
        try {
            const res = await fetch(`api/health`);
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