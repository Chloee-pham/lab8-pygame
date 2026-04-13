const state = {
  entries: [],
  selectedPath: null,
  search: "",
};

const summaryCards = document.getElementById("summaryCards");
const searchInput = document.getElementById("searchInput");
const selectionLabel = document.getElementById("selectionLabel");
const fileTree = document.getElementById("fileTree");
const fileViewer = document.getElementById("fileViewer");
const fileTitle = document.getElementById("fileTitle");
const fileMeta = document.getElementById("fileMeta");

function escapeHtml(value) {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/\"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function formatSize(size) {
  if (size < 1024) {
    return `${size} B`;
  }
  if (size < 1024 * 1024) {
    return `${(size / 1024).toFixed(1)} KB`;
  }
  return `${(size / (1024 * 1024)).toFixed(1)} MB`;
}

function titleCase(value) {
  return value
    .split(/[-_\s]+/)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function languageLabel(language) {
  return (
    {
      python: "Python",
      markdown: "Markdown",
      javascript: "JavaScript",
      css: "CSS",
      html: "HTML",
      json: "JSON",
      yaml: "YAML",
      text: "Text",
    }[language] || titleCase(language)
  );
}

function createSummaryCard(value, label, detail) {
  const card = document.createElement("div");
  card.className = "summary-card";
  card.innerHTML = `<strong>${value}</strong><span>${label}${detail ? ` · ${detail}` : ""}</span>`;
  return card;
}

function renderSummary(summary) {
  summaryCards.replaceChildren();
  summaryCards.append(
    createSummaryCard(
      summary.fileCount,
      "files indexed",
      `${summary.pythonFileCount} Python`,
    ),
    createSummaryCard(
      summary.textFileCount,
      "text files",
      `${summary.rootName} root`,
    ),
    createSummaryCard(
      summary.topLevelFolders.length || 1,
      "top-level folders",
      "project structure",
    ),
    createSummaryCard("Live", "file preview", "served from the repo"),
  );
}

function filteredEntries() {
  const query = state.search.trim().toLowerCase();
  if (!query) {
    return state.entries;
  }
  return state.entries.filter((entry) => {
    const haystack =
      `${entry.path} ${entry.language} ${entry.name}`.toLowerCase();
    return haystack.includes(query);
  });
}

function buildTree(entries) {
  const root = { children: new Map(), files: [] };

  for (const entry of entries) {
    const parts = entry.path.split("/");
    let cursor = root;
    for (let index = 0; index < parts.length - 1; index += 1) {
      const folderName = parts[index];
      if (!cursor.children.has(folderName)) {
        cursor.children.set(folderName, { children: new Map(), files: [] });
      }
      cursor = cursor.children.get(folderName);
    }
    cursor.files.push(entry);
  }

  return root;
}

function renderNodeList(node, container, prefix = "") {
  const folderNames = [...node.children.keys()].sort((a, b) =>
    a.localeCompare(b),
  );
  for (const folderName of folderNames) {
    const folder = node.children.get(folderName);
    const folderWrap = document.createElement("div");
    folderWrap.className = "tree-folder";
    folderWrap.innerHTML = `
			<div class="tree-node folder-node">
				<span class="badge">DIR</span>
				<span class="path">${escapeHtml(prefix + folderName)}</span>
				<span class="size">${folder.files.length + [...folder.children.values()].reduce((total, child) => total + child.files.length, 0)} items</span>
			</div>
		`;
    const nested = document.createElement("div");
    nested.style.paddingLeft = "14px";
    nested.style.marginBottom = "8px";
    renderNodeList(folder, nested, `${prefix + folderName}/`);
    folderWrap.append(nested);
    container.append(folderWrap);
  }

  const files = [...node.files].sort((a, b) => a.name.localeCompare(b.name));
  for (const entry of files) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `tree-node file-node ${entry.path === state.selectedPath ? "active" : ""}`;
    button.dataset.path = entry.path;
    button.innerHTML = `
			<span class="badge">${escapeHtml(languageLabel(entry.language))}</span>
			<span class="path">${escapeHtml(entry.path)}</span>
			<span class="size">${formatSize(entry.size)}</span>
		`;
    button.addEventListener("click", () => selectFile(entry.path));
    container.append(button);
  }
}

function renderTree() {
  const filtered = filteredEntries();
  const grouped = buildTree(filtered);
  fileTree.replaceChildren();
  if (filtered.length === 0) {
    const empty = document.createElement("div");
    empty.className = "empty-state";
    empty.textContent = "No matching files.";
    fileTree.append(empty);
    return;
  }
  renderNodeList(grouped, fileTree);
}

function highlightPython(source) {
  const escaped = escapeHtml(source);
  return escaped
    .replace(/(#.*)$/gm, '<span class="token-comment">$1</span>')
    .replace(
      /("""[\s\S]*?"""|'''[\s\S]*?'''|"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')/g,
      '<span class="token-string">$1</span>',
    )
    .replace(
      /\b(def|class|return|import|from|as|if|elif|else|for|while|try|except|finally|with|in|is|and|or|not|lambda|pass|break|continue|yield|True|False|None)\b/g,
      '<span class="token-keyword">$1</span>',
    )
    .replace(/\b(\d+(?:\.\d+)?)\b/g, '<span class="token-number">$1</span>')
    .replace(
      /(\.|=|:|\(|\)|\[|\]|\{|\}|,)/g,
      '<span class="token-operator">$1</span>',
    );
}

function highlightMarkdown(source) {
  return escapeHtml(source)
    .replace(/^(#{1,6} .*)$/gm, '<span class="token-heading">$1</span>')
    .replace(/(\[[^\]]+\]\([^)]+\))/g, '<span class="token-link">$1</span>');
}

function highlightSource(source, language) {
  if (language === "python") {
    return highlightPython(source);
  }
  if (language === "markdown") {
    return highlightMarkdown(source);
  }
  return escapeHtml(source);
}

function renderCode(source, language) {
  const lines = source.split(/\r?\n/);
  return lines
    .map((line, index) => {
      const lineNumber = String(index + 1).padStart(
        lines.length > 99 ? 3 : 2,
        " ",
      );
      return `
				<div class="line-row">
					<div class="line-no">${lineNumber}</div>
					<div class="line-code">${highlightSource(line || " ", language)}</div>
				</div>
			`;
    })
    .join("");
}

async function selectFile(path) {
  state.selectedPath = path;
  renderTree();
  selectionLabel.textContent = path;

  const response = await fetch(`/api/file?path=${encodeURIComponent(path)}`);
  if (!response.ok) {
    fileViewer.className = "viewer empty-state";
    fileViewer.textContent = `Unable to load ${path}`;
    fileTitle.textContent = titleCase(path.split("/").pop() || path);
    fileMeta.textContent = "Unavailable";
    return;
  }

  const payload = await response.json();
  fileTitle.textContent = payload.name;
  fileMeta.innerHTML = `
		<span class="badge">${escapeHtml(languageLabel(payload.language))}</span>
		<span class="badge">${escapeHtml(formatSize(payload.content.length))}</span>
	`;
  fileViewer.className = "viewer";
  fileViewer.innerHTML = `
		<div class="code-header">
			<div class="code-title">
				<strong>${escapeHtml(payload.name)}</strong>
				<span>${escapeHtml(payload.path)}</span>
			</div>
			<div class="badge">${escapeHtml(languageLabel(payload.language))}</div>
		</div>
		<pre class="code-body">${renderCode(payload.content, payload.language)}</pre>
	`;
  localStorage.setItem("lab8-explorer-path", path);
}

async function init() {
  const response = await fetch("/api/tree");
  const payload = await response.json();
  state.entries = payload.entries;
  renderSummary(payload.summary);
  renderTree();

  const storedPath = localStorage.getItem("lab8-explorer-path");
  const defaultFile =
    storedPath && state.entries.some((entry) => entry.path === storedPath)
      ? storedPath
      : state.entries.find((entry) => entry.path === "README.md")?.path ||
        state.entries[0]?.path;

  if (defaultFile) {
    await selectFile(defaultFile);
  }

  searchInput.addEventListener("input", (event) => {
    state.search = event.target.value;
    renderTree();
  });
}

init().catch((error) => {
  fileViewer.className = "viewer empty-state";
  fileViewer.textContent = `Explorer failed to load: ${error.message}`;
});
