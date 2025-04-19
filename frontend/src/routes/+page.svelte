<script lang="ts">
  import { onMount } from "svelte";
  import { backendReady, products } from "$stores/main";
  import { fetchProducts } from "$utils/db";
  import Products from "$components/Products.svelte";

  onMount(async () => {
    let fetchedProducts = await fetchProducts();
    console.log(fetchedProducts);
    products.set(fetchedProducts);
  });
</script>

{#if !$backendReady}
  <p class="text-center text-gray-500 mt-10 text-xl">🔄 Connecting to backend...</p>
{:else if $products.length === 0}
  <p class="text-center text-gray-500 mt-10 text-xl">No products found. Try a different search!</p>
{:else}
  <Products />
{/if}
