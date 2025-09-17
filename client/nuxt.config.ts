import tailwindcss from "@tailwindcss/vite";
import dotenv from "dotenv";

dotenv.config({ path: "../.env" });
// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
	compatibilityDate: "2025-07-15",

	runtimeConfig: {
		public: {
			// apiBase: "http://localhost:8000",
			apiBase: `http://${process.env.SERVER_HOST || "localhost"}:${
				process.env.SERVER_PORT || 8000
			}`,
		},
	},

	modules: ["@nuxt/ui", "@vueuse/nuxt"],
	css: ["~/assets/css/main.css"],
	devtools: { enabled: false },
	vite: {
		plugins: [tailwindcss()],
	},
});
