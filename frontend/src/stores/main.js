import { writable } from 'svelte/store';

export const products = writable([]);
export const bestSellers = writable([]);
export const trending = writable([]);

export const pastQueries = writable([]);