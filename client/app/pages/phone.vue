<script setup lang="ts">
import type { MessageWithStatusResponse } from "@/types/messages";
import type { PaginatedResponse } from "@/types/pagination"; // 👈 import your generic
import { getMessages } from "@@/api/messages";
import { useQuery } from "@tanstack/vue-query";
import { ref } from "vue";

const phoneNumber = ref<string | undefined>("254792701195");
const page = ref(1);
const size = ref(20);
const sizes = ref([10, 20, 50]);

const {
	data: messages,
	error,
	isLoading,
	isError,
	isPending,
} = useQuery<PaginatedResponse<MessageWithStatusResponse>>({
	queryKey: ["messages", phoneNumber, page, size],
	queryFn: () =>
		getMessages({
			phoneNumber: phoneNumber.value,
			page: page.value,
			size: size.value,
			sort_order: "asc",
		}),
	refetchInterval: 10000,
});

const groupedMessages = computed(() => {
	if (!messages.value?.items) return [];

	const groups: Record<string, MessageWithStatusResponse[]> = {};

	messages.value.items.forEach((msg) => {
		const ts = msg.incoming_message.timestamp;
		if (!ts) return; // skip if no timestamp

		const dayKey = new Date(Number(ts) * 1000)
			.toISOString()
			.split("T")[0] as string;

		if (!groups[dayKey]) groups[dayKey] = [];
		groups[dayKey].push(msg);
	});

	// Return sorted array of date groups
	return Object.entries(groups)
		.sort(([a], [b]) => (a < b ? 1 : -1))
		.map(([date, items]) => ({ date, items }));
});

const bottomEl = ref<HTMLDivElement | null>(null);

watch(groupedMessages, async () => {
	await nextTick();
	bottomEl.value?.scrollIntoView({ behavior: "smooth" });
});
</script>

<template>
	<ULink to="/">home</ULink>
	<p>{{ phoneNumber }}</p>
	<div class="p-6 h-screen flex flex-col">
		<!-- Loading -->
		<div v-if="isLoading" class="flex-1 flex items-center justify-center">
			<UProgress animation="swing" color="neutral" />
		</div>

		<!-- Error -->
		<div
			v-else-if="isError"
			class="flex-1 flex items-center justify-center text-red-500"
		>
			❌ Failed to load messages: {{ (error as Error).message }}
		</div>

		<!-- Chat -->
		<div
			v-else
			class="flex-1 space-y-4 p-4 bg-gray-100 rounded-lg flex flex-col-reverse"
		>
			<div
				v-for="group in groupedMessages"
				:key="group.date"
				class="space-y-2"
			>
				<!-- Day separator -->
				<div class="text-center text-sm text-gray-500 my-2">
					{{ group.date }}
				</div>

				<!-- Messages -->
				<div
					v-for="msg in group.items"
					:key="msg.incoming_message.timestamp"
					class="space-y-1"
				>
					<!-- Incoming message -->
					<MessageBubble
						:id="'in-' + msg.incoming_message.timestamp"
						:text="msg.incoming_message.incoming_message"
						:timestamp="
							new Date(
								Number(msg.incoming_message.timestamp) * 1000
							)
						"
						type="incoming"
					/>

					<!-- Reply message -->
					<MessageBubble
						:id="'out-' + msg.incoming_message.timestamp"
						:text="msg.reply_message.message"
						:timestamp="
							new Date(
								Number(msg.incoming_message.timestamp) * 1000
							)
						"
						type="outgoing"
						:statuses="msg.statuses"
					/>
				</div>
			</div>
		</div>
		<div ref="bottomEl"></div>
	</div>
</template>
