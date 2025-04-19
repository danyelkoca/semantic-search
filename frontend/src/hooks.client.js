import { pastQueries, backendReady } from "$stores/main";
import { waitForBackendReady } from "$utils/db";

const storedQueries = localStorage.getItem('pastQueries') ? JSON.parse(localStorage.getItem('pastQueries')) : [];
const cleanedQueries = [...new Set(storedQueries.filter(query => query && query.trim() !== ''))];
pastQueries.set(cleanedQueries);

// Wrap inside an async function
async function initialize() {
    await waitForBackendReady();
    backendReady.set(true);
}

// Call it immediately
initialize();