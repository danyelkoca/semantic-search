<script>
  import { products } from "$stores/main";
  import { fetchProducts } from "$utils/db";

  let debounceTimeout;
  let isMenuOpen = false;

  import { pastQueries } from "$stores/main";
  function handleInput(query) {
    clearTimeout(debounceTimeout);
    debounceTimeout = setTimeout(async () => {
      let fetchedProducts = await fetchProducts(query);
      products.set(fetchedProducts);
    }, 500); // Adjust the debounce time as needed
  }

  function handleBlur(query) {
    clearTimeout(debounceTimeout);
    debounceTimeout = setTimeout(() => {
      // Strip whitespace before adding to storedQueries
      let trimmedQuery = query.trim();

      // Update pastQueries in localStorage and writable store if trimmedQuery is not empty
      if (trimmedQuery) {
        let storedQueries = JSON.parse(localStorage.getItem("pastQueries")) || [];
        // Remove the query if it already exists to avoid duplicates
        storedQueries = storedQueries.filter((q) => q !== trimmedQuery);
        // Push the query to the top of the list
        storedQueries.unshift(trimmedQuery);
        // Keep only the latest 100 queries
        storedQueries = storedQueries.slice(0, 100);
        localStorage.setItem("pastQueries", JSON.stringify(storedQueries));
        pastQueries.set(storedQueries);
      }
    }, 500); // Add a 500 ms delay
  }

  function toggleMenu() {
    isMenuOpen = !isMenuOpen;
  }

  let showSuggestions = false;
</script>

<header class="bg-white border-b border-[1px] border-slate-200 top-0 z-10">
  <div class="px-4 py-2 mx-auto flex justify-between items-center gap-4">
    <a href="/" style="font-family: 'Do Hyeon', Inter;" class="text-4xl text-sky-900 text-center">metro</a>
    <div class="relative">
      <input
        type="text"
        placeholder="Search for outfits..."
        class="px-4 py-2 grow rounded-full max-w-[300px] border-slate-200 border"
        on:input={(event) => handleInput(event.currentTarget.value)}
        on:focus={() => (showSuggestions = true)}
        on:blur={(event) => {
          setTimeout(() => (showSuggestions = false), 200);
          handleBlur(event.currentTarget.value);
        }}
      />
      {#if showSuggestions && $pastQueries.length > 0}
        <ul class="absolute bg-white border border-slate-200 rounded-md mt-1 w-full max-w-[300px] z-10">
          {#each $pastQueries.slice(0, 5) as query}
            <li class="px-2 py-1 text-xs hover:bg-slate-100 cursor-pointer" on:click={() => handleInput(query)}>
              {query}
            </li>
          {/each}
        </ul>
      {/if}
    </div>
    <button class="lg:hidden text-sky-900 text-4xl cursor-pointer" on:click={toggleMenu} aria-label="Toggle menu"> ☰ </button>
    <nav class="hidden lg:flex space-x-4">
      <a href="/best-selling" class="text-sky-900 font-bold">Best Selling</a>
      <a href="/trending" class="text-sky-900 font-bold">Trending</a>
    </nav>
  </div>
  {#if isMenuOpen}
    <nav class="lg:hidden bg-white border-t border-slate-200">
      <a href="/best-selling" class="block px-4 py-2 text-sky-900 font-bold">Best Selling</a>
      <a href="/trending" class="block px-4 py-2 text-sky-900 font-bold">Trending</a>
    </nav>
  {/if}
</header>
