import { FormEvent, useEffect, useRef, useState } from "react";
import { Film, Send, Sparkles } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ChatMessage, type Msg } from "@/components/ChatMessage";

const CHAT_URL = `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/chat`;

const SUGGESTIONS = [
  "Un thriller psychologique tordu avec un twist final",
  "Un film feel-good pour un dimanche pluvieux",
  "Une animation poétique pour toute la famille",
  "Un classique des années 70 à redécouvrir",
];

const Index = () => {
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  const send = async (text: string) => {
    if (!text.trim() || isLoading) return;
    const userMsg: Msg = { role: "user", content: text.trim() };
    const next = [...messages, userMsg];
    setMessages(next);
    setInput("");
    setIsLoading(true);

    let assistantSoFar = "";
    const upsertAssistant = (chunk: string) => {
      assistantSoFar += chunk;
      setMessages((prev) => {
        const last = prev[prev.length - 1];
        if (last?.role === "assistant") {
          return prev.map((m, i) =>
            i === prev.length - 1 ? { ...m, content: assistantSoFar } : m
          );
        }
        return [...prev, { role: "assistant", content: assistantSoFar }];
      });
    };

    try {
      const resp = await fetch(CHAT_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY}`,
        },
        body: JSON.stringify({ messages: next }),
      });

      if (!resp.ok || !resp.body) {
        if (resp.status === 429) toast.error("Trop de requêtes, patientez un instant.");
        else if (resp.status === 402) toast.error("Crédits IA épuisés.");
        else toast.error("Une erreur est survenue.");
        setIsLoading(false);
        return;
      }

      const reader = resp.body.getReader();
      const decoder = new TextDecoder();
      let buf = "";
      let done = false;

      while (!done) {
        const { done: d, value } = await reader.read();
        if (d) break;
        buf += decoder.decode(value, { stream: true });
        let i: number;
        while ((i = buf.indexOf("\n")) !== -1) {
          let line = buf.slice(0, i);
          buf = buf.slice(i + 1);
          if (line.endsWith("\r")) line = line.slice(0, -1);
          if (!line.startsWith("data: ")) continue;
          const json = line.slice(6).trim();
          if (json === "[DONE]") { done = true; break; }
          try {
            const p = JSON.parse(json);
            const c = p.choices?.[0]?.delta?.content;
            if (c) upsertAssistant(c);
          } catch {
            buf = line + "\n" + buf;
            break;
          }
        }
      }
    } catch (e) {
      console.error(e);
      toast.error("Erreur de connexion.");
    } finally {
      setIsLoading(false);
    }
  };

  const onSubmit = (e: FormEvent) => {
    e.preventDefault();
    send(input);
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b border-border/60 backdrop-blur-xl bg-background/40 sticky top-0 z-10">
        <div className="container max-w-4xl flex items-center justify-between py-4">
          <div className="flex items-center gap-3">
            <div className="relative h-10 w-10 rounded-xl bg-primary/10 border border-primary/30 grid place-items-center">
              <Film className="h-5 w-5 text-primary" />
              <span className="absolute -inset-1 rounded-xl bg-primary/20 blur-md -z-10" />
            </div>
            <div>
              <h1 className="text-lg font-semibold tracking-tight">
                Cinéphile<span className="text-gold">.AI</span>
              </h1>
              <p className="text-xs text-muted-foreground">
                Recommandations de films par recherche sémantique
              </p>
            </div>
          </div>
          <div className="hidden sm:flex items-center gap-2 text-xs text-muted-foreground">
            <Sparkles className="h-3.5 w-3.5 text-primary" />
            Propulsé par IA
          </div>
        </div>
      </header>

      {/* Main */}
      <main className="flex-1 container max-w-4xl flex flex-col py-6">
        {messages.length === 0 ? (
          <div className="flex-1 flex flex-col items-center justify-center text-center px-4 animate-fade-up">
            <div className="relative mb-6">
              <div className="h-20 w-20 rounded-2xl bg-card border border-border grid place-items-center shadow-[var(--shadow-elegant)]">
                <Film className="h-9 w-9 text-primary" />
              </div>
              <div className="absolute inset-0 rounded-2xl bg-primary/30 blur-2xl -z-10" />
            </div>
            <h2 className="text-3xl sm:text-4xl font-semibold tracking-tight max-w-xl">
              Trouvez votre prochain film en{" "}
              <span className="text-gold">une phrase</span>
            </h2>
            <p className="mt-3 text-muted-foreground max-w-md">
              Décrivez l'envie, l'ambiance ou le style — je fouille la base et vous
              propose les meilleures correspondances.
            </p>

            <div className="mt-10 grid sm:grid-cols-2 gap-3 w-full max-w-2xl">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => send(s)}
                  className="text-left p-4 rounded-xl bg-card border border-border hover:border-primary/50 hover:bg-secondary/50 transition-all duration-200 group"
                >
                  <span className="text-sm text-foreground/90 group-hover:text-foreground">
                    {s}
                  </span>
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div
            ref={scrollRef}
            className="flex-1 overflow-y-auto scrollbar-thin space-y-5 pr-2"
          >
            {messages.map((m, i) => (
              <ChatMessage key={i} message={m} />
            ))}
            {isLoading && messages[messages.length - 1]?.role === "user" && (
              <div className="flex gap-3 animate-fade-up">
                <div className="h-9 w-9 rounded-full bg-primary/10 border border-primary/30 grid place-items-center">
                  <Film className="h-4 w-4 text-primary" />
                </div>
                <div className="bg-card border border-border rounded-2xl rounded-tl-sm px-4 py-3 flex gap-1.5 items-center">
                  <span className="typing-dot h-2 w-2 rounded-full bg-primary" style={{ animationDelay: "0s" }} />
                  <span className="typing-dot h-2 w-2 rounded-full bg-primary" style={{ animationDelay: "0.2s" }} />
                  <span className="typing-dot h-2 w-2 rounded-full bg-primary" style={{ animationDelay: "0.4s" }} />
                </div>
              </div>
            )}
          </div>
        )}

        {/* Composer */}
        <form
          onSubmit={onSubmit}
          className="mt-6 sticky bottom-4 bg-card/80 backdrop-blur-xl border border-border rounded-2xl p-2 shadow-[var(--shadow-elegant)] flex items-end gap-2"
        >
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                send(input);
              }
            }}
            placeholder="Décris le film que tu cherches…"
            rows={1}
            className="resize-none border-0 bg-transparent focus-visible:ring-0 shadow-none min-h-[44px] max-h-40"
          />
          <Button
            type="submit"
            size="icon"
            disabled={!input.trim() || isLoading}
            className="h-11 w-11 shrink-0 rounded-xl"
          >
            <Send className="h-4 w-4" />
          </Button>
        </form>
        <p className="text-center text-xs text-muted-foreground mt-2">
          Spécialisé en recommandation de films · Réponses en français
        </p>
      </main>
    </div>
  );
};

export default Index;
