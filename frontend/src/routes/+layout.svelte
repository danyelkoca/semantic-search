<script>
  let { children } = $props();
  import Navbar from "$components/layout/Navbar.svelte";
  import "../app.css";
</script>

<!-- NAVBAR -->
<div class="min-h-screen flex flex-col bg-slate-50">
  <Navbar />
  <div class="p-4 grow">
    {@render children()}
  </div>
  <footer class="bg-slate-100 text-center p-4 flex items-center justify-around">
    <p class="text-slate-600 text-sm">© 2025 Metro. All rights reserved.</p>
    <div class="flex justify-center space-x-4 mt-2">
      <a href="/about" class="text-slate-600 hover:text-slate-800 text-sm">About</a>
      <a href="/contact" class="text-slate-600 hover:text-slate-800 text-sm">Contact</a>
    </div>
  </footer>
</div>
