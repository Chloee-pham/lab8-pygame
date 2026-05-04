# Architecture Document

## 1. Purpose

This document describes the architecture of the Lab 8 project located in this folder.

The project consists of two independent runtimes:

- **Pygame Simulation**: a desktop simulation with moving, interacting squares
- **Code Explorer**: a local web-based utility for browsing and viewing project files

The goal is clarity and maintainability for an educational codebase. Both runtimes are self-contained and can be executed independently.

## 2. System Overview

### 2.1 Pygame Simulation

- **Entry point**: `main.py`
- **Responsibility**: real-time square simulation with physics, collision detection, and rendering
- **Runtime**: local process, single-threaded Pygame event loop
- **Target rate**: 60 FPS
- **Dependencies**: `pygame==2.6.1`

### 2.2 Code Explorer Utility

- **Backend**: `code-explorer/serve.py` — HTTP server providing repository API
- **Frontend**:
  - `code-explorer/index.html` — document structure
  - `code-explorer/app.js` — client-side interaction and rendering
  - `code-explorer/styles.css` — visual styling
- **Responsibility**: browse, search, and view project files through local web UI
- **Runtime**: ThreadingHTTPServer on `127.0.0.1:8000` + browser client
- **Dependencies**: Python standard library (no external packages)

The two runtimes do not share live state and operate completely independently.

## 3. High-Level System Architecture

```text
┌──────────────────────────────────────────────────────────────────┐
│                       Repository Root                             │
│                   (lab8-pygame directory)                         │
└────────────────────────┬──────────────────┬──────────────────────┘
                         │                  │
          ┌──────────────┴────────┐   ┌─────┴──────────────┐
          │  PYGAME RUNTIME       │   │  CODE EXPLORER     │
          │  (main.py)            │   │  (code-explorer/)  │
          └──────────────┬────────┘   └─────┬──────────────┘
                         │                  │
         ┌───────────────┴───┐      ┌───────┴─────────────┐
         │                   │      │                     │
         v                   v      v                     v
    ┌────────────┐  ┌─────────────┐  ┌──────────┐  ┌─────────────┐
    │ Pygame     │  │ Simulation  │  │  HTTP    │  │   Browser   │
    │ Window     │  │ State Loop  │  │  Server  │  │     UI      │
    │ 800×600    │  │ 60 FPS      │  │  Port    │  │  Search &   │
    │            │  │             │  │  8000    │  │  Preview    │
    └────────────┘  └─────────────┘  └──────────┘  └─────────────┘
                         │
      ┌──────────────────┼──────────────────┐
      │                  │                  │
      v                  v                  v
  ┌────────┐        ┌──────────┐      ┌──────────┐
  │ Update │        │  Render  │      │  Input   │
  │ Physics│        │  Scene   │      │  Events  │
  └────────┘        └──────────┘      └──────────┘
```

### Data Flow: Pygame Simulation

```text
create_initial_squares(count)
         ↓
[MovingSquare, MovingSquare, ...]
         ↓
    ┌────────────────────────────┐
    │   Main Loop (run)          │
    │   - tick clock             │
    │   - poll events            │
    │   - update_squares(dt)     │
    │   - draw_scene()           │
    └────────────────────────────┘
         ↓ (per frame)
    ┌────────────────────────────┐
    │   update_squares()         │
    │   ├─ age & rebirth check   │
    │   ├─ jitter + chase logic  │
    │   ├─ velocity integration  │
    │   └─ wall bounce           │
    └────────────────────────────┘
         ↓
    ┌────────────────────────────┐
    │   draw_scene()             │
    │   ├─ fill background       │
    │   ├─ draw alpha surfaces   │
    │   ├─ fade by lifespan age  │
    │   └─ flip display buffer   │
    └────────────────────────────┘
```

### Data Flow: Code Explorer

````text
HTTP Request (GET /api/tree or /api/file)
         ↓
    ┌────────────────────────────┐
    │  ExplorerHandler.do_GET()  │
    └────────────────────────────┘
         ↓
    ┌────────────────────────────┐
    │  Route Dispatch            │
    │  /api/tree? /api/file?     │
    │  /? (static assets)        │
    └────────────────────────────┘
         ↓
    ┌────────────────────────────┐
    │  Data Generation/Fetch     │
    │  - list repo files         │
    │  - resolve & read file     │
    │  - return JSON or binary   │
    └────────────────────────────┘
         ↓
    HTTP Response (JSON or asset)

## 4. Pygame Simulation Architecture

### 4.1 Domain Model

`MovingSquare` is a mutable dataclass and the main entity in the simulation.

- spatial state: `x`, `y`
- kinematics: `vx`, `vy`
- visual attributes: `size`, `color`
- lifecycle: `lifespan`, `age`

All simulation behavior transforms a list of `MovingSquare` objects in place.

### 4.2 Configuration Layer

Top-level constants in `main.py` define behavior and rendering tuning:

- display and timing: `WINDOW_WIDTH`, `WINDOW_HEIGHT`, `FPS`
- population and size bounds: `SQUARE_COUNT`, `MIN_SQUARE_SIZE`, `MAX_SQUARE_SIZE`
- motion and collisions: `JITTER_ACCELERATION`, `BASE_MAX_JITTER_SPEED`, `BOUNCE_DAMPING`
- chase logic: `CHASE_WEIGHT`, `MIN_SIZE_DELTA`, `DETECTION_RADIUS`
- lifecycle: `MIN_LIFESPAN`, `MAX_LIFESPAN`

This keeps behavior tuning centralized and easy to modify.

### 4.3 Initialization Layer

- `init_pygame()` initializes display, caption, and clock.
- `_make_square()` creates one randomized entity.
- `create_initial_squares(count)` builds the initial collection.

### 4.4 Behavior Layer

`update_squares(squares, dt_seconds)` executes one simulation step per frame.

Per entity, in order:

1. increment age
2. rebirth if lifespan expired
3. compute random jitter acceleration
4. find nearest larger target inside detection radius
5. blend jitter and directed chase acceleration
6. integrate velocity and position with `dt_seconds`
7. clamp speed based on square size
8. apply damped wall bounce on boundary collisions

Support functions:

- `_center(square)` gives entity center point
- `_find_nearest_larger_target(chaser, squares)` performs nearest-target search
- `rebirth_square(square)` resets entity to a fresh random state

### 4.5 Rendering Layer

`draw_scene(screen, squares)` renders one frame.

- clears background
- draws each square on an alpha surface
- fades opacity as `age / lifespan` increases
- flips display buffer

Visual fading communicates lifecycle progress without extra UI widgets.

### 4.6 Control Layer

`run()` orchestrates the frame pipeline:

1. tick clock and compute `dt_seconds`
2. poll/handle window events
3. update simulation state
4. draw frame
5. exit cleanly with `pygame.quit()`

The loop remains intentionally compact for educational readability.

## 5. Pygame Frame Flow

```text
while running:
  dt = clock.tick(FPS) / 1000.0
  running = handle_events()
  update_squares(squares, dt)
  draw_scene(screen, squares)
````

## 6. Code Explorer Architecture

### 6.1 Backend HTTP Server

`code-explorer/serve.py` implements a local HTTP server (`ThreadingHTTPServer` on `127.0.0.1:8000`) with three route types:

#### 6.1.1 API Endpoints

**GET `/api/tree`** — Repository Metadata

Returns complete file tree and project summary:

```json
{
  "root": "lab8-pygame",
  "entries": [
    {
      "path": "main.py",
      "name": "main.py",
      "language": "python",
      "size": 8192,
      "folder": ""
    },
    {
      "path": "code-explorer/app.js",
      "name": "app.js",
      "language": "javascript",
      "size": 4096,
      "folder": "code-explorer"
    }
  ],
  "summary": {
    "rootName": "lab8-pygame",
    "fileCount": 10,
    "textFileCount": 8,
    "pythonFileCount": 2,
    "topLevelFolders": ["code-explorer"]
  }
}
```

**GET `/api/file?path=<relative_path>`** — File Content

Returns the contents of a text file:

```json
{
  "path": "main.py",
  "name": "main.py",
  "language": "python",
  "content": "from __future__ import annotations\n..."
}
```

- Supports: `.py`, `.md`, `.txt`, `.json`, `.js`, `.css`, `.html`, `.yaml`, `.yml`, `.ini`, `.cfg`, `.sh`, `.xml`, `.csv`
- Blocks: binary files, paths outside repository root
- Encoding: UTF-8 with error replacement fallback

#### 6.1.2 Static Asset Routes

**GET `/`, `/index.html`, `/app.js`, `/styles.css`**

Serves frontend static files from `code-explorer/` directory.

#### 6.1.3 Security Controls

- **Path Resolution**: `resolve_repo_path()` ensures no path traversal attacks; target must be inside repository root
- **File Type Validation**: `is_text_file()` prevents serving binary files
- **Ignored Directories**: `.git`, `.venv`, `__pycache__`, `.DS_Store` excluded from tree listings

### 6.2 Frontend Client

`index.html`, `app.js`, and `styles.css` provide:

- **Project Summary Display**: file counts, Python file count, directory structure overview
- **File Search/Filter**: real-time substring matching across paths and file metadata
- **File Tree View**: hierarchical folder and file browser
- **File Viewer**: syntax-highlighted content display
- **Client-Side State**: selected file, search query stored in module-scoped `state` object

#### 6.2.1 Frontend Data Model

```javascript
const state = {
  entries: [], // array of file entry objects from /api/tree
  selectedPath: null, // current selected file path
  search: "", // current search query
};
```

#### 6.2.2 Frontend Key Functions

- `escapeHtml(value)` — Sanitize HTML special characters
- `formatSize(size)` — Convert bytes to human-readable format (B, KB, MB)
- `languageLabel(language)` — Map file extensions to language display names
- `filteredEntries()` — Filter file list by search query
- `buildTree(entries)` — Generate hierarchical folder structure
- `renderSummary(summary)` — Display project statistics

## 7. State, Data, and Determinism

- Simulation state is in-memory only.
- No persistence/database layer exists.
- Randomized initialization and movement use Python `random`.
- Determinism is not guaranteed because no fixed seed is enforced.

## 8. Non-Functional Characteristics

- Simplicity: single-file simulation code for teaching clarity.
- Performance: adequate for current entity count.
- Scalability limit: nearest-target logic is O(n^2) per frame.
- Portability: runs on standard Python + Pygame environment.

## 9. Architectural Decisions and Trade-Offs

1. Keep simulation in one file.

- Benefit: easy to read in class/lab context.
- Cost: limited modularity for larger features.

2. Use mutable entity objects.

- Benefit: straightforward update loop.
- Cost: harder to isolate pure logic for tests.

3. Combine random jitter with directed chase.

- Benefit: richer emergent behavior with low complexity.
- Cost: exact outcomes are less predictable.

4. Separate code explorer from game runtime.

- Benefit: no coupling between UI tooling and simulation loop.
- Cost: extra process to run when needed.

## 10. Known Constraints

- No automated test suite currently defined.
- No runtime debug overlay (FPS/entity metrics).
- Configuration is compile-time constants only (no config file/CLI flags).

## 11. Evolution Path

Potential incremental refactors:

1. split `main.py` into `config`, `model`, `systems`, and `render` modules
2. add deterministic seed option for reproducible runs
3. replace nearest-target brute force with spatial partitioning
4. introduce lightweight tests for pure helper functions

## 12. Operational Notes

### 12.1 Dependencies

- **Pygame Simulation**: `pygame==2.6.1`
- **Code Explorer**: None (uses Python standard library)

### 12.2 Environment Setup

```bash
# Create virtual environment
python3 -m venv .venv

# Activate (macOS/Linux)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 12.3 Running the Runtimes

**Pygame Simulation:**

```bash
python main.py
```

**Code Explorer:**

```bash
python code-explorer/serve.py
```

Then navigate to `http://127.0.0.1:8000` in a web browser.

### 12.4 Project File Structure

```
lab8-pygame/
├── main.py                    # Pygame simulation entry point
├── ARCHITECTURE.md            # This file
├── README.md                  # Quick start guide
├── REPORT.md                  # Project report template
├── JOURNAL.md                 # Development journal
├── requirements.txt           # Python dependencies
├── .venv/                     # Virtual environment (local)
└── code-explorer/
    ├── serve.py               # HTTP server backend
    ├── index.html             # Frontend HTML structure
    ├── app.js                 # Frontend client logic
    └── styles.css             # Frontend visual styling
```

### 12.5 Configuration Tuning

All simulation parameters are compile-time constants at the top of `main.py`. Key tunables:

| Parameter                            | Range/Value              | Effect                        |
| ------------------------------------ | ------------------------ | ----------------------------- |
| `WINDOW_WIDTH`, `WINDOW_HEIGHT`      | pixels                   | Display resolution            |
| `FPS`                                | ticks/sec (typically 60) | Frame rate target             |
| `SQUARE_COUNT`                       | entities (24)            | Number of squares             |
| `MIN_SQUARE_SIZE`, `MAX_SQUARE_SIZE` | pixels                   | Entity size bounds            |
| `JITTER_ACCELERATION`                | units/s² (220.0)         | Random motion intensity       |
| `BASE_MAX_JITTER_SPEED`              | units/s (180.0)          | Speed cap before chase        |
| `CHASE_WEIGHT`                       | 0–1 (0.55)               | Blend of jitter vs. chase     |
| `DETECTION_RADIUS`                   | pixels (220.0)           | Target acquisition range      |
| `MIN_LIFESPAN`, `MAX_LIFESPAN`       | seconds                  | Entity lifetime range         |
| `BOUNCE_DAMPING`                     | 0–1 (0.82)               | Energy loss on wall collision |

### 12.6 Performance Characteristics

- **Frame Time Budget**: ~16.7 ms @ 60 FPS
- **Update Complexity**: O(n²) nearest-neighbor search per frame
  - Current: 24 entities → ~576 distance checks/frame
  - At 60 FPS: manageable cost
- **Render Complexity**: O(n) alpha surface creation and blit
- **Memory**: ~few KB for simulation state + ~tens of KB for Pygame surfaces

### 12.7 Debugging / Diagnostics

- No built-in FPS display or debug overlay
- No profiler integration
- Simulation runs headless-compatible (Pygame backend configurable)
- Code Explorer logs suppressed (`ExplorerHandler.log_message()` is no-op)

## 13. Deployment and Integration

### 13.1 Local Execution Models

Both runtimes are designed for local execution only:

| Runtime       | Execution           | Network        | Persistence           |
| ------------- | ------------------- | -------------- | --------------------- |
| Pygame        | Single process      | None           | None (in-memory only) |
| Code Explorer | ThreadingHTTPServer | Localhost:8000 | File system read-only |

### 13.2 Concurrent Execution

Both runtimes can run **simultaneously** in separate terminal sessions without interference:

- Terminal 1: `python main.py` (Pygame simulation)
- Terminal 2: `python code-explorer/serve.py` (Code Explorer web UI)

No shared state, no synchronization primitives needed.

### 13.3 Extension Points

**To add features, consider:**

1. **Add simulation behavior**: Modify `update_squares()` or add new entity properties to `MovingSquare`
2. **Add interactive controls**: Extend `handle_events()` to respond to new Pygame events
3. **Add metrics/analytics**: Hook into `run()` to collect telemetry before/after frame cycles
4. **Add file operations**: Extend Code Explorer's `ExplorerHandler` with new routes (e.g., `/api/search`)
5. **Add visualization features**: Extend `draw_scene()` to render additional overlays (grid, stats, etc.)

### 13.4 Testing Considerations

- **Unit testable** functions: `_random_velocity()`, `_center()`, `_find_nearest_larger_target()`
- **Integration testing**: Start `run()` loop in test, verify state evolution
- **Code Explorer backend**: Test `resolve_repo_path()`, `is_text_file()`, route handlers in isolation
- **Code Explorer frontend**: DOM-based tests or headless browser simulation (Playwright, Puppeteer)

## 14. Security Model

### 14.1 Threat Model

- **Local-only execution**: no remote network exposure
- **File access**: Code Explorer limited to repository root via `resolve_repo_path()` sandboxing
- **Input validation**: query parameters checked; binary files rejected

### 14.2 Assumptions

- User runs code on trusted machine
- No multi-user isolation required
- File system permissions sufficient to protect sensitive data
- No authentication/authorization layer needed

## 15. Quality and Compliance

### 15.1 Code Quality

- **Typing**: Full type annotations with `from __future__ import annotations`
- **Style**: Python PEP 8; conciseness preferred for educational clarity
- **Documentation**: Docstrings on key functions; inline comments on complex logic

### 15.2 Known Limitations

- **No async I/O**: Pygame event loop runs on main thread; Code Explorer uses thread pool for HTTP handlers
- **No state persistence**: simulation loses all state on exit
- **No reproducibility**: random seed not fixed; same config produces different runs
- **Limited error recovery**: crashes exit ungracefully

### 15.3 Future Improvements

1. Add `--seed` CLI flag for reproducible runs
2. Implement spatial hashing for O(1) nearest-neighbor queries
3. Split `main.py` into `config.py`, `entities.py`, `physics.py`, `rendering.py`
4. Add regression test suite
5. Add configuration file support (YAML/TOML)
6. Implement frame-by-frame pause/resume in Pygame frontend
