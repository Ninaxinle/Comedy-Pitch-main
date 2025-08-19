Here’s a polished, step-by-step guide to setting up Figma’s Dev Mode MCP server and using it with Cursor to generate code from your designs:

---

## 1️⃣ Subscribe to Figma Dev Seat

Ensure you're on a plan with **Dev mode** (about \$15/month per seat). Free-tier users cannot access Dev Mode or MCP server features. ([Figma Help Center][1], [The Verge][2])

---

## 2️⃣ Install & Enable Figma Desktop Dev Mode MCP

* Download/update the **Figma Desktop app** (browser version doesn’t work).
* Open your file, go to **Preferences → Enable Dev Mode MCP Server**.
* Also toggle **Dev Mode** at the bottom of the design pane.
* The local MCP server will start on `http://127.0.0.1:3845/sse`.
  ([Medium][3], [Figma Help Center][1])

---

## 3️⃣ Set Up MCP Integration in Cursor

* In **Cursor**, go to **Settings → Cursor Settings → MCP (or MCP Tools)**.
* Click **+ Add new MCP Server**.
* Paste this JSON config:

  ```json
  {
    "mcpServers": {
      "Figma": {
        "url": "http://127.0.0.1:3845/sse"
      }
    }
  }
  ```
* Save and look for a **green dot / "4 tools enabled"** indicator. You can also find an “Add Figma to Cursor” button in Cursor’s MCP directory.
  ([Figma Help Center][1], [UX Planet][4], [Builder.io][5])

---

## 4️⃣ Select Your Frame in Figma

* In the Desktop app, click to select a **Frame** (not a group or nested layer).
* With the frame selected and Dev Mode still on, it's now ready for Cursor commands.
  ([Medium][3])
  
> **Note:** If you're using a weaker model (such as the default "auto" mode in Cursor), it may not realize it can fetch the code for the currently selected frame in Figma. In such cases, you can right-click the frame in Figma and copy its link, then provide that link to Cursor. However, for the smoothest experience, it's best to use a stronger model like **Claude Sonnet 4** or **Gemini 2.5 Pro**—these models can directly access and generate code for the selected frame without needing a manual link.

---

## 5️⃣ Ask Cursor to Generate Code

* Switch Cursor to **Agent mode**.
* Use a prompt like:

  ```
  Generate a React component from the selected Figma frame, using TypeScript and Tailwind CSS.
  ```
* Cursor will internally use Figma’s MCP `get_code` tool, pulling design metadata—variables, layout, colors—resulting in much cleaner code than image-based approaches.
  ([Reddit][6], [Medium][3], [Figma Help Center][1])

---

## 6️⃣ Troubleshooting Tips
> **Important:** Figma-generated React components often use `size-full` (i.e., `w-full h-full`) classes, which require their parent container to have explicit width and height set.  
> **If you do not wrap the generated component in a container with the exact dimensions of your Figma frame** (e.g., `<div className="w-[393px] h-[852px]"><YourComponent /></div>`), the component will render as a blank area.  
> Always check your Figma frame's size and wrap the generated component accordingly to ensure it displays correctly.

* Preferable models: **Claude Sonnet**, **Gemini 2.5 Pro** work better than “auto” mode.

* In my test, it may not put the full code from Figma in, perhaps due to context window limit. If the code appears cut off:

  * **Manually paste** the full code into the file. In cursor you can find the result of the `get_code` tool call and you can copy it. 
  * Prompt Cursor to refine, debug, or connect plumbing based on that file.

---

## ✅ Your Completed Workflow

| Step | Action                                |
| ---- | ------------------------------------- |
| 💰   | Subscribe to Dev seat                 |
| 📥   | Install Figma Desktop                 |
| 🔧   | Enable Dev Mode + MCP Server          |
| ⚙️   | Configure Cursor with MCP URL         |
| 📐   | Select frame in Figma                 |
| 🤖   | Prompt Cursor to generate/refine code |
| ✂️   | Optional manual paste + refinement    |

---

### 📎 Helpful References (I have NOT weatched these. May be helfpul)

* **UX Planet** walkthrough of Figma MCP → Cursor integration ([apidog][7], [The Verge][2], [UX Planet][4], [Medium][3])
* Figma’s official **Dev Mode MCP Server guide** ([Figma Help Center][1])
* Builder.io deep dive on **design-to-code** with Cursor ([Builder.io][5])

---

### TL;DR

1. Get Figma Dev seat → enable MCP and Dev Mode
2. Connect Cursor with MCP URL
3. Select your frame → prompt Cursor in Agent mode
4. Let code generate; if truncated, paste manually and refine

[1]: https://help.figma.com/hc/en-us/articles/32132100833559-Guide-to-the-Dev-Mode-MCP-Server?utm_source=chatgpt.com "Guide to the Dev Mode MCP Server – Figma Learn - Help Center"
[2]: https://www.theverge.com/news/679439/figma-dev-mode-mcp-server-beta-release?utm_source=chatgpt.com "Figma will let your AI access its design servers"
[3]: https://medium.com/%40ano/how-to-connect-figmas-mcp-server-to-cursor-and-preview-your-ui-code-instantly-fcf01802d422?utm_source=chatgpt.com "Figma's MCP Server Just Changed Dev Handoff - Medium"
[4]: https://uxplanet.org/new-figma-mcp-cursor-integration-with-example-46e0641400d6?utm_source=chatgpt.com "New Figma MCP + Cursor Integration with Example - UX Planet"
[5]: https://www.builder.io/blog/figma-mcp-server?utm_source=chatgpt.com "Design to Code with the Figma MCP Server - Builder.io"
[6]: https://www.reddit.com/r/CursorAI/comments/1j7r4am/cursor_ai_x_figma_mcp/?utm_source=chatgpt.com "Cursor AI x Figma MCP : r/CursorAI - Reddit"
[7]: https://apidog.com/blog/figma-mcp/?utm_source=chatgpt.com "Figma Now Has a MCP Server and Here's How to Use It - Apidog"
