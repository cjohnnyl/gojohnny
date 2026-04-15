"use client";
import { useMemo } from "react";

export type Conversation = {
  id: number;
  title: string;
  created_at?: string;
};

type Props = {
  conversations: Conversation[];
  currentId?: number;
  onSelect: (id: number) => void;
  onNewChat: () => void;
  isOpen: boolean;
  onClose?: () => void;
};

function groupConversationsByDate(conversations: Conversation[]) {
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);

  const sevenDaysAgo = new Date(today);
  sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);

  const groups: Record<string, Conversation[]> = {
    "Hoje": [],
    "Ontem": [],
    "Semana passada": [],
    "Anterior": [],
  };

  conversations.forEach((conv) => {
    const convDate = conv.created_at
      ? new Date(conv.created_at)
      : new Date();
    convDate.setHours(0, 0, 0, 0);

    if (convDate.getTime() === today.getTime()) {
      groups["Hoje"].push(conv);
    } else if (convDate.getTime() === yesterday.getTime()) {
      groups["Ontem"].push(conv);
    } else if (convDate.getTime() >= sevenDaysAgo.getTime()) {
      groups["Semana passada"].push(conv);
    } else {
      groups["Anterior"].push(conv);
    }
  });

  return groups;
}

export default function ChatSidebar({
  conversations,
  currentId,
  onSelect,
  onNewChat,
  isOpen,
  onClose,
}: Props) {
  const groupedConversations = useMemo(
    () => groupConversationsByDate(conversations),
    [conversations]
  );

  const groups = Object.entries(groupedConversations).filter(
    ([, convs]) => convs.length > 0
  );

  return (
    <>
      {/* Overlay para mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/50 sm:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed sm:relative inset-y-0 left-0 z-40 w-60 bg-zinc-900 border-r border-zinc-800 flex flex-col transition-transform duration-300 sm:translate-x-0 ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        {/* Header */}
        <div className="p-4 border-b border-zinc-800">
          <button
            onClick={onNewChat}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-white text-sm font-medium transition-colors"
            style={{
              background: "linear-gradient(135deg, #7c3aed, #a855f7)",
            }}
          >
            <svg
              className="w-4 h-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 4v16m8-8H4"
              />
            </svg>
            Novo chat
          </button>
        </div>

        {/* Conversations */}
        <div className="flex-1 overflow-y-auto">
          {groups.length === 0 ? (
            <div className="p-4 text-center text-zinc-400 text-sm">
              Nenhuma conversa ainda
            </div>
          ) : (
            <div className="space-y-1 p-4">
              {groups.map(([groupName, convs]) => (
                <div key={groupName}>
                  <h3 className="text-xs font-semibold text-zinc-500 uppercase mb-2 px-2 mt-4 first:mt-0">
                    {groupName}
                  </h3>
                  <div className="space-y-1">
                    {convs.map((conv) => (
                      <button
                        key={conv.id}
                        onClick={() => {
                          onSelect(conv.id);
                          onClose?.();
                        }}
                        className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors truncate ${
                          currentId === conv.id
                            ? "bg-zinc-800 text-white border-l-2 border-violet-500"
                            : "text-zinc-300 hover:bg-zinc-800/50"
                        }`}
                        title={conv.title}
                      >
                        {conv.title}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </aside>
    </>
  );
}
