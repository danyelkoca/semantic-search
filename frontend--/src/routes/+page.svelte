<script>
  let query = "";
  let results = [];

  async function search() {
    const res = await fetch(`/products?query=${encodeURIComponent(query)}`);
    const data = await res.json();
    results = data.products;
  }

  async function loadInitial() {
    const res = await fetch("/products");
    const data = await res.json();
    results = data.products;
  }

  loadInitial();
</script>

<div class="max-w-7xl mx-auto p-4">
  <h1 class="text-3xl font-bold text-center mb-6">Semantic Fashion Search</h1>

  <form class="flex gap-4 justify-center mb-6" on:submit|preventDefault={search}>
    <input
      bind:value={query}
      type="text"
      placeholder="Try: outfit for summer beach trip"
      class="input input-bordered w-full max-w-md rounded-full border px-4 py-2"
    />
    <button type="submit" class="btn bg-blue-500 text-white px-6 py-2 rounded-full hover:bg-blue-600"> Search </button>
  </form>

  <div class="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-12 gap-4">
    {#each results as item}
      <a href={`/products/${item.id}`} class="block bg-white rounded-lg shadow hover:shadow-lg transition overflow-hidden">
        {#if item.main_hi_res_image}
          <img src={`https://m.media-amazon.com/images/I/${item.main_hi_res_image}`} alt="Product image" class="w-full aspect-square object-cover" />
        {/if}
        <div class="p-3">
          <h2 class="text-sm font-semibold truncate">{item.title}</h2>
          <p class="text-xs text-gray-500 truncate">{item.store}</p>
          <p class="text-xs text-gray-600">{item.price >= 0 ? `$${item.price.toFixed(2)}` : "N/A"}</p>
          <p class="text-xs text-yellow-500">{item.average_rating} ⭐ ({item.rating_number})</p>
        </div>
      </a>
    {/each}
  </div>
</div>
