<script lang="ts">
  import { onMount } from "svelte";
  import { trending } from "$stores/main";

  onMount(async () => {
    if ($trending.length > 0) {
      return;
    }

    const endpoint = "http://localhost:8000/trending";
    const res = await fetch(endpoint);
    const data = await res.json();

    if (data.ok) {
      trending.set(data.products);
    }
  });
</script>

<h2 class="text-2xl font-bold mb-4">Trending Products</h2>
<div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 xl:grid-cols-6 gap-4">
  {#each $trending as product}
    <a href={`/products/${product.product_id}`} class="relative block group overflow-hidden rounded-lg shadow hover:shadow-lg transition">
      {#if product.main_hi_res_image.length > 0}
        <img
          src={`https://m.media-amazon.com/images/I/${product.main_hi_res_image}`}
          alt={product.title}
          class="aspect-[4/3] w-full object-cover group-hover:scale-105 transition-transform"
        />
      {:else}
        <div class="aspect-[4/3] w-full bg-gray-200 flex items-center justify-center text-gray-500 text-sm">No Image</div>
      {/if}
      <div class="absolute bottom-0 left-0 right-0 bg-slate-700 bg-opacity-50 text-white text-xs p-2 flex justify-between items-center">
        <span class="truncate">{product.title || "Untitled"}</span>
        {#if product.price >= 0}
          <span class="ml-2 font-bold">${product.price.toFixed(2)}</span>
        {/if}
      </div>
    </a>
  {/each}
</div>
