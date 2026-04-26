import { useState } from "react"
import { Sandpack } from "@codesandbox/sandpack-react"

interface Props {
  files: Record<string, string>
}

export default function PreviewPanel({ files }: Props) {
  const [activeTab, setActiveTab] = useState("preview")

  // Convert your files dict to Sandpack format
  const sandpackFiles = Object.entries(files).reduce((acc, [name, code]) => {
    acc[`/src/pages/${name}`] = { code }
    return acc
  }, {} as Record<string, { code: string }>)

  return (
    <div className="flex flex-col h-screen flex-1">

      {/* Tabs */}
      <div className="flex border-b border-white/10">
        <button
          onClick={() => setActiveTab("preview")}
          className={`px-6 py-3 text-sm font-medium ${
            activeTab === "preview"
              ? "text-white border-b-2 border-violet-500"
              : "text-white/40"
          }`}
        >
          Preview
        </button>
        <button
          onClick={() => setActiveTab("code")}
          className={`px-6 py-3 text-sm font-medium ${
            activeTab === "code"
              ? "text-white border-b-2 border-violet-500"
              : "text-white/40"
          }`}
        >
          Code
        </button>
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-hidden">

        {/* Empty state */}
        {Object.keys(files).length === 0 && (
          <div className="flex items-center justify-center h-full text-white/30 text-sm">
            Your generated UI will appear here
          </div>
        )}

        {/* Preview Tab */}
        {activeTab === "preview" && Object.keys(files).length > 0 && (
          <Sandpack
            template="react"
            files={{
              ...sandpackFiles,
              "/src/App.jsx": { code: files["App.jsx"] || "" }
            }}
            options={{
              showNavigator: false,
              showTabs: false,
              editorHeight: "100%",
              visibleFiles: ["/src/App.jsx"]
            }}
            theme="dark"
          />
        )}

        {/* Code Tab */}
        {activeTab === "code" && Object.keys(files).length > 0 && (
          <div className="text-white p-4">
            Code editor coming next
          </div>
        )}

      </div>
    </div>
  )
}