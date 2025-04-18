<script lang="ts">
  export let data;
  const product = data.product;
</script>

<div class="flex flex-col lg:flex-row gap-8">
  {#if product.main_hi_res_image}
    <img
      class="rounded-lg max-w-full max-h-[500px] object-contain"
      src={`https://m.media-amazon.com/images/I/${product.main_hi_res_image}`}
      alt={product.title}
    />
  {/if}

  <div class="flex-1 space-y-4">
    <h1 class="text-2xl font-bold">{product.title || "Untitled Product"}</h1>

    <p><strong>Store:</strong> {product.store || "Unknown"}</p>
    <p><strong>Price:</strong> {product.price >= 0 ? `$${product.price.toFixed(2)}` : "N/A"}</p>
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
      <div class="flex flex-wrap gap-2">
        {#each product.features as feature}
          <span class="text-xs bg-gray-200 px-2 py-1 rounded">{feature}</span>
        {/each}
      </div>
    {/if}

    {#if product.details}
      <details open class="mt-4">
        <summary class="cursor-pointer font-semibold">Details</summary>
        <ul class="list-disc list-inside text-sm mt-2">
          {#each Object.entries(JSON.parse(product.details || "{}")) as [key, value]}
            <li><strong>{key}:</strong> {value}</li>
          {/each}
        </ul>
      </details>
    {/if}
  </div>
</div>
