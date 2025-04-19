
import { backendReady } from "$stores/main";

export async function fetchProducts(query = "") {
    const BACKEND_URL = import.meta.env.VITE_BACKEND_URL
    const endpoint = query ? `${baseUrl}/products?query=${encodeURIComponent(query)}` : `${BACKEND_URL}/products`;
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
    const BACKEND_URL = import.meta.env.VITE_BACKEND_URL
    const healthUrl = `${BACKEND_URL}/health`;

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