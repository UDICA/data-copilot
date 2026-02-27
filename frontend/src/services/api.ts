import type { ChatEvent, DataSource } from '../types';

/**
 * Send a chat message and stream the response as server-sent events.
 *
 * POSTs to /api/chat with the full message history, then reads the SSE
 * response stream, parsing each event into a ChatEvent object.
 *
 * @param messages - Array of {role, content} message objects.
 * @yields ChatEvent objects as they arrive from the server.
 */
export async function* sendChatMessage(
  messages: Array<{ role: string; content: string }>
): AsyncGenerator<ChatEvent> {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ messages }),
  });

  if (!response.ok) {
    yield {
      type: 'error',
      content: `Server responded with ${response.status}: ${response.statusText}`,
    };
    return;
  }

  const reader = response.body?.getReader();
  if (!reader) {
    yield { type: 'error', content: 'No response stream available.' };
    return;
  }

  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');

    // Keep the last (potentially incomplete) line in the buffer
    buffer = lines.pop() ?? '';

    let currentEventType = '';

    for (const line of lines) {
      if (line.startsWith('event:')) {
        currentEventType = line.slice(6).trim();
      } else if (line.startsWith('data:')) {
        const dataStr = line.slice(5).trim();
        if (!dataStr) continue;

        try {
          const parsed = JSON.parse(dataStr) as ChatEvent;
          // Use the event type from the SSE envelope if present
          if (currentEventType && !parsed.type) {
            parsed.type = currentEventType as ChatEvent['type'];
          }
          yield parsed;
        } catch {
          // Skip malformed JSON lines
        }

        currentEventType = '';
      }
    }
  }
}

/**
 * Fetch the list of configured data sources from the server.
 *
 * @returns Array of DataSource objects.
 */
export async function getDataSources(): Promise<DataSource[]> {
  try {
    const response = await fetch('/api/sources');
    if (!response.ok) {
      return [];
    }
    const data = await response.json();
    return data.sources ?? [];
  } catch {
    return [];
  }
}
