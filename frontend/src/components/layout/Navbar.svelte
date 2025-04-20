<script>
  import { goto } from "$app/navigation";
  import { pastQueries } from "$stores/main";
  import { Circle } from "svelte-loading-spinners";
  let isMenuOpen = false;
  let searchQuery = "";
  let queryType = "vector";
  let isSearching = false;

  async function handleSearch() {
    if (searchQuery.trim() === "") return;
    isSearching = true;
    await goto(`/search?query=${encodeURIComponent(searchQuery.trim())}&query_type=${queryType}`);
    if (searchQuery.trim()) {
      pastQueries.update((queries) => {
        const filtered = queries.filter((q) => q !== searchQuery.trim());
        const updated = [searchQuery.trim(), ...filtered].slice(0, 5);
        localStorage.setItem("pastQueries", JSON.stringify(updated));
        return updated;
      });
    }
    isSearching = false;
  }

  function toggleMenu() {
    isMenuOpen = !isMenuOpen;
  }
</script>

<header class="bg-white border-b border-[1px] border-slate-200 top-0 z-10">
  <div class="p-4 mx-auto flex justify-between items-center gap-4">
    <a href="/" style="font-family: 'Do Hyeon', Inter;" class="text-4xl text-sky-900 text-center">
      <span class="hidden sm:inline">metro</span>
      <span class="sm:hidden">m</span>
    </a>
    <div class="relative flex flex-col gap-2">
      <form class="flex items-center gap-2" on:submit|preventDefault={handleSearch}>
        <input
          type="text"
          placeholder="Search..."
          class="h-10 px-4 rounded-lg grow w-full mx-auto max-w-[500px] sm:min-w-[300px] md:min-w-[400px] lg:min-w-[500px] border-slate-200 border"
          bind:value={searchQuery}
          required
        />
        <select bind:value={queryType} class="h-10 px-3 rounded-lg border border-slate-200 bg-white text-slate-700 text-sm">
          <option value="keyword">Keyword</option>
          <option selected value="vector">Vector</option>
          <option value="hybrid">Hybrid</option>
        </select>
        <button
          disabled={isSearching}
          type="submit"
          class="h-10 bg-sky-900 cursor-pointer text-white px-4 rounded-lg hover:bg-sky-700 transition flex items-center justify-center"
        >
          {#if isSearching}
            <Circle size="20" color="#ffffff" unit="px" duration="1.2s" />
          {:else}
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" class="h-5 w-5" fill="white">
              <path
                d="M448 768A320 320 0 1 0 448 128a320 320 0 0 0 0 640z m297.344-76.992l214.592 214.592-54.336 54.336-214.592-214.592a384 384 0 1 1 54.336-54.336z"
              />
            </svg>
          {/if}
        </button>
      </form>

      <div class="flex flex-wrap text-xs text-slate-600">
        {#each $pastQueries.slice(0, 5) as query}
          <button
            class="mx-1 cursor-pointer text-sky-600 hover:underline"
            on:click={() => {
              searchQuery = query;
              handleSearch();
            }}
          >
            {query}
          </button>
        {/each}
      </div>
    </div>
    <button class="lg:hidden text-sky-900 text-4xl cursor-pointer" on:click={toggleMenu} aria-label="Toggle menu"> ☰ </button>
    <nav class="hidden lg:flex space-x-4">
      <a href="/best-sellers" class="text-sky-900">Best-Sellers</a>
      <a href="/trending" class="text-sky-900">Trending</a>
    </nav>
  </div>
  {#if isMenuOpen}
    <nav class="lg:hidden bg-white border-t border-slate-200">
      <a href="/best-sellers" class="block px-4 py-2 text-sky-900">Best-Sellers</a>
      <a href="/trending" class="block px-4 py-2 text-sky-900">Trending</a>
    </nav>
  {/if}
</header>
