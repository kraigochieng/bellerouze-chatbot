<script setup lang="ts">
import type { MessageWithStatusResponse, StatusUpdate } from "@/types/messages";
import type { PaginatedResponse } from "@/types/pagination"; // 👈 import your generic
import { getMessages } from "@@/api/messages";
import type { TableColumn } from "@nuxt/ui";
import { useQuery } from "@tanstack/vue-query";
import { ref } from "vue";
const phoneNumber = ref<string | undefined>(undefined);
const page = ref(1);
const size = ref(20);
const sizes = ref([10, 20, 50]);
import { capitalize } from "lodash";
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
			sort_order: "desc",
		}),
	refetchInterval: 10000, // ⏱ auto-refetch every 2s
});

type ChatRow = {
	from: string;
	message: string;
	reply: string;
	timestamp: string;
	statuses: StatusUpdate[];
};

const UBadge = resolveComponent("UBadge");
const columns: TableColumn<ChatRow>[] = [
	{
		accessorKey: "from",
		header: "From",
	},
	{
		accessorKey: "message",
		header: "Incoming Message",
		cell: ({ row }) => {
			const msg = row.getValue("message") as string;
			return h(
				"span",
				{ class: "truncate max-w-[200px] block", title: msg },
				msg
			);
		},
	},
	{
		accessorKey: "reply",
		header: "Reply",
		cell: ({ row }) => {
			const reply = row.getValue("reply") as string;
			return h(
				"span",
				{ class: "truncate max-w-[200px] block", title: reply },
				reply
			);
		},
	},
	{
		accessorKey: "timestamp",
		header: "Timestamp",
		cell: ({ row }) => {
			const ts = row.getValue("timestamp") as string;
			return new Date(ts).toLocaleString();
		},
	},
	{
		accessorKey: "statuses",
		header: "Statuses",
		cell: ({ row }) => {
			const statuses = row.getValue("statuses") as StatusUpdate[];

			return h(
				"div",
				{ class: "flex flex-wrap gap-1" },
				statuses.map((s) =>
					h(
						UBadge,
						{
							color:
								s.status === "read"
									? "success"
									: s.status === "delivered"
									? "info"
									: s.status === "sent"
									? "primary"
									: s.status === "failed"
									? "error"
									: "neutral",
							variant: "subtle",
							class: "capitalize",
							title: `${capitalize(s.status)} @ ${new Date(
								Number(s.timestamp) * 1000
							).toLocaleString()}`,
						},
						() => s.status
					)
				)
			);
		},
	},
];

// 🔑 Transform backend items into rows for UTable
const rows = computed(
	() =>
		messages.value?.items.map((msg) => ({
			from: msg.incoming_message.from_number,
			message: msg.incoming_message.incoming_message,
			timestamp: new Date(
				Number(msg.incoming_message.timestamp) * 1000
			).toLocaleString(),
			reply: msg.reply_message.message,
			statuses: msg.statuses,
		})) ?? []
);
</script>

<template>
	<div class="p-6">
		<ULink to="/phone">Phone</ULink>
		<h1 class="text-2xl font-bold mb-4">📩 Stored Messages</h1>

		<!-- Loading -->
		<div v-if="isLoading">
			<UProgress animation="swing" colour="neutral" />
		</div>

		<!-- Error -->
		<div v-else-if="isError" class="text-red-500">
			❌ Failed to load messages: {{ (error as Error).message }}
		</div>

		<div v-else>
			<USelect v-model="size" :items="sizes" />
			<UTable :data="rows" :columns="columns" />
			<UPagination
				v-model:page="page"
				:items-per-page="messages?.size"
				:total="messages?.total"
				active-color="neutral"
			/>
		</div>
	</div>
</template>
