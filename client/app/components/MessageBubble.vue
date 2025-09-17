<script setup lang="ts">
import type { MessageWithStatusResponse, StatusUpdate } from "@/types/messages";

interface Props {
	id: string;
	text: string;
	timestamp: Date;
	type: "incoming" | "outgoing";
	// statuses?: StatusUpdate[];
}

const props = defineProps<Props>();
</script>

<template>
	<div
		class="flex"
		:class="props.type === 'outgoing' ? 'justify-start' : 'justify-end'"
	>
		<div
			class="max-w-xs px-4 py-2 rounded-2xl shadow"
			:class="
				props.type === 'outgoing'
					? 'bg-blue-500 text-white rounded-br-none'
					: 'bg-white text-gray-800 rounded-bl-none'
			"
		>
			<!-- Message text -->
			<p class="whitespace-pre-wrap">{{ props.text }}</p>

			<!-- Timestamp + statuses -->
			<div class="text-xs opacity-70 mt-1 flex items-center space-x-1">
				<span>{{ props.timestamp.toLocaleTimeString() }}</span>

				<!-- Only show status for outgoing -->
				<!-- <span
					v-if="props.type === 'outgoing' && props.statuses?.length"
				>
					{{ props.statuses[props.statuses.length - 1].status ?? ''  }}
				</span> -->
			</div>
		</div>
	</div>
</template>
