import type { MessageWithStatusResponse } from "@/types/messages";
import type { PaginatedResponse } from "@/types/pagination";



export async function getMessages({
	phoneNumber,
	page = 1,
	size = 20,
	sort_order = "desc",
}: {
	phoneNumber?: string;
	page?: number;
	size?: number;
	sort_order?: "asc" | "desc";
}): Promise<PaginatedResponse<MessageWithStatusResponse>> {
	const config = useRuntimeConfig();

	return await $fetch<PaginatedResponse<MessageWithStatusResponse>>(
		`${config.public.apiBase}/messages`,
		{
			params: {
				phone_number: phoneNumber,
				page,
				size,
				sort_order,
			},
		}
	);
}
