<script lang="ts">
  export let data;
  const product = data.product;
</script>

<main class="p-8 max-w-5xl mx-auto">
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
      <p><strong>Rating:</strong> {product.average_rating} ⭐ ({product.rating_number})</p>

      {#if product.features?.length}
        <div class="flex flex-wrap gap-2">
          {#each product.features as feature}
            <span class="text-xs bg-gray-200 px-2 py-1 rounded-full">{feature}</span>
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
</main>
