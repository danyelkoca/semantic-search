<script lang="ts">
  import { onMount } from "svelte";
  import { bestSellers, trending } from "$stores/main";
  import Products from "$components/Products.svelte";
  import { Rainbow } from "svelte-loading-spinners";

  let loadingBestSellers = true;
  let loadingTrending = true;

  onMount(async () => {
    if ($bestSellers.length === 0) {
      const res = await fetch("/api/best-sellers");
      const data = await res.json();
      if (data.ok) {
        bestSellers.set(data.products);
      }
    }
    loadingBestSellers = false;

    if ($trending.length === 0) {
      const resTrending = await fetch("/api/trending");
      const dataTrending = await resTrending.json();
      if (dataTrending.ok) {
        trending.set(dataTrending.products);
      }
    }
    loadingTrending = false;
  });
</script>

<div class="flex flex-col gap-16">
  <section>
    <h2 class="text-2xl font-bold mb-4">Best Sellers</h2>
    {#if loadingBestSellers}
      <div class="flex justify-center items-center h-full w-full grow">
        <Rainbow size="60" color="#575C6E" unit="px" duration="2s" />
      </div>
    {:else if $bestSellers.length === 0}
      <div class="flex justify-center items-center h-full w-full grow text-center text-xl">No best sellers found.</div>
    {:else}
      <Products products={$bestSellers} showType="compact" />
    {/if}
  </section>

  <section>
    <h2 class="text-2xl font-bold mb-4">Trending Products</h2>
    {#if loadingTrending}
      <div class="flex justify-center items-center h-full w-full grow">
        <Rainbow size="60" color="#575C6E" unit="px" duration="2s" />
      </div>
    {:else if $trending.length === 0}
      <div class="flex justify-center items-center h-full w-full grow text-center text-xl">No trending products found.</div>
    {:else}
      <Products products={$trending} showType="compact" />
    {/if}
  </section>
</div>
