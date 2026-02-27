/** A single message in the chat conversation. */
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: ToolSource[];
  timestamp: Date;
  isStreaming?: boolean;
}

/** Attribution metadata for a tool used during a response. */
export interface ToolSource {
  tool_name: string;
  type: 'sql' | 'file' | 'web' | 'analysis';
}

/** A server-sent event from the /api/chat SSE stream. */
export interface ChatEvent {
  type: 'token' | 'tool_start' | 'tool_result' | 'done' | 'error';
  content?: string;
  tool_name?: string;
  tool_args?: Record<string, unknown>;
  sources?: string[];
}

/** A connected data source (database, directory, etc.). */
export interface DataSource {
  id: string;
  name: string;
  type: 'database' | 'directory';
  status: 'connected' | 'disconnected' | 'error';
  details: string;
}
