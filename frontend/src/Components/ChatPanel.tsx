import { useState } from "react"

interface Message {
  role: string
  text: string
}

interface Props {
  setFiles: (files: Record<string, string>) => void
}

export default function ChatPanel({ setFiles }: Props) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)

  const handleSend = async () => {
    if (!input.trim()) return

    // 1. Add user message
    setMessages(prev => [...prev, { role: "user", text: input }])
    setLoading(true)

    // 2. Add generating message
    setMessages(prev => [...prev, { role: "ai", text: "Generating your website..." }])

    try {
      // 3. Call FastAPI
      const response = await fetch("http://localhost:8000/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: input })
      })

      const data = await response.json()

      // 4. Pass files to PreviewPanel
      setFiles(data.result.files)

      // 5. Done message
      setMessages(prev => [...prev, { role: "ai", text: "Done! Your website is ready." }])

    } catch (error) {
      setMessages(prev => [...prev, { role: "ai", text: "Something went wrong." }])
    } finally {
      setLoading(false)
      setInput("")
    }
  }

  return (
    <div className="flex flex-col h-screen w-[30%] min-w-[300px] border-r border-white/10">

      <div className="p-4 border-b border-white/10 text-white font-bold">
        AI UI Designer
      </div>

      <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-3">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`px-4 py-2 rounded-lg text-sm max-w-[85%] ${
              msg.role === "user"
                ? "bg-violet-600 text-white self-end"
                : "bg-white/10 text-white self-start"
            }`}
          >
            {msg.text}
          </div>
        ))}
      </div>

      <div className="p-4 border-t border-white/10 flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          disabled={loading}
          className="flex-1 bg-white/5 text-white rounded-lg px-4 py-2 outline-none"
          placeholder="Describe your website..."
        />
        <button
          onClick={handleSend}
          disabled={loading}
          className="bg-violet-600 text-white px-4 py-2 rounded-lg disabled:opacity-50"
        >
          {loading ? "..." : "Send"}
        </button>
      </div>

    </div>
  )
}