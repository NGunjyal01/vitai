"use client";

interface ChatMessageProps {
  role: "user" | "assistant";
  content: string;
  isStreaming?: boolean;
}

function formatContent(text: string) {
  // Split by newlines and process each line
  const lines = text.split("\n");

  return lines.map((line, i) => {
    // Bold: **text**
    const parts = line.split(/(\*\*[^*]+\*\*)/g);
    const formattedParts = parts.map((part, j) => {
      if (part.startsWith("**") && part.endsWith("**")) {
        return (
          <strong key={j} className="font-semibold">
            {part.slice(2, -2)}
          </strong>
        );
      }
      return part;
    });

    // Bullet points
    const trimmed = line.trim();
    if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
      return (
        <div key={i} className="flex gap-2 ml-2">
          <span className="text-gray-400 select-none">&#8226;</span>
          <span>{formattedParts.slice(0).map((p, idx) => (typeof p === 'string' ? p.replace(/^[-*]\s/, '') : p))}</span>
        </div>
      );
    }

    // Numbered list
    if (/^\d+\.\s/.test(trimmed)) {
      const match = trimmed.match(/^(\d+\.)\s/);
      return (
        <div key={i} className="flex gap-2 ml-2">
          <span className="text-gray-400 select-none font-medium">{match?.[1]}</span>
          <span>{formattedParts.map((p, idx) => (typeof p === 'string' ? p.replace(/^\d+\.\s/, '') : p))}</span>
        </div>
      );
    }

    // Empty line = paragraph break
    if (trimmed === "") {
      return <div key={i} className="h-2" />;
    }

    return (
      <div key={i}>
        {formattedParts}
      </div>
    );
  });
}

export default function ChatMessage({ role, content, isStreaming }: ChatMessageProps) {
  const isUser = role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-3`}>
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-400 to-teal-500 flex items-center justify-center mr-2 mt-1 flex-shrink-0">
          <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
          </svg>
        </div>
      )}
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
          isUser
            ? "bg-emerald-600 text-white rounded-br-md"
            : "bg-white text-gray-800 border border-gray-200 rounded-bl-md shadow-sm"
        }`}
      >
        <div className="space-y-0.5">
          {formatContent(content)}
        </div>
        {isStreaming && (
          <span className="inline-block w-1.5 h-4 bg-emerald-500 rounded-sm ml-0.5 animate-pulse" />
        )}
      </div>
    </div>
  );
}
