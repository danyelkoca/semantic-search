<script lang="ts">
  import { onMount } from "svelte";
  import { products } from "$stores/main";
  import Products from "$components/Products.svelte";
  import { fetchProducts } from "$utils/db";

  onMount(async () => {
    let fetchedProducts = await fetchProducts();
    console.log(fetchedProducts);
    products.set(fetchedProducts);
  });
</script>

{#if $products.length === 0}
  <p class="text-center text-gray-500 mt-10 text-xl">No products found. Try a different search!</p>
{:else}
  <Products />
{/if}
