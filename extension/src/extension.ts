import * as vscode from "vscode";
import { execFile } from "child_process";
import * as path from "path";

let selectedFilePath: string | null = null;

export function activate(context: vscode.ExtensionContext) {

  // Command: Select File (manual)
  const selectFile = vscode.commands.registerCommand(
    "ai-code-helper.selectFile",
    async () => {
      const result = await vscode.window.showOpenDialog({
        canSelectMany: false,
        filters: { Python: ["py"] }
      });

      if (!result || result.length === 0) {
        vscode.window.showWarningMessage("No file selected");
        return;
      }

      selectedFilePath = result[0].fsPath;
      vscode.window.showInformationMessage(
        `Selected file: ${path.basename(selectedFilePath)}`
      );
    }
  );

  // Command: Open Chat
  const chat = vscode.commands.registerCommand(
    "ai-code-helper.chat",
    () => {

      //  AUTO-DETECT ACTIVE FILE
      const activeEditor = vscode.window.activeTextEditor;
      if (activeEditor?.document?.fileName.endsWith(".py")) {
        selectedFilePath = activeEditor.document.fileName;
      }

      const panel = vscode.window.createWebviewPanel(
        "aiCodeHelper",
        "AI Code Helper",
        vscode.ViewColumn.One,
        { enableScripts: true, retainContextWhenHidden: true }
      );

      panel.webview.html = getChatHtml();

      panel.webview.onDidReceiveMessage(async (msg) => {
        if (msg.type !== "ask") return;

        if (!selectedFilePath) {
          panel.webview.postMessage({
            type: "answer",
            text: " Please open or select a Python file first."
          });
          return;
        }

        const pythonExe = path.join(
          "D:",
          "ananta",
          "AI_engineer_Intership",
          "AI_CODE_HELPER_PROJECT",
          "rag",
          "helper",
          "Scripts",
          "python.exe"
        );

        const ragScript = path.join(
          "D:",
          "ananta",
          "AI_engineer_Intership",
          "AI_CODE_HELPER_PROJECT",
          "rag",
          "rag_query.py"
        );

        execFile(
          pythonExe,
          [ragScript, selectedFilePath, msg.text],
          { windowsHide: true },
          (err, stdout, stderr) => {
            panel.webview.postMessage({
              type: "answer",
              text: err ? stderr : stdout
            });
          }
        );
      });
    }
  );

  context.subscriptions.push(selectFile, chat);
}

export function deactivate() {}


// UI HTML
function getChatHtml(): string {
  return `
<!DOCTYPE html>
<html>
<head>
<style>
body { background:#1e1e1e; color:#ddd; font-family:Segoe UI; margin:0; }
#chat { padding:12px; height:85vh; overflow-y:auto; }
.user { color:#4fc3f7; margin-bottom:8px; }
.ai { color:#9ccc65; white-space:pre-wrap; margin-bottom:12px; }
footer { display:flex; padding:10px; gap:8px; }
input { flex:1; padding:8px; background:#252526; color:white; border:1px solid #444; }
button { padding:8px 14px; background:#0e639c; color:white; border:none; }
</style>
</head>
<body>

<div id="chat"></div>

<footer>
  <input id="q" placeholder="Ask about the selected file..." />
  <button onclick="send()">Send</button>
</footer>

<script>
const vscode = acquireVsCodeApi();
const chat = document.getElementById("chat");

function send() {
  const input = document.getElementById("q");
  if (!input.value.trim()) return;

  chat.innerHTML += "<div class='user'>You: " + input.value + "</div>";
  vscode.postMessage({ type:"ask", text: input.value });
  input.value = "";
  chat.scrollTop = chat.scrollHeight;
}

window.addEventListener("message", e => {
  chat.innerHTML += "<div class='ai'>AI: " + e.data.text + "</div>";
  chat.scrollTop = chat.scrollHeight;
});
</script>

</body>
</html>
`;
}
