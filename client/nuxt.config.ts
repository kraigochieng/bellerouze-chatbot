import tailwindcss from "@tailwindcss/vite";
// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
				compatibilityDate: "2025-07-15",

				runtimeConfig: {
								public: {
												apiBase: "http://localhost:8000",
								},
				},

				modules: ["@nuxt/ui", "@vueuse/nuxt"],
				css: ["~/assets/css/main.css"],
				devtools: { enabled: false },
				vite: {
								plugins: [tailwindcss()],
				},
});