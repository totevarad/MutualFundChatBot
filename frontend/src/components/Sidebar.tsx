"use client";

import { MessageSquare, Plus, Settings } from "lucide-react";
import clsx from "clsx";

export default function Sidebar({ onNewChat }: { onNewChat: () => void }) {
  return (
    <div className="w-64 h-full bg-surface-container-low border-r border-outline-variant flex flex-col">
      <div className="p-4 border-b border-outline-variant">
        <h1 className="text-xl font-bold text-primary mb-4">SmartInvest AI</h1>
        <button
          onClick={onNewChat}
          className="w-full flex items-center justify-center gap-2 bg-primary text-background py-2 rounded font-medium hover:bg-opacity-90 transition"
        >
          <Plus size={18} /> New Conversation
        </button>
      </div>

      <div className="flex-1 overflow-y-auto custom-scrollbar p-2">
        <div className="text-xs text-outline mb-2 mt-4 px-2 font-mono uppercase">Today</div>
        <button className="w-full text-left px-3 py-2 rounded hover:bg-surface-container-high transition flex items-center gap-3 text-sm text-secondary truncate">
          <MessageSquare size={16} className="text-outline" />
          HDFC Flexi Cap details...
        </button>
      </div>

      <div className="p-4 border-t border-outline-variant">
        <button className="flex items-center gap-3 text-secondary hover:text-primary transition">
          <Settings size={18} />
          <span>Settings</span>
        </button>
      </div>
    </div>
  );
}
