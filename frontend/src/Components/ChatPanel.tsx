import { useState } from "react"
import type { GeneratedFiles, GenerationMeta } from "../App"

interface Message {
  id: string
  role: "user" | "system" | "error"
  text: string
}

interface Props {
  meta: GenerationMeta
  onGenerated: (files: GeneratedFiles, prompt: string) => void
}

function createMessage(role: Message["role"], text: string): Message {
  return {
    id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
    role,
    text
  }
}

export default function ChatPanel({ meta, onGenerated }: Props) {
  const [messages, setMessages] = useState<Message[]>([
    createMessage("system", "Backend ready. Submit a prompt to generate a website.")
  ])
  const [input, setInput] = useState("Create futuristic AI startup website")
  const [loading, setLoading] = useState(false)

  const handleSend = async () => {
    const prompt = input.trim()
    if (!prompt || loading) return

    setLoading(true)
    setMessages((prev) => [
      ...prev,
      createMessage("user", prompt),
      createMessage("system", "Generation started. Waiting for backend response.")
    ])

    try {
      const response = await fetch("/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data?.detail || "Generation failed")
      }

      const files = data?.result?.files || {}
      console.info("[frontend] generated files", Object.keys(files))
      onGenerated(files, prompt)

      setMessages((prev) => [
        ...prev,
        createMessage(
          "system",
          `Generation completed. Received ${Object.keys(files).length} files.`
        )
      ])
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown error"
      setMessages((prev) => [...prev, createMessage("error", message)])
    } finally {
      setLoading(false)
    }
  }

  return (
    <aside className="flex min-h-0 flex-col border-r border-[#2a2c31] bg-[#16171b] max-lg:border-b max-lg:border-r-0">
      <div className="border-b border-[#2a2c31] px-5 py-4">
        <div className="text-sm uppercase tracking-[0.18em] text-[#d3ff72]">Agentic UI</div>
        <h1 className="mt-2 text-xl font-semibold text-[#f8f4ea]">Website Generator</h1>
      </div>

      <div className="grid grid-cols-3 border-b border-[#2a2c31] text-sm">
        <div className="px-4 py-3">
          <div className="text-[#8f969f]">Files</div>
          <div className="mt-1 font-semibold">{meta.fileCount}</div>
        </div>
        <div className="border-x border-[#2a2c31] px-4 py-3">
          <div className="text-[#8f969f]">Pages</div>
          <div className="mt-1 font-semibold">{meta.pageCount}</div>
        </div>
        <div className="px-4 py-3">
          <div className="text-[#8f969f]">Status</div>
          <div className="mt-1 font-semibold">{loading ? "Running" : "Idle"}</div>
        </div>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto px-4 py-4">
        <div className="flex flex-col gap-3">
          {messages.map((message) => (
            <div
              key={message.id}
              className={[
                "rounded-md border px-3 py-2 text-sm leading-6",
                message.role === "user"
                  ? "ml-6 border-[#d3ff72]/30 bg-[#d3ff72]/10 text-[#f6ffd8]"
                  : "",
                message.role === "system"
                  ? "mr-6 border-[#3b3f46] bg-[#202227] text-[#d8dce0]"
                  : "",
                message.role === "error"
                  ? "mr-6 border-[#ff6b6b]/40 bg-[#ff6b6b]/10 text-[#ffd0d0]"
                  : ""
              ].join(" ")}
            >
              {message.text}
            </div>
          ))}
        </div>
      </div>

      <div className="border-t border-[#2a2c31] p-4">
        <textarea
          value={input}
          onChange={(event) => setInput(event.target.value)}
          disabled={loading}
          rows={4}
          className="h-28 w-full resize-none rounded-md border border-[#30333a] bg-[#0f1013] px-3 py-3 text-sm leading-6 text-[#f8f4ea] outline-none transition focus:border-[#d3ff72]/70 disabled:opacity-60"
          placeholder="Describe the website to generate"
        />
        <button
          type="button"
          onClick={handleSend}
          disabled={loading || !input.trim()}
          className="mt-3 w-full rounded-md bg-[#d3ff72] px-4 py-3 text-sm font-semibold text-[#12140f] transition hover:bg-[#e0ff94] disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? "Generating..." : "Generate Website"}
        </button>
      </div>
    </aside>
  )
}
