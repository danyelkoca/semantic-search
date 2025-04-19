import adapter from '@sveltejs/adapter-static';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	kit: {
		adapter: adapter({
			fallback: '200.html',
			pages: 'build',     // 🔥 ensure output to build/
			assets: 'build'     // 🔥 ensure output to build/
		}),
		paths: {
			base: '',
		},
		alias: {
			$components: "./src/components",
			$stores: "./src/stores",
			$images: "./src/images",
			$icons: "./src/icons",
			$utils: "./src/utils",
			$data: "./src/data",
		},
	},
};

export default config;