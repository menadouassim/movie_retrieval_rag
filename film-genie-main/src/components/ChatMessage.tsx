import ReactMarkdown from "react-markdown";
import { Film, User } from "lucide-react";
import { cn } from "@/lib/utils";

export type Msg = { role: "user" | "assistant"; content: string };

export const ChatMessage = ({ message }: { message: Msg }) => {
  const isUser = message.role === "user";
  return (
    <div className={cn("flex gap-3 animate-fade-up", isUser && "flex-row-reverse")}>
      <div
        className={cn(
          "flex h-9 w-9 shrink-0 items-center justify-center rounded-full border",
          isUser
            ? "bg-secondary border-border"
            : "bg-primary/10 border-primary/30 text-primary"
        )}
      >
        {isUser ? <User className="h-4 w-4" /> : <Film className="h-4 w-4" />}
      </div>
      <div
        className={cn(
          "max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-sm",
          isUser
            ? "bg-primary text-primary-foreground rounded-tr-sm"
            : "bg-card border border-border rounded-tl-sm prose-chat"
        )}
      >
        {isUser ? (
          <p className="whitespace-pre-wrap">{message.content}</p>
        ) : (
          <ReactMarkdown>{message.content || "…"}</ReactMarkdown>
        )}
      </div>
    </div>
  );
};
