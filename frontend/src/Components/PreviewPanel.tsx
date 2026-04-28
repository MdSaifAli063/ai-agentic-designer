import { useEffect, useMemo, useState } from "react"
import { Sandpack } from "@codesandbox/sandpack-react"
import type { GeneratedFiles, GenerationMeta } from "../App"

interface Props {
  files: GeneratedFiles
  meta: GenerationMeta
}

type ViewMode = "preview" | "code"

function toSandpackPath(name: string): string {
  if (name === "App.jsx") return "/src/App.js"
  if (name.startsWith("/")) return name
  return `/src/pages/${name}`
}

function buildSandpackFiles(files: GeneratedFiles): Record<string, { code: string }> {
  const mappedFiles = Object.entries(files).reduce((acc, [name, code]) => {
    acc[toSandpackPath(name)] = { code }
    return acc
  }, {} as Record<string, { code: string }>)

  return {
    "/public/index.html": {
      code: `
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <script src="https://cdn.tailwindcss.com"></script>
    <title>Generated Site</title>
  </head>
  <body>
    <div id="root"></div>
  </body>
</html>
`.trim()
    },
    "/src/index.js": {
      code: `
import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import "./styles.css";

createRoot(document.getElementById("root")).render(<App />);
`.trim()
    },
    "/src/styles.css": {
      code: `
html,
body,
#root {
  min-height: 100%;
  margin: 0;
}

body {
  background: #000814;
}

* {
  box-sizing: border-box;
}
`.trim()
    },
    ...mappedFiles
  }
}

export default function PreviewPanel({ files, meta }: Props) {
  const [view, setView] = useState<ViewMode>("preview")
  const fileNames = useMemo(() => Object.keys(files), [files])
  const [selectedFile, setSelectedFile] = useState("App.jsx")
  const hasFiles = fileNames.length > 0
  const sandpackFiles = useMemo(() => buildSandpackFiles(files), [files])

  useEffect(() => {
    if (!files[selectedFile]) {
      setSelectedFile(fileNames.includes("App.jsx") ? "App.jsx" : fileNames[0] || "App.jsx")
    }
  }, [fileNames, files, selectedFile])

  return (
    <section className="min-h-0 min-w-0 bg-[#0d0e11]">
      <header className="flex h-16 items-center justify-between border-b border-[#2a2c31] px-5">
        <div className="min-w-0">
          <div className="truncate text-sm text-[#8f969f]">{meta.lastPrompt || "No generation yet"}</div>
          <div className="mt-1 text-sm font-medium text-[#f8f4ea]">
            {hasFiles ? `${meta.fileCount} files ready` : "Preview waiting for generated files"}
          </div>
        </div>

        <div className="flex rounded-md border border-[#2a2c31] bg-[#16171b] p-1">
          <button
            type="button"
            onClick={() => setView("preview")}
            className={`rounded px-4 py-2 text-sm transition ${
              view === "preview" ? "bg-[#d3ff72] text-[#12140f]" : "text-[#c2c7ce]"
            }`}
          >
            Preview
          </button>
          <button
            type="button"
            onClick={() => setView("code")}
            className={`rounded px-4 py-2 text-sm transition ${
              view === "code" ? "bg-[#d3ff72] text-[#12140f]" : "text-[#c2c7ce]"
            }`}
          >
            Code
          </button>
        </div>
      </header>

      <div className="h-[calc(100vh-4rem)] min-h-0 max-lg:h-[calc(100vh-420px-4rem)]">
        {!hasFiles && (
          <div className="grid h-full place-items-center px-6 text-center text-sm text-[#8f969f]">
            Generated website output will render here after the backend returns files.
          </div>
        )}

        {hasFiles && view === "preview" && (
          <div className="h-full bg-white">
            <Sandpack
              key={fileNames.join("|")}
              template="react"
              files={sandpackFiles}
              options={{
                showNavigator: true,
                showTabs: false,
                showLineNumbers: true,
                showInlineErrors: true,
                wrapContent: true,
                editorHeight: "100%",
                visibleFiles: ["/src/App.js"] as any,
                activeFile: "/src/App.js" as any
              }}
              theme="dark"
            />
          </div>
        )}

        {hasFiles && view === "code" && (
          <div className="grid h-full grid-cols-[260px_1fr] min-[0px]:min-h-0 max-md:grid-cols-1 max-md:grid-rows-[180px_1fr]">
            <aside className="min-h-0 overflow-y-auto border-r border-[#2a2c31] bg-[#15161a] max-md:border-b max-md:border-r-0">
              {fileNames.map((name) => (
                <button
                  type="button"
                  key={name}
                  onClick={() => setSelectedFile(name)}
                  className={`block w-full border-b border-[#24272d] px-4 py-3 text-left text-sm transition ${
                    selectedFile === name
                      ? "bg-[#d3ff72] text-[#12140f]"
                      : "text-[#d8dce0] hover:bg-[#20232a]"
                  }`}
                >
                  {name}
                </button>
              ))}
            </aside>

            <div className="min-h-0 overflow-auto bg-[#090a0d]">
              <div className="sticky top-0 border-b border-[#2a2c31] bg-[#111217] px-4 py-3 text-sm text-[#f8f4ea]">
                {selectedFile}
              </div>
              <pre className="min-h-full overflow-auto p-5 text-sm leading-6 text-[#d8dce0]">
                <code>{files[selectedFile] || ""}</code>
              </pre>
            </div>
          </div>
        )}
      </div>
    </section>
  )
}
