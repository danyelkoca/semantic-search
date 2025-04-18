<script lang="ts">
  import { onMount } from "svelte";
  import { products } from "$stores/main";
  import Products from "$components/Products.svelte";
  import { fetchProducts } from "$utils/db";

  let loading = false;
  let fetchedProducts = [];

  let popularProducts = [];

  onMount(async () => {
    let fetchedProducts = await fetchProducts();
    console.log(fetchedProducts);
    products.set(fetchedProducts);

    const endpoint = "http://localhost:8000/products/popular";
    const res = await fetch(endpoint);
    const data = await res.json();

    if (data.ok) {
      popularProducts = data.products;
    }
  });
</script>

{#if $products.length === 0}
  <p class="text-center text-gray-500 mt-10 text-xl">No products found. Try a different search!</p>
{:else}
  <Products />
{/if}
