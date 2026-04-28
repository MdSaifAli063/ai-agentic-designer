import { useState } from "react"
import ChatPanel from "./Components/ChatPanel"
import PreviewPanel from "./Components/PreviewPanel"

export type GeneratedFiles = Record<string, string>

export interface GenerationMeta {
  fileCount: number
  pageCount: number
  lastPrompt: string
}

export default function App() {
  const [files, setFiles] = useState<GeneratedFiles>({})
  const [meta, setMeta] = useState<GenerationMeta>({
    fileCount: 0,
    pageCount: 0,
    lastPrompt: ""
  })

  const handleGenerated = (nextFiles: GeneratedFiles, prompt: string) => {
    setFiles(nextFiles)
    setMeta({
      fileCount: Object.keys(nextFiles).length,
      pageCount: Object.keys(nextFiles).filter((name) => name !== "App.jsx").length,
      lastPrompt: prompt
    })
  }

  return (
    <main className="grid h-screen w-screen grid-cols-[360px_1fr] overflow-hidden bg-[#101114] text-[#f4f0e8] max-lg:grid-cols-1 max-lg:grid-rows-[420px_1fr]">
      <ChatPanel onGenerated={handleGenerated} meta={meta} />
      <PreviewPanel files={files} meta={meta} />
    </main>
  )
}
