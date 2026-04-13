from __future__ import annotations

import json
import mimetypes
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parent.parent
ASSET_DIR = Path(__file__).resolve().parent
TEXT_EXTENSIONS = {
	".py",
	".md",
	".txt",
	".json",
	".js",
	".css",
	".html",
	".toml",
	".yaml",
	".yml",
	".ini",
	".cfg",
	".sh",
	".xml",
	".csv",
}


def language_for(path: Path) -> str:
	extension = path.suffix.lower()
	return {
		".py": "python",
		".md": "markdown",
		".js": "javascript",
		".css": "css",
		".html": "html",
		".json": "json",
		".yaml": "yaml",
		".yml": "yaml",
	}.get(extension, "text")


def is_text_file(path: Path) -> bool:
	return path.suffix.lower() in TEXT_EXTENSIONS or path.name in {"README", "LICENSE"}


def resolve_repo_path(relative_path: str) -> Path:
	relative_path = relative_path.lstrip("/")
	target = (ROOT / relative_path).resolve()
	if target != ROOT and ROOT not in target.parents:
		raise FileNotFoundError(relative_path)
	return target


def iter_repository_entries() -> list[dict[str, object]]:
	entries: list[dict[str, object]] = []
	ignored_names = {".git", ".venv", "__pycache__", ".DS_Store"}
	for path in sorted(ROOT.rglob("*")):
		if any(part in ignored_names for part in path.parts):
			continue
		if path.is_dir():
			continue
		relative_path = path.relative_to(ROOT).as_posix()
		try:
			size = path.stat().st_size
		except OSError:
			size = 0
		entries.append(
			{
				"path": relative_path,
				"name": path.name,
				"language": language_for(path),
				"size": size,
				"folder": path.parent.relative_to(ROOT).as_posix() if path.parent != ROOT else "",
			}
		)
	return entries


def repository_summary() -> dict[str, object]:
	entries = iter_repository_entries()
	text_files = [entry for entry in entries if is_text_file(ROOT / str(entry["path"]))]
	python_files = [entry for entry in entries if str(entry["language"]) == "python"]
	return {
		"rootName": ROOT.name,
		"fileCount": len(entries),
		"textFileCount": len(text_files),
		"pythonFileCount": len(python_files),
		"topLevelFolders": sorted({str(entry["path"]).split("/", 1)[0] for entry in entries if "/" in str(entry["path"])}),
	}


class ExplorerHandler(BaseHTTPRequestHandler):
	def _send_json(self, payload: dict[str, object], status: HTTPStatus = HTTPStatus.OK) -> None:
		encoded = json.dumps(payload, indent=2).encode("utf-8")
		self.send_response(status)
		self.send_header("Content-Type", "application/json; charset=utf-8")
		self.send_header("Content-Length", str(len(encoded)))
		self.end_headers()
		self.wfile.write(encoded)

	def _send_text(self, path: Path) -> None:
		content = path.read_bytes()
		content_type, _ = mimetypes.guess_type(path.name)
		if content_type is None:
			content_type = "application/octet-stream"
		self.send_response(HTTPStatus.OK)
		self.send_header("Content-Type", f"{content_type}; charset=utf-8" if content_type.startswith("text/") else content_type)
		self.send_header("Content-Length", str(len(content)))
		self.end_headers()
		self.wfile.write(content)

	def do_GET(self) -> None:  # noqa: N802
		parsed = urlparse(self.path)
		if parsed.path == "/api/tree":
			self._send_json({"root": ROOT.name, "entries": iter_repository_entries(), "summary": repository_summary()})
			return

		if parsed.path == "/api/file":
			query = parse_qs(parsed.query)
			relative_path = query.get("path", [""])[0]
			if not relative_path:
				self._send_json({"error": "Missing path"}, HTTPStatus.BAD_REQUEST)
				return
			try:
				target = resolve_repo_path(relative_path)
			except FileNotFoundError:
				self._send_json({"error": "Invalid path"}, HTTPStatus.NOT_FOUND)
				return
			if not target.is_file():
				self._send_json({"error": "Not a file"}, HTTPStatus.NOT_FOUND)
				return
			if not is_text_file(target):
				self._send_json({"error": "Binary files are not supported"}, HTTPStatus.UNSUPPORTED_MEDIA_TYPE)
				return
			try:
				content = target.read_text(encoding="utf-8")
			except UnicodeDecodeError:
				content = target.read_text(encoding="utf-8", errors="replace")
			self._send_json(
				{
					"path": relative_path,
					"name": target.name,
					"language": language_for(target),
					"content": content,
				},
			)
			return

		asset_path = ASSET_DIR / ("index.html" if parsed.path in {"/", ""} else parsed.path.lstrip("/"))
		if asset_path.is_file() and asset_path.resolve().is_relative_to(ASSET_DIR):
			self._send_text(asset_path)
			return

		self.send_error(HTTPStatus.NOT_FOUND)

	def log_message(self, format: str, *args: object) -> None:
		return


def main() -> None:
	server = ThreadingHTTPServer(("127.0.0.1", 8000), ExplorerHandler)
	print("Code explorer running at http://127.0.0.1:8000")
	print(f"Serving project root: {ROOT}")
	try:
		server.serve_forever()
	except KeyboardInterrupt:
		pass
	finally:
		server.server_close()


if __name__ == "__main__":
	main()