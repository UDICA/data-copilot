import { useState, useCallback } from 'react';
import type { ChatMessage, ToolSource } from '../types';
import { sendChatMessage } from '../services/api';

/** Map a tool name to its source type for badge display. */
function classifyTool(toolName: string): ToolSource['type'] {
  if (toolName.startsWith('sql_') || toolName.includes('query') || toolName.includes('schema')) {
    return 'sql';
  }
  if (toolName.startsWith('file_') || toolName.includes('read') || toolName.includes('browse') || toolName.includes('parse')) {
    return 'file';
  }
  if (toolName.startsWith('web_') || toolName.includes('search') || toolName.includes('fetch')) {
    return 'web';
  }
  return 'analysis';
}

/** Generate a unique ID for messages. */
function makeId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

/**
 * Chat state management hook.
 *
 * Manages the message list, loading state, and the send flow that
 * streams assistant responses from the backend SSE endpoint.
 */
export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: makeId(),
      role: 'user',
      content: content.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    // Build the full history for the API
    const apiMessages = [...messages, userMessage].map(m => ({
      role: m.role,
      content: m.content,
    }));

    // Create a placeholder assistant message
    const assistantId = makeId();
    const assistantMessage: ChatMessage = {
      id: assistantId,
      role: 'assistant',
      content: '',
      sources: [],
      timestamp: new Date(),
      isStreaming: true,
    };

    setMessages(prev => [...prev, assistantMessage]);

    try {
      let accumulatedContent = '';
      const accumulatedSources: ToolSource[] = [];

      for await (const event of sendChatMessage(apiMessages)) {
        switch (event.type) {
          case 'token':
            accumulatedContent += event.content ?? '';
            // Collect sources from token events
            if (event.sources) {
              for (const src of event.sources) {
                if (!accumulatedSources.some(s => s.tool_name === src)) {
                  accumulatedSources.push({
                    tool_name: src,
                    type: classifyTool(src),
                  });
                }
              }
            }
            setMessages(prev =>
              prev.map(m =>
                m.id === assistantId
                  ? { ...m, content: accumulatedContent, sources: [...accumulatedSources], isStreaming: true }
                  : m
              )
            );
            break;

          case 'tool_start':
            // Track tool usage via source badges only — no inline text
            if (event.tool_name && !accumulatedSources.some(s => s.tool_name === event.tool_name)) {
              accumulatedSources.push({
                tool_name: event.tool_name,
                type: classifyTool(event.tool_name),
              });
              setMessages(prev =>
                prev.map(m =>
                  m.id === assistantId
                    ? { ...m, sources: [...accumulatedSources], isStreaming: true }
                    : m
                )
              );
            }
            break;

          case 'tool_result':
            if (event.tool_name && !accumulatedSources.some(s => s.tool_name === event.tool_name)) {
              accumulatedSources.push({
                tool_name: event.tool_name,
                type: classifyTool(event.tool_name),
              });
            }
            break;

          case 'done':
            // Collect any final sources
            if (event.sources) {
              for (const src of event.sources) {
                if (!accumulatedSources.some(s => s.tool_name === src)) {
                  accumulatedSources.push({
                    tool_name: src,
                    type: classifyTool(src),
                  });
                }
              }
            }
            setMessages(prev =>
              prev.map(m =>
                m.id === assistantId
                  ? { ...m, content: accumulatedContent, sources: [...accumulatedSources], isStreaming: false }
                  : m
              )
            );
            break;

          case 'error':
            accumulatedContent += `\n\n${event.content ?? 'An error occurred.'}`;
            setMessages(prev =>
              prev.map(m =>
                m.id === assistantId
                  ? { ...m, content: accumulatedContent, isStreaming: false }
                  : m
              )
            );
            break;
        }
      }

      // Ensure streaming flag is cleared
      setMessages(prev =>
        prev.map(m =>
          m.id === assistantId ? { ...m, isStreaming: false } : m
        )
      );
    } catch {
      setMessages(prev =>
        prev.map(m =>
          m.id === assistantId
            ? { ...m, content: 'Failed to connect to the server. Please check that the backend is running.', isStreaming: false }
            : m
        )
      );
    } finally {
      setIsLoading(false);
    }
  }, [messages, isLoading]);

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  return { messages, isLoading, sendMessage, clearMessages };
}
