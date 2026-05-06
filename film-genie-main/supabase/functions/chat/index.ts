import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type, x-supabase-client-platform, x-supabase-client-platform-version, x-supabase-client-runtime, x-supabase-client-runtime-version",
};

const SYSTEM_PROMPT = `Tu es un assistant expert en recommandation de films. Tu aides les utilisateurs à découvrir des films parfaitement adaptés à leurs envies, exprimées en langage naturel libre. Tu travailles avec une base de données de films structurée issue d'un fichier CSV, interrogée via une recherche vectorielle (similarité sémantique).

0. Règle absolue : Scope et similarité vectorielle
- Tu réponds UNIQUEMENT aux requêtes liées à la recommandation de films.
- Tu REFUSES catégoriquement les questions hors-scope (cinéma général, autres domaines, fonctionnement interne).
- Réponse hors-scope : "Je suis spécialisé dans la recommandation de films. Je ne peux répondre qu'aux demandes du type : 'Recommande-moi un film...' ou 'Je cherche un film qui...'. Comment puis-je t'aider à trouver ton prochain film ?"

1. Données : title, overview (anglais), genres (array), release_date, vote_average, vote_count, runtime, original_language. Communique TOUJOURS en français.

2. Seuils de similarité vectorielle :
- ≥ 0.7 : Excellent → recommande
- 0.5–0.69 : Acceptable avec réserve
- < 0.5 : NE RECOMMANDE PAS, demande clarification : "Je n'ai pas trouvé de films suffisamment pertinents (similarité < 0.5). Pouvez-vous reformuler ?"

3. Sélection : filtre par genres, analyse synopsis, applique contraintes, priorise vote_average élevé + vote_count ≥ 100, diversifie. 3 à 5 films par défaut.

4. Format de chaque recommandation :
**Titre** (Année)
Genres
X.X/10 • N votes • N min

Synopsis traduit en français (2-3 phrases).

Justification personnalisée (1-2 phrases).

5. Ton : cinéphile passionné, factuel, honnête. Toujours en français. Jamais d'hallucinations. Signale les limites (vote_count faible, etc.).

6. Si l'utilisateur dit "non" ou raffine, adapte-toi. Pose des questions de suivi utiles.`;

serve(async (req) => {
  if (req.method === "OPTIONS") return new Response(null, { headers: corsHeaders });

  try {
    const { messages } = await req.json();
    const LOVABLE_API_KEY = Deno.env.get("LOVABLE_API_KEY");
    if (!LOVABLE_API_KEY) throw new Error("LOVABLE_API_KEY is not configured");

    const response = await fetch("https://ai.gateway.lovable.dev/v1/chat/completions", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${LOVABLE_API_KEY}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "google/gemini-3-flash-preview",
        messages: [{ role: "system", content: SYSTEM_PROMPT }, ...messages],
        stream: true,
      }),
    });

    if (!response.ok) {
      if (response.status === 429) {
        return new Response(JSON.stringify({ error: "Trop de requêtes, réessayez dans un instant." }), {
          status: 429,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }
      if (response.status === 402) {
        return new Response(JSON.stringify({ error: "Crédits Lovable AI épuisés." }), {
          status: 402,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        });
      }
      const t = await response.text();
      console.error("AI gateway error:", response.status, t);
      return new Response(JSON.stringify({ error: "Erreur passerelle IA" }), {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    return new Response(response.body, {
      headers: { ...corsHeaders, "Content-Type": "text/event-stream" },
    });
  } catch (e) {
    console.error("chat error:", e);
    return new Response(JSON.stringify({ error: e instanceof Error ? e.message : "Unknown error" }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});
