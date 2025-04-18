<script>
  import { products } from "$stores/main";
</script>

{#if $products.length !== 0}
  <div class="grid gap-4 grid-cols-2 md:grid-cols-3 lg:grid-cols-4 2xl:grid-cols-6">
    {#each $products as product (product.product_id)}
      <div class="block bg-white rounded-lg overflow-hidden shadow hover:shadow-xl hover:-translate-y-1 transition transform relative">
        {#if product.main_hi_res_image.length > 0}
          <div class="relative">
            <img
              src={`https://m.media-amazon.com/images/I/${product.main_hi_res_image}`}
              alt={product.title}
              class="aspect-[4/3] w-full h-full object-cover"
            />
          </div>
        {:else}
          <div class="aspect-[4/3] w-full bg-gray-200 flex items-center justify-center">
            <span class="text-gray-500 text-sm">No Image Available</span>
          </div>
        {/if}
        {#if product.price >= 0}
          <span class="absolute top-2 right-2 bg-slate-600 text-white text-xs font-bold px-2 py-1 rounded">
            ${product.price.toFixed(2)}
          </span>
        {/if}
        <div class="p-3 space-y-2">
          <a href={`/products/${product.product_id}`} class="text-sky-500 text-sm block overflow-hidden text-ellipsis whitespace-normal line-clamp-2"
            >{product.title || "Untitled"}</a
          >
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
              {#each product.features as feature, index}
                {#if index < 3 || product.showAllFeatures}
                  <span class="bg-gray-200 truncate text-gray-600 text-[10px] px-2 py-[2px] rounded">{feature}</span>
                {/if}
              {/each}

              {#if product.features.length > 3}
                <button class="text-blue-500 text-xs cursor-pointer" on:click={() => (product.showAllFeatures = !product.showAllFeatures)}>
                  {product.showAllFeatures ? "See less" : `See ${product.features.length - 3} more`}
                </button>
              {/if}
            </div>
          {/if}
        </div>
      </div>
    {/each}
  </div>
{/if}
