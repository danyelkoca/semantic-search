import { pastQueries } from "$stores/main";

const storedQueries = localStorage.getItem('pastQueries') ? JSON.parse(localStorage.getItem('pastQueries')) : [];
const cleanedQueries = [...new Set(storedQueries.filter(query => query && query.trim() !== ''))];
pastQueries.set(cleanedQueries);
