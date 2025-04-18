import { writable } from 'svelte/store';

export const products = writable([]);
export const bestSellingProducts = writable([]);
export const trendingProducts = writable([]);

export const pastQueries = writable([]);