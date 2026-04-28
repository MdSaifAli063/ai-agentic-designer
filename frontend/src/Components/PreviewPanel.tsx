import { useEffect, useMemo, useState } from "react"
import type { GeneratedFiles, GenerationMeta } from "../App"

interface Props {
  files: GeneratedFiles
  meta: GenerationMeta
}

type ViewMode = "preview" | "code"

function toComponentName(fileName: string): string {
  return fileName.split("/").pop()?.replace(/\.jsx$/, "") || "Page"
}

function removeImports(code: string): string {
  return code
    .replace(/import\s+\{[^}]*\}\s+from\s+["']react["'];?\s*/g, "")
    .replace(/import\s+React\s+from\s+["']react["'];?\s*/g, "")
    .replace(/import\s+\w+\s+from\s+["']\.\/pages\/[^"']+["'];?\s*/g, "")
    .replace(/import\s+[^;]+;?\s*/g, "")
}

function transformComponentCode(code: string): string {
  return removeImports(code)
    .replace(/export\s+default\s+function\s+(\w+)/g, "function $1")
    .replace(/export\s+default\s+(\w+);?/g, "")
}

function transformAppCode(appCode: string, pageFiles: string[]): string {
  const routeEntries = pageFiles
    .map((fileName) => {
      const componentName = toComponentName(fileName)
      const route =
        componentName === "Home"
          ? "/"
          : `/${componentName.replace(/([a-z0-9])([A-Z])/g, "$1-$2").toLowerCase()}`
      return `"${route}": ${componentName}`
    })
    .join(",\n  ")

  const navigationEntries = pageFiles
    .map((fileName) => {
      const componentName = toComponentName(fileName)
      const route =
        componentName === "Home"
          ? "/"
          : `/${componentName.replace(/([a-z0-9])([A-Z])/g, "$1-$2").toLowerCase()}`
      return `{ route: "${route}", label: "${componentName.replace(/([a-z])([A-Z])/g, "$1 $2")}" }`
    })
    .join(", ")

  const cleaned = removeImports(appCode)
    .replace(/const\s+routes\s*=\s*\{[\s\S]*?\};/, `const routes = {\n  ${routeEntries}\n};`)
    .replace(/const\s+navigation\s*=\s*\[[\s\S]*?\];/, `const navigation = [${navigationEntries}];`)
    .replace(/export\s+default\s+function\s+App/g, "function App")
    .replace(/export\s+default\s+App;?/g, "")

  return cleaned
}

function buildPreviewHtml(files: GeneratedFiles): string {
  const appCode =
    files["src/App.jsx"] ||
    files["App.jsx"] ||
    "function App(){ return <div>No App.jsx generated</div> }"
  const pageFiles = Object.keys(files).filter((name) => name.startsWith("src/pages/") && name.endsWith(".jsx"))
  const pageCode = pageFiles.map((name) => transformComponentCode(files[name])).join("\n\n")
  const runtimeAppCode = transformAppCode(appCode, pageFiles)

  const script = `
const { useEffect, useState, useMemo, useRef } = React;

${pageCode}

${runtimeAppCode}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);
`

  return `
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <script src="https://cdn.tailwindcss.com"></script>
    <script crossorigin src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <style>
      html, body, #root {
        min-height: 100%;
        margin: 0;
      }

      body {
        background: #000814;
      }

      * {
        box-sizing: border-box;
      }

      .preview-error {
        min-height: 100vh;
        background: #140707;
        color: #ffe8e8;
        padding: 24px;
        font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
        white-space: pre-wrap;
      }
    </style>
  </head>
  <body>
    <div id="root"></div>
    <script>
      document.addEventListener("click", function(event) {
        const target = event.target;
        if (!(target instanceof Element)) return;
        const link = target.closest("a");
        if (!link) return;

        const href = link.getAttribute("href") || "";
        if (!href) return;

        if (href.startsWith("#/")) {
          event.preventDefault();
          window.location.hash = href.slice(1);
          return;
        }

        if (href === "/" || href.startsWith("/")) {
          event.preventDefault();
          window.location.hash = href;
        }
      });

      window.addEventListener("error", function(event) {
        document.getElementById("root").innerHTML =
          '<pre class="preview-error">' + ${JSON.stringify("Preview runtime error:\\n")} + event.message + "\\n" + event.filename + ":" + event.lineno + ":" + event.colno + "</pre>";
      });
    </script>
    <script type="text/babel" data-presets="env,react">
${script}
    </script>
  </body>
</html>
`.trim()
}

export default function PreviewPanel({ files, meta }: Props) {
  const [view, setView] = useState<ViewMode>("preview")
  const fileNames = useMemo(() => Object.keys(files), [files])
  const [selectedFile, setSelectedFile] = useState("App.jsx")
  const hasFiles = fileNames.length > 0
  const previewHtml = useMemo(() => buildPreviewHtml(files), [files])

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
          <iframe
            key={fileNames.join("|")}
            title="Generated website preview"
            srcDoc={previewHtml}
            sandbox="allow-scripts allow-same-origin"
            className="h-full w-full border-0 bg-white"
          />
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
