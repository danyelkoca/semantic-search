<script lang="ts">
  import { onMount } from "svelte";

  let products = [];
  let query = "";
  let loading = false;
  let timeout: NodeJS.Timeout;

  async function fetchProducts(search = "") {
    loading = true;
    const endpoint = search ? `http://localhost:8000/products?query=${encodeURIComponent(search)}` : "http://localhost:8000/products";
    const res = await fetch(endpoint);
    const data = await res.json();
    if (data.ok) {
      products = search ? data.products : data.products || [];
    } else {
      products = [];
    }
    loading = false;
  }

  onMount(() => {
    fetchProducts();
  });

  function handleInput(e: Event) {
    query = (e.target as HTMLInputElement).value;
    fetchProducts(query);
  }
</script>

<!-- NAVBAR -->
<header class="bg-white shadow-sm sticky top-0 z-10">
  <div class="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
    <h1 class="text-2xl font-bold text-blue-600">Semantic Fashion Search</h1>
    <input
      type="text"
      placeholder="Search for outfits..."
      class="p-2 px-4 w-72 rounded-full border focus:outline-none focus:ring focus:border-blue-400"
      bind:value={query}
      on:input={handleInput}
    />
  </div>
</header>

<!-- RESULTS -->
<main class="p-6 bg-gray-50 min-h-screen">
  {#if loading}
    <div class="flex justify-center mt-10">
      <div class="w-10 h-10 border-4 border-blue-300 border-t-transparent rounded-full animate-spin"></div>
    </div>
  {:else if products.length === 0}
    <p class="text-center text-gray-500 mt-10 text-xl">No products found. Try a different search!</p>
  {:else}
    <div class="grid gap-6 grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 2xl:grid-cols-12">
      {#each products as product}
        <a
          href={`/products/${product.product_id}`}
          class="block bg-white rounded-lg overflow-hidden shadow hover:shadow-xl hover:-translate-y-1 transition transform"
        >
          {#if product.main_hi_res_image.length > 0}
            <div class="relative">
              <img src={`https://m.media-amazon.com/images/I/${product.main_hi_res_image}`} alt={product.title} class="w-full h-32 object-cover" />
            </div>
          {:else}
            <div class="w-full h-32 bg-gray-200 flex items-center justify-center">
              <span class="text-gray-500 text-sm">No Image Available</span>
            </div>
          {/if}
          {#if product.price >= 0}
            <span class="absolute top-2 right-2 bg-blue-500 text-white text-xs font-bold px-2 py-1 rounded">
              ${product.price.toFixed(2)}
            </span>
          {/if}
          <div class="p-3 space-y-2">
            <h2 class="font-semibold text-sm truncate">{product.title || "Untitled"}</h2>
            <p class="text-xs text-gray-500 truncate">{product.store || "Unknown Store"}</p>

            <div class="flex items-center text-xs gap-[2px]">
              {#each Array(5) as _, i}
                {#if product.average_rating >= i + 1}
                  <!-- Full Star -->
                  <svg class="w-4 h-4 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.286 3.957h4.146c.969 0 1.371 1.24.588 1.81l-3.356 2.44
        1.285 3.956c.3.922-.755 1.688-1.54 1.118l-3.356-2.44-3.356 2.44c-.784.57-1.838-.196-1.539-1.118l1.285-3.956-3.356-2.44c-.783-.57-.38-1.81.588-1.81h4.146z"
                    />
                  </svg>
                {:else if product.average_rating >= i + 0.5}
                  <!-- Half Star -->
                  <svg class="w-4 h-4" viewBox="0 0 20 20">
                    <defs>
                      <linearGradient id="half-grad">
                        <stop offset="50%" stop-color="rgb(250, 204, 21)" />
                        <!-- yellow-400 -->
                        <stop offset="50%" stop-color="rgb(209, 213, 219)" />
                        <!-- gray-300 -->
                      </linearGradient>
                    </defs>
                    <path
                      fill="url(#half-grad)"
                      d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.286 3.957h4.146c.969 0 1.371 1.24.588 1.81l-3.356 2.44
        1.285 3.956c.3.922-.755 1.688-1.54 1.118l-3.356-2.44-3.356 2.44c-.784.57-1.838-.196-1.539-1.118l1.285-3.956-3.356-2.44c-.783-.57-.38-1.81.588-1.81h4.146z"
                    />
                  </svg>
                {:else}
                  <!-- Empty Star -->
                  <svg class="w-4 h-4 text-gray-300" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.286 3.957h4.146c.969 0 1.371 1.24.588 1.81l-3.356 2.44
        1.285 3.956c.3.922-.755 1.688-1.54 1.118l-3.356-2.44-3.356 2.44c-.784.57-1.838-.196-1.539-1.118l1.285-3.956-3.356-2.44c-.783-.57-.38-1.81.588-1.81h4.146z"
                    />
                  </svg>
                {/if}
              {/each}
              <span class="text-gray-500 ml-1">({product.rating_number})</span>
            </div>

            {#if product.features?.length}
              <div class="flex flex-wrap gap-1">
                {#each product.features.slice(0, 3) as feature}
                  <span class="bg-gray-200 truncate text-gray-600 text-[10px] px-2 py-[2px] rounded-full">{feature}</span>
                {/each}
                {#if product.features.length > 3}
                  <span class="text-blue-500 text-xs">+{product.features.length - 3} more</span>
                {/if}
              </div>
            {/if}
          </div>
        </a>
      {/each}
    </div>
  {/if}
</main>
