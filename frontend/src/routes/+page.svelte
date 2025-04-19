<script lang="ts">
  import { onMount } from "svelte";
  import { products, loading } from "$stores/main";
  import { fetchProducts } from "$utils/db";
  import Products from "$components/Products.svelte";

  onMount(async () => {
    if ($products.length === 0) {
      const fetchedProducts = await fetchProducts();
      products.set(fetchedProducts);
    }
  });
</script>

<Products />
