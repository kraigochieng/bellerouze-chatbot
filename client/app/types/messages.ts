export interface IncomingMessage {
	phone_number_id: string;
	timestamp: string;
	type: "message";
	from_number: string;
	incoming_message: string;
}

export interface ReplyMessage {
	to_number: string;
	message_id: string;
	message: string;
}

export interface StatusUpdate {
	phone_number_id: string;
	timestamp: string;
	type: "status";
	status: string;
	message_id: string;
	recipient_id: string;
}

export interface MessageWithStatusResponse {
	incoming_message: IncomingMessage;
	reply_message: ReplyMessage;
	statuses: StatusUpdate[];
}

export interface IncomingChatMessage {
	id: string;
	text: string;
	timestamp: Date;
	type: "incoming";
	from: string; // sender phone number
}

// Outgoing message
export interface OutgoingChatMessage {
	id: string;
	text: string;
	timestamp: Date;
	type: "outgoing";
	from: "You";
	statuses: StatusUpdate[]; // only for outgoing
}

export interface ChatMessage {
	id: string;
	from: string;
	text: string;
	timestamp: Date; // always required
	type: "incoming" | "outgoing";
	statuses?: StatusUpdate[];
}
