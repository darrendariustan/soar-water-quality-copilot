"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { MessageCircle, X, Send, Bot } from "lucide-react";
import type { ChatMessage, ScenarioId, WaterTestResult } from "@/types";
import { sendChatMessage } from "@/lib/api";
import { initialChat } from "@/lib/mock-data";

interface ChatAssistantProps {
  activeScenario: ScenarioId | null;
  result?: WaterTestResult | null;
  onUpdateParams?: (params: Record<string, number>) => void;
}

export function ChatAssistant({ activeScenario, result, onUpdateParams }: ChatAssistantProps) {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>(initialChat);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, sending, open]);

  const handleSend = async () => {
    if (!input.trim() || sending) return;
    const userMsg: ChatMessage = {
      id: `m-${Date.now()}`,
      role: "user",
      content: input.trim(),
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setSending(true);

    const assistantId = `m-${Date.now() + 1}`;
    setMessages((prev) => [
      ...prev,
      {
        id: assistantId,
        role: "assistant",
        content: "",
        timestamp: new Date().toISOString(),
      },
    ]);

    try {
      const contextDict = result ? {
        risk_level: result.overallRisk,
        parameters: result.parameters?.reduce((acc: any, p) => ({ ...acc, [p.name]: p.value }), {})
      } : undefined;

      const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${API_URL}/api/chat/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          message: userMsg.content,
          history: messages.map(m => ({ role: m.role, content: m.content })),
          scenario: activeScenario ?? undefined,
          context: contextDict
        }),
      });

      if (res.body) {
        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let done = false;
        
        while (!done) {
          const { value, done: doneReading } = await reader.read();
          done = doneReading;
          if (value) {
            const chunk = decoder.decode(value, { stream: true });
            const lines = chunk.split("\n");
            for (const line of lines) {
              if (line.startsWith("data: ")) {
                const data = line.slice(6);
                try {
                  const parsed = JSON.parse(data);
                  if (parsed.text) {
                    let extractedParams: Record<string, number> | null = null;
                    
                    setMessages((prev) => prev.map((msg) => {
                      if (msg.id === assistantId) {
                        let newContent = msg.content + parsed.text;
                        const match = newContent.match(/\[UPDATE_PARAMS:\s*(\{.*?\})\s*\]/);
                        if (match) {
                          try {
                            extractedParams = JSON.parse(match[1]);
                            newContent = newContent.replace(match[0], "").trim();
                          } catch (e) {}
                        }
                        return { ...msg, content: newContent };
                      }
                      return msg;
                    }));

                    if (extractedParams && onUpdateParams) {
                      onUpdateParams(extractedParams);
                    }
                  } else if (parsed.error) {
                    setMessages((prev) => prev.map((msg) => 
                      msg.id === assistantId ? { ...msg, content: msg.content + "\n[Error: " + parsed.error + "]" } : msg
                    ));
                  }
                } catch (e) {}
              }
            }
          }
        }
      }
    } catch (err) {
       setMessages((prev) => prev.map((msg) => 
         msg.id === assistantId ? { ...msg, content: msg.content + "\n[Error: " + (err instanceof Error ? err.message : String(err)) + "]" } : msg
       ));
    } finally {
      setSending(false);
    }
  };

  return (
    <>
      {!open && (
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setOpen(true)}
          className="fixed bottom-5 right-5 z-30 flex items-center gap-2 rounded-full bg-water-400 px-5 py-3 text-white shadow-lg shadow-water-400/30"
        >
          <MessageCircle className="h-5 w-5" />
          <span className="hidden text-sm font-semibold sm:inline">
            Ask the assistant
          </span>
        </motion.button>
      )}

      <AnimatePresence>
        {open && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setOpen(false)}
              className="fixed inset-0 z-30 bg-ink/20 backdrop-blur-sm md:hidden"
            />
            <motion.aside
              initial={{ x: 360 }}
              animate={{ x: 0 }}
              exit={{ x: 360 }}
              transition={{ type: "spring", damping: 26, stiffness: 240 }}
              className="fixed right-0 top-0 z-40 flex h-full w-[340px] flex-col border-l border-line bg-paper shadow-xl"
            >
              <div className="flex items-center justify-between border-b border-line p-4">
                <div className="flex items-center gap-2.5">
                  <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-water-50 text-water-500">
                    <Bot className="h-4 w-4" />
                  </div>
                  <div>
                    <h2 className="font-display text-sm font-semibold text-ink">
                      Safety Assistant
                    </h2>
                    <p className="text-[10px] text-ink-soft">
                      Powered by the master agent
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => setOpen(false)}
                  className="text-ink-soft hover:text-ink"
                  aria-label="Close"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              <div className="flex-1 space-y-3 overflow-y-auto p-4">
                {messages.map((msg) => (
                  <motion.div
                    key={msg.id}
                    initial={{ opacity: 0, y: 6 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
                  >
                    <div
                      className={`max-w-[85%] rounded-2xl px-3.5 py-2 text-sm leading-relaxed ${
                        msg.role === "user"
                          ? "rounded-br-sm bg-water-400 text-white"
                          : "rounded-bl-sm bg-paper-soft text-ink"
                      }`}
                    >
                      {msg.content}
                    </div>
                  </motion.div>
                ))}
                {sending && (
                  <div className="flex justify-start">
                    <div className="rounded-2xl rounded-bl-sm bg-paper-soft px-3.5 py-2.5">
                      <span className="flex gap-1">
                        {[0, 1, 2].map((i) => (
                          <motion.span
                            key={i}
                            className="h-1.5 w-1.5 rounded-full bg-ink-soft"
                            animate={{ opacity: [0.3, 1, 0.3] }}
                            transition={{ repeat: Infinity, duration: 1, delay: i * 0.2 }}
                          />
                        ))}
                      </span>
                    </div>
                  </div>
                )}
                <div ref={endRef} />
              </div>

              <div className="border-t border-line p-4">
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleSend()}
                    placeholder="Ask about your water..."
                    className="flex-1 rounded-xl border border-line bg-paper px-3.5 py-2.5 text-sm text-ink placeholder-ink-soft/60 focus:border-water-400 focus:outline-none"
                  />
                  <button
                    onClick={handleSend}
                    disabled={!input.trim() || sending}
                    className="rounded-xl bg-water-400 px-3.5 text-white transition-colors hover:bg-water-500 disabled:opacity-40"
                    aria-label="Send"
                  >
                    <Send className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </motion.aside>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
