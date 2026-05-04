from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse


ROOT = Path(__file__).resolve().parent
QUIZ_DATA_FILE = ROOT / "questions.json"


def load_quiz_data() -> dict[str, object]:
    """Load quiz questions from JSON file."""
    if not QUIZ_DATA_FILE.exists():
        return {"quizzes": []}
    try:
        with open(QUIZ_DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"quizzes": []}


class QuizHandler(BaseHTTPRequestHandler):
    """HTTP request handler for quiz API and static assets."""

    def _send_json(
        self, payload: dict[str, object], status: HTTPStatus = HTTPStatus.OK
    ) -> None:
        """Send JSON response."""
        encoded = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _send_file(self, file_path: Path, content_type: str = "text/html") -> None:
        """Send file content with appropriate MIME type."""
        try:
            content = file_path.read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header(
                "Content-Type",
                f"{content_type}; charset=utf-8"
                if content_type.startswith("text/")
                else content_type,
            )
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except (FileNotFoundError, IOError):
            self.send_error(HTTPStatus.NOT_FOUND)

    def do_GET(self) -> None:  # noqa: N802
        """Handle GET requests."""
        parsed = urlparse(self.path)

        # API: Get all available quizzes
        if parsed.path == "/api/quizzes":
            quiz_data = load_quiz_data()
            self._send_json(quiz_data)
            return

        # API: Get specific quiz
        if parsed.path == "/api/quiz":
            query = parse_qs(parsed.query)
            quiz_id = query.get("id", [None])[0]
            if not quiz_id:
                self._send_json({"error": "Missing quiz id"}, HTTPStatus.BAD_REQUEST)
                return

            quiz_data = load_quiz_data()
            for quiz in quiz_data.get("quizzes", []):
                if quiz.get("id") == quiz_id:
                    self._send_json(quiz)
                    return

            self._send_json(
                {"error": "Quiz not found"}, HTTPStatus.NOT_FOUND
            )
            return

        # API: Submit quiz answers and get results
        if parsed.path == "/api/submit":
            query = parse_qs(parsed.query)
            quiz_id = query.get("id", [None])[0]
            if not quiz_id:
                self._send_json({"error": "Missing quiz id"}, HTTPStatus.BAD_REQUEST)
                return

            quiz_data = load_quiz_data()
            for quiz in quiz_data.get("quizzes", []):
                if quiz.get("id") == quiz_id:
                    self._send_json({"quizId": quiz_id, "status": "submitted"})
                    return

            self._send_json(
                {"error": "Quiz not found"}, HTTPStatus.NOT_FOUND
            )
            return

        # Static assets
        if parsed.path in {"/", "", "/index.html"}:
            self._send_file(ROOT / "index.html", "text/html")
            return

        if parsed.path == "/app.js":
            self._send_file(ROOT / "app.js", "text/javascript")
            return

        if parsed.path == "/styles.css":
            self._send_file(ROOT / "styles.css", "text/css")
            return

        self.send_error(HTTPStatus.NOT_FOUND)

    def log_message(self, format: str, *args: object) -> None:
        """Suppress log messages."""
        return


def main() -> None:
    """Start the quiz server."""
    server = ThreadingHTTPServer(("127.0.0.1", 8001), QuizHandler)
    print("Flash Quiz site running at http://127.0.0.1:8001")
    print(f"Serving from: {ROOT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
