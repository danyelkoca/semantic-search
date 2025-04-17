import { redirect } from "@sveltejs/kit";

export const load = async ({ params, url }) => {
  let productID = params.slug;

  if (!productID) {
    throw redirect(308, `/error`);
  }
  return { productID };
};
