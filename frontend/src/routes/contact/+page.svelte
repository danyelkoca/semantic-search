<script>
  const send = (event) => {
    event.preventDefault();
    alert("Message sent");
  };
</script>

<form on:submit={send} class="flex flex-col gap-4 max-w-[700px] w-full mx-auto relative">
  <div class="flex gap-4 flex-col lg:flex-row">
    <label class="w-[120px] flex items-center" for="name">Name</label>
    <input required class="grow bg-white rounded border-2 px-4 py-2 border-slate-200" id="name" type="text" placeholder="Your name" maxlength="50" />
  </div>

  <div class="flex gap-4 flex-col lg:flex-row">
    <label class="w-[120px] flex items-center" for="email">Email</label>
    <input
      class={`grow bg-white rounded border-2 px-4 py-2 border-slate-200`}
      id="email"
      type="email"
      required
      placeholder="name@example.com"
      maxlength="50"
    />
  </div>

  <div class="flex gap-4 flex-col lg:flex-row">
    <label class="w-[120px] flex items-center" for="message">Message</label>
    <textarea
      class={`grow bg-white rounded border-2 px-4 py-2 border-slate-200`}
      id="message"
      required
      rows="6"
      maxlength="1000"
      placeholder="Your question/feedback"
    ></textarea>
  </div>

  <div class="flex justify-center items-center flex-col gap-2">
    <button type="submit" class="cursor-pointer px-4 py-2 text-white rounded-full flex gap-2 items-center justify-center min-w-[120px] bg-blue-500">
      <span>Send</span>
    </button>
  </div>
</form>
