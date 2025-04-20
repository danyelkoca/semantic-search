<script>
  import Products from "$components/Products.svelte";

  export let data;

  let products = [];
  let query = "";
  let queryType = "";
  let friendlyQueryType = "";

  $: products = data.products || [];
  $: query = data.query || "";
  $: queryType = data.queryType || "";

  $: friendlyQueryType = queryType === "vector" ? "Vector" : queryType === "hybrid" ? "Hybrid" : "Keyword";
</script>

<div class="space-y-4 py-4">
  {#if query}
    <div class="text-center text-gray-700">
      <p class="text-xl">Showing results for: <strong>{query}</strong></p>
      <p class="text-sm text-gray-500">Query Type: {friendlyQueryType}</p>
    </div>
  {/if}

  <Products {products} />
</div>
