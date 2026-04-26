import ChatPanel from "./Components/ChatPanel"
import PriviewPanel from "./Components/PreviewPanel"
import { useState } from "react"




export default function App() {
  const [files, setFiles] = useState({})

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#0f0f1a]">
        
        <ChatPanel setFiles={setFiles}/>
        <PriviewPanel files={files} />
    </div>
  )
}