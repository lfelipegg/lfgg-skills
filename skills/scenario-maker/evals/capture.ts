import { appendFileSync, readFileSync } from "node:fs";
import type { ExtensionAPI } from "@oh-my-pi/pi-coding-agent";

// Capture client-visible provenance, never credentials or provider headers.
export default function (pi: ExtensionAPI) {
  pi.on("before_agent_start", (_event, ctx) => {
    const systemPrompt = readFileSync(process.env.EVAL_SYSTEM_FILE!, "utf8");
    appendFileSync(process.env.EVAL_CONTEXT_FILE!, JSON.stringify({type: "eval_context", systemPrompt, cwd: ctx.cwd,
      model: {provider: ctx.model?.provider, id: ctx.model?.id, name: ctx.model?.name},
      thinking: pi.getThinkingLevel(), tools: pi.getActiveTools()}) + "\n");
    return {systemPrompt};
  });
  pi.on("before_provider_request", (event) => {
    const payload = event.payload;
    appendFileSync(process.env.EVAL_CONTEXT_FILE!, JSON.stringify({type: "provider_request", eventKeys: Object.keys(event),
      payloadKeys: payload && typeof payload === "object" ? Object.keys(payload) : [],
      // These body fields expose instructions/settings/tools, not authentication.
      observed: payload && typeof payload === "object" ? Object.fromEntries(
        Object.entries(payload).filter(([key]) =>
          ["model", "instructions", "reasoning", "text", "temperature", "top_p", "seed", "service_tier", "tools", "input", "messages", "system"].includes(key))) : null}) + "\n");
  });
}
