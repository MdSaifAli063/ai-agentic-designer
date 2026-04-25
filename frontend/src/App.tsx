import ChatPanel from "./Components/ChatPanel"
import PriviewPanel from "./Components/PreviewPanel"


export default function App() {
  return (
    <div className="flex h-screen bg-[#0f0f1a]">
        <PriviewPanel />
        <ChatPanel />
    </div>
  )
}