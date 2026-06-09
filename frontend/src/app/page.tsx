"use client";

import { useState, useRef, useEffect } from "react";
import Sidebar from "@/components/Sidebar";
import MarketTicker from "@/components/MarketTicker";
import { Send, ExternalLink, Bot, User } from "lucide-react";
import { sendMessage, clearMemory } from "@/lib/api";
import ReactMarkdown from "react-markdown";

interface Message {
  role: "user" | "assistant";
  content: string;
  source_url?: string;
}

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [userId, setUserId] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Generate simple UUID for session
    let id = localStorage.getItem("user_id");
    if (!id) {
      id = "user_" + Math.random().toString(36).substring(2, 15);
      localStorage.setItem("user_id", id);
    }
    setUserId(id);
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;
    
    const userMessage = input.trim();
    setInput("");
    setMessages(prev => [...prev, { role: "user", content: userMessage }]);
    setIsLoading(true);

    try {
      const res = await sendMessage(userMessage, userId);
      setMessages(prev => [...prev, { 
        role: "assistant", 
        content: res.answer,
        source_url: res.source_url 
      }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: "assistant", content: "Sorry, I encountered an error. Please try again." }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = async () => {
    if (userId) {
      await clearMemory(userId);
    }
    setMessages([]);
  };

  return (
    <div className="flex h-screen bg-background text-secondary overflow-hidden">
      {/* Sidebar - Desktop Only for now */}
      <div className="hidden md:block">
        <Sidebar onNewChat={handleNewChat} />
      </div>

      <div className="flex-1 flex flex-col min-w-0">
        <MarketTicker />
        
        {/* Header */}
        <header className="h-16 flex items-center px-6 border-b border-outline-variant bg-surface-container-low shrink-0 justify-between">
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 rounded-full bg-primary animate-pulse"></div>
            <span className="font-semibold text-tertiary">Live Chat</span>
          </div>
        </header>

        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto custom-scrollbar p-6 animated-mesh-bg">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center max-w-2xl mx-auto space-y-8">
              <div className="w-16 h-16 bg-surface-container-high rounded-full flex items-center justify-center mb-4">
                <Bot size={32} className="text-primary" />
              </div>
              <h2 className="text-3xl font-bold text-tertiary">How can I help with your investments today?</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full">
                {["What is an SIP?", "Compare HDFC Flexi Cap and Large Cap", "What is expense ratio?", "Explain NAV"].map((q) => (
                  <button 
                    key={q}
                    onClick={() => setInput(q)}
                    className="p-4 rounded-xl border border-outline-variant bg-surface-container-low hover:border-primary transition text-left text-sm"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="max-w-3xl mx-auto space-y-6">
              {messages.map((m, i) => (
                <div key={i} className={`flex gap-4 ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  {m.role === 'assistant' && (
                    <div className="w-8 h-8 rounded-full bg-surface-container-highest flex items-center justify-center shrink-0">
                      <Bot size={18} className="text-primary" />
                    </div>
                  )}
                  <div className={`max-w-[80%] rounded-2xl p-4 ${m.role === 'user' ? 'bg-primary text-background rounded-tr-sm' : 'bg-surface-container-low border border-outline-variant rounded-tl-sm'}`}>
                    {m.role === 'assistant' ? (
                      <div className="prose prose-invert prose-p:leading-relaxed prose-pre:bg-surface-container-highest max-w-none">
                        <ReactMarkdown>{m.content}</ReactMarkdown>
                      </div>
                    ) : (
                      <p>{m.content}</p>
                    )}
                    
                    {m.source_url && m.source_url !== "Unknown" && m.source_url !== "" && (
                      <a href={m.source_url} target="_blank" rel="noreferrer" className="mt-3 inline-flex items-center gap-1 text-xs bg-surface-container-highest hover:bg-outline-variant text-tertiary px-2 py-1 rounded transition border border-outline-variant">
                        <ExternalLink size={12} /> Source
                      </a>
                    )}
                  </div>
                  {m.role === 'user' && (
                    <div className="w-8 h-8 rounded-full bg-surface-container-high flex items-center justify-center shrink-0">
                      <User size={18} className="text-secondary" />
                    </div>
                  )}
                </div>
              ))}
              {isLoading && (
                <div className="flex gap-4">
                  <div className="w-8 h-8 rounded-full bg-surface-container-highest flex items-center justify-center shrink-0">
                    <Bot size={18} className="text-primary" />
                  </div>
                  <div className="bg-surface-container-low border border-outline-variant rounded-2xl rounded-tl-sm p-4 flex items-center h-12">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-primary rounded-full animate-typing-dot" style={{ animationDelay: '0ms' }}></div>
                      <div className="w-2 h-2 bg-primary rounded-full animate-typing-dot" style={{ animationDelay: '200ms' }}></div>
                      <div className="w-2 h-2 bg-primary rounded-full animate-typing-dot" style={{ animationDelay: '400ms' }}></div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="p-4 bg-background border-t border-outline-variant">
          <div className="max-w-3xl mx-auto relative">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask a factual mutual fund question..."
              className="w-full bg-surface-container-low border border-outline-variant rounded-full py-4 pl-6 pr-14 text-tertiary placeholder:text-outline focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition"
            />
            <button 
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              className="absolute right-2 top-2 p-2 bg-primary text-background rounded-full hover:bg-opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              <Send size={18} />
            </button>
          </div>
          <div className="text-center mt-3 text-xs text-outline font-mono">
            SmartInvest AI provides facts, not financial advice.
          </div>
        </div>
      </div>
    </div>
  );
}
