# Light Refactoring Plan - Lab 8 Pygame Project

## 1. Overview

### Current State

The Lab 8 project consists of three independent runtimes:

- **main.py**: Pygame simulation (~250 lines) with moving square entities
- **code-explorer/serve.py**: HTTP file browser (~150 lines)
- **quiz/serve.py**: Quiz server (~130 lines)
- **quiz/app.js**: Quiz frontend (~280 lines)

### General Assessment

**Strengths:**

- Good use of type annotations and dataclasses
- Functions have clear docstrings
- Separation of concerns (three independent runtimes)
- Adequate code organization with helper functions

**Improvement Opportunities:**

- **Magic numbers** scattered throughout (especially in main.py)
- **Repeated logic** in collision handling and coordinate calculations
- **Long functions** that do multiple things (e.g., `update_squares` is 60+ lines)
- **Inconsistent naming** conventions in some places
- **Code duplication** across multiple server files
- **Large blocks** of related code could be grouped into helper functions
- **Comments could be more frequent** to explain _why_ code works, not just _what_ it does

---

## 2. Refactoring Goals

1. **Reduce code duplication** - Extract repeated patterns into reusable functions
2. **Improve readability** - Break long functions into smaller, focused units
3. **Organize constants** - Group related configuration values
4. **Clarify intent** - Add comments explaining design decisions
5. **Enhance maintainability** - Make it easier for students to modify and extend
6. **Preserve behavior** - All changes are refactoring only (no new features)

---

## 3. Step-by-Step Refactoring Plan

### Step 1: Extract Physics Constants into a Config Dictionary (main.py)

**What to do:**
Group related physics constants into organized dictionaries for clarity.

**Why this helps:**

- Constants are easier to find and modify
- Related values are grouped logically
- Beginners can see which parameters affect similar behaviors

**Current code pattern:**

```python
WINDOW_WIDTH = 800
JITTER_ACCELERATION = 220.0
CHASE_WEIGHT = 0.55
```

**Refactoring approach:**

```python
# Create logical groupings
DISPLAY = {"width": 800, "height": 600, "fps": 60}
PHYSICS = {"jitter_accel": 220.0, "max_jitter_speed": 180.0, "bounce_damping": 0.82}
BEHAVIOR = {"chase_weight": 0.55, "min_size_delta": 6, "detection_radius": 220.0}
```

**Add inline comments:**

- Explain why constants are grouped this way
- Comment what each group affects (e.g., "# PHYSICS: affects square movement mechanics")

---

### Step 2: Extract Wall Bounce Logic into a Separate Function (main.py)

**What to do:**
Move the wall collision code from `update_squares()` into its own `_bounce_off_walls()` function.

**Why this helps:**

- `update_squares()` is too long (~60 lines); splitting it up makes it easier to understand
- The bounce logic is self-contained and can be tested independently
- Students can modify bounce behavior without touching other physics

**Current pattern:**

```python
# --- Bounce off walls ---
if square.x < 0:
    square.x = 0
    square.vx = abs(square.vx) * BOUNCE_DAMPING
# ... (repeated for all four walls)
```

**New function to create:**

```python
def _bounce_off_walls(square: MovingSquare) -> None:
    """Handle collision with window boundaries and reflect velocity."""
    # (move all four wall checks here)
```

**Add inline comments:**

- Explain what `abs(square.vx) * BOUNCE_DAMPING` does (energy loss on bounce)
- Comment why we use `abs()` (to reverse direction while preserving magnitude)

---

### Step 3: Extract Acceleration Blending Logic into a Function (main.py)

**What to do:**
Create `_blend_accelerations()` function that combines jitter and chase acceleration.

**Why this helps:**

- `update_squares()` becomes shorter and more readable
- The blending concept (mixing two behaviors) is highlighted
- Students can understand that acceleration is a weighted average

**Current pattern:**

```python
ax = jitter_ax * (1.0 - CHASE_WEIGHT) + directed_ax * CHASE_WEIGHT
ay = jitter_ay * (1.0 - CHASE_WEIGHT) + directed_ay * CHASE_WEIGHT
```

**New function to create:**

```python
def _blend_accelerations(
    jitter_ax: float, jitter_ay: float,
    directed_ax: float, directed_ay: float,
    chase_weight: float
) -> tuple[float, float]:
    """Blend random jitter with directed chase acceleration.

    Higher chase_weight = more directed motion, less randomness.
    Lower chase_weight = more random motion, less directed.
    """
```

**Add inline comments:**

- Explain the weighted average formula
- Comment that `CHASE_WEIGHT = 0.55` means 55% chase, 45% jitter

---

### Step 4: Extract Velocity Calculation into a Function (main.py)

**What to do:**
Create `_calculate_velocity_from_acceleration()` that handles velocity integration and clamping.

**Why this helps:**

- Another section of `update_squares()` is simplified
- The integration process (v += a\*dt) is explicitly shown
- Clamping logic is isolated

**New function to create:**

```python
def _calculate_velocity_from_acceleration(
    square: MovingSquare, ax: float, ay: float, dt_seconds: float, max_speed: float
) -> None:
    """Update velocity using acceleration and clamp to max speed."""
```

**Add inline comments:**

- Explain Euler integration (v_new = v_old + a\*dt)
- Clarify why we clamp velocity (prevent runaway speeds)

---

### Step 5: Extract Helper Functions for Common HTTP Patterns (quiz/serve.py & code-explorer/serve.py)

**What to do:**
Create a shared base class or utility functions for JSON/file sending that both servers use.

**Why this helps:**

- Removes code duplication (`_send_json` appears in both files)
- Shows students the DRY principle (Don't Repeat Yourself)
- Makes it easier to fix bugs in multiple places

**Current duplication:**
Both `QuizHandler` and `ExplorerHandler` have similar `_send_json()` methods.

**Refactoring approach:**
Create a base handler class:

```python
class BaseHTTPHandler(BaseHTTPRequestHandler):
    """Common utilities for HTTP handlers."""

    def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        # (shared implementation)
```

**Add inline comments:**

- Explain why DRY principle matters (easier to maintain)
- Comment that both servers benefit from shared utility code

---

### Step 6: Extract DOM Management Functions in quiz/app.js

**What to do:**
Create utility functions for common DOM operations (e.g., `hideView()`, `showView()`).

**Why this helps:**

- Current `showView()` is repeated; extract it fully
- Reduces chances of forgetting to update one place
- Makes view management clearer

**Current pattern:**

```javascript
[quizSelectionView, quizTakingView, resultsView].forEach((v) =>
  v.classList.remove("active"),
);
view.classList.add("active");
```

**New utility function:**

```javascript
function hideAllViews() {
  [quizSelectionView, quizTakingView, resultsView].forEach((view) => {
    // Hide with comment explaining why we hide all first
    view.classList.remove("active");
  });
}

function showView(view) {
  // Use centralized hide-all + show-one pattern
  hideAllViews();
  view.classList.add("active");
}
```

**Add inline comments:**

- Explain that we hide-all-then-show-one to prevent multiple views showing
- Comment why this pattern prevents bugs (only one view active at a time)

---

### Step 7: Improve Naming in code-explorer/serve.py

**What to do:**
Rename `iter_repository_entries()` to `get_repository_entries()` for clarity.

**Why this helps:**

- The function returns a list, not an iterator; the name should reflect that
- Beginners won't confuse it with Python's iterator protocol
- More consistent naming with other similar functions

**Current name:** `iter_repository_entries()` (implies iterator protocol)

**New name:** `get_repository_entries()` (clearly returns a value)

**Add inline comments:**

- Explain that we filter out ignored directories (security/cleanliness)
- Comment what the returned dictionary structure contains

---

### Step 8: Add Explanatory Comments to Physics Integration (main.py)

**What to do:**
Add detailed comments explaining the physics simulation loop in `update_squares()`.

**Why this helps:**

- Students understand the step-by-step physics calculation
- Clarifies the order: age → rebirth → acceleration → velocity → position → collision
- Demonstrates the importance of delta-time in physics

**Pattern to enhance:**

```python
# Current: minimal comments
for square in squares:
    square.age += dt_seconds
    # ...more logic...
```

**Enhanced with comments:**

```python
# Process each square through one frame of simulation
for square in squares:
    # Step 1: Update age toward end-of-life
    square.age += dt_seconds

    # Step 2: Rebirth if lifespan expired (prevents age drift)
    if square.age >= square.lifespan:
        rebirth_square(square)
        continue  # Skip physics update for freshly-born squares

    # Step 3-5: ... calculate and apply forces ...
    # Step 6: ... integrate velocity and position ...
    # Step 7: ... handle boundary collisions ...
```

**Add inline comments:**

- Explain why we use `dt_seconds` (frame-rate independence)
- Comment that we `continue` after rebirth (why we skip this frame)

---

## 4. Final Output Requirements (Mandatory)

When this plan is executed, the refactored code MUST include inline comments that:

### 4.1 Explain Each Change

For every extracted function, the original location should have a comment like:

```python
# Bounce off walls (separated into _bounce_off_walls() for clarity)
_bounce_off_walls(square)
```

### 4.2 Explain Why It Improves the Code

Each refactored section should include a comment explaining the benefit:

```python
# Extracted for readability: _update_squares() was 60+ lines.
# This helper keeps collision logic together and testable.
def _bounce_off_walls(square: MovingSquare) -> None:
```

### 4.3 Highlight Programming Concepts

Comments should reference programming principles:

```python
# DRY Principle: We removed duplicate _send_json() by creating a base class.
# This means bug fixes in JSON handling happen in ONE place, not three.
class BaseHTTPHandler(BaseHTTPRequestHandler):
```

### 4.4 Final Code Structure

The refactored code will have:

- **Clearer function names** that describe what they do
- **Shorter functions** (under 20-30 lines each)
- **Grouped constants** in logical dictionaries
- **Extracted helpers** for repeated patterns
- **Inline comments** explaining the _why_, not just the _what_
- **All original behavior preserved** (no logic changes)

---

## 5. Key Concepts for Students

### 5.1 Code Organization: The "Single Responsibility Principle"

Each function should do ONE thing well.

**Example:**

- `update_squares()` currently does: age tracking, rebirth, jitter, chase, acceleration blending, velocity clamping, position integration, and collision handling
- Better: `update_squares()` orchestrates the loop; helper functions handle each step

**Why it matters:** Easier to test, debug, and modify individual pieces

### 5.2 Code Reuse: The "DRY Principle" (Don't Repeat Yourself)

If code appears in multiple places, extract it to a shared location.

**Example:**

- `_send_json()` was in both `QuizHandler` and `ExplorerHandler`
- Better: Create a base class with this method once

**Why it matters:** Bug fixes apply everywhere; code is easier to maintain

### 5.3 Naming Conventions

Names should clearly indicate what something does.

**Example:**

- `iter_repository_entries()` sounds like it returns an iterator → confusing
- `get_repository_entries()` clearly says "get a list"

**Why it matters:** Beginners understand code faster when names are clear

### 5.4 Magic Numbers vs. Named Constants

Avoid "magic numbers" scattered throughout code.

**Example:**

- Current: `255 - ratio * 175` (why 255? why 175?)
- Better: `ALPHA_MAX - ratio * ALPHA_FADE_RANGE` with a comment explaining the fade effect

**Why it matters:** Code intent is clear; easier to modify behavior

### 5.5 Physics Simulation: Step-by-Step Integration

Physics simulations follow a pattern:

1. Update time-based values (age)
2. Handle boundary conditions (rebirth)
3. Calculate forces (jitter + chase)
4. Integrate velocity (v += a\*dt)
5. Integrate position (x += v\*dt)
6. Handle collisions

**Why it matters:** Students understand that order matters in simulations

---

## 6. Safety Notes

### 6.1 Testing After Refactoring

After each step:

1. Run the refactored code to verify behavior is unchanged
2. Test edge cases (e.g., squares at boundaries, newly reborn squares)
3. Watch the visual simulation to ensure physics looks the same

### 6.2 Preserve Original Behavior

**Critical rule:** Every refactoring must produce identical output.

- No numerical changes (physics must look the same)
- No API changes (servers must respond identically)
- No UI changes (quiz frontend must look the same)

**How to verify:**

- Compare results before/after (simulation should be visually identical)
- Check API responses are unchanged (JSON format must be the same)

### 6.3 Version Control Considerations

Make small commits for each step:

```bash
git commit -m "Extract _bounce_off_walls() from update_squares()"
git commit -m "Group physics constants into PHYSICS dict"
git commit -m "Extract velocity blending into _blend_accelerations()"
```

This way, if a refactor breaks something, it's easy to identify which step caused it.

### 6.4 Common Pitfalls to Avoid

- **Don't change the function signature**: If `_random_velocity()` takes `size`, keep it that way
- **Don't modify algorithm logic**: The physics should produce identical results
- **Don't rename constants**: If you group them, keep the same values
- **Don't introduce new dependencies**: Refactoring should use existing imports only

---

## 7. Suggested Refactoring Order

Start with simpler changes, progress to more complex:

1. **Step 1** (15 min): Group constants in main.py (low risk)
2. **Step 2** (20 min): Extract `_bounce_off_walls()` (isolated logic)
3. **Step 3** (20 min): Extract `_blend_accelerations()` (math operation)
4. **Step 4** (20 min): Extract `_calculate_velocity_from_acceleration()` (physics)
5. **Step 5** (25 min): Create base HTTP handler class (requires code movement)
6. **Step 6** (15 min): Extract DOM utilities in quiz/app.js (isolated UI)
7. **Step 7** (10 min): Rename `iter_repository_entries()` (find & replace)
8. **Step 8** (15 min): Add physics explanation comments (documentation)

**Total estimated time:** ~2-3 hours for beginners

---

## 8. Benefits After Refactoring

### Code Quality

- Functions are shorter (easier to read)
- Logic is better organized (easier to find things)
- Constants are grouped (easier to modify behavior)

### Maintainability

- Duplicated code is eliminated (fewer places to fix bugs)
- Helper functions are reusable (for future extensions)
- Comments explain the "why" (students understand intentions)

### Learning Value

- Students practice extraction refactoring
- Students see DRY principle in action
- Students understand code organization best practices

### Future Development

- Adding new physics behaviors is easier (modify extracted functions)
- Adding new quiz types is easier (use base HTTP handler)
- Testing individual systems is easier (smaller functions are testable)

---

## 9. Example: Before & After (main.py snippet)

### Before Refactoring

```python
def update_squares(squares: List[MovingSquare], dt_seconds: float) -> None:
    """Update all squares for one frame, including life span / rebirth."""
    for square in squares:
        # --- Life Span / Rebirth ---
        square.age += dt_seconds
        if square.age >= square.lifespan:
            rebirth_square(square)
            continue

        # --- Base jitter ---
        speed_scale = BASE_SQUARE_SIZE / square.size
        max_speed = BASE_MAX_JITTER_SPEED * speed_scale
        jitter_ax = random.uniform(-JITTER_ACCELERATION, JITTER_ACCELERATION)
        jitter_ay = random.uniform(-JITTER_ACCELERATION, JITTER_ACCELERATION)

        # ... (40+ more lines of logic) ...

        # --- Bounce off walls ---
        if square.x < 0:
            square.x = 0
            square.vx = abs(square.vx) * BOUNCE_DAMPING
        # ... (3 more wall checks, 10+ lines)
```

### After Refactoring (with comments explaining changes)

```python
def update_squares(squares: List[MovingSquare], dt_seconds: float) -> None:
    """Update all squares for one frame, including life span / rebirth.

    Refactored for clarity: Helper functions now handle wall collisions,
    acceleration blending, and velocity calculation. This keeps the main
    loop focused on the overall simulation flow.
    """
    for square in squares:
        # Step 1: Update age (refactored: explicit step numbering helps
        # beginners follow the simulation sequence)
        square.age += dt_seconds
        if square.age >= square.lifespan:
            rebirth_square(square)
            continue  # Skip physics for freshly-born squares

        # Step 2-4: Calculate acceleration and velocity (extracted into
        # helper functions for readability; each helper does one job)
        speed_scale = BASE_SQUARE_SIZE / square.size
        max_speed = BASE_MAX_JITTER_SPEED * speed_scale

        jitter_ax, jitter_ay = _calculate_jitter_acceleration()
        directed_ax, directed_ay = _calculate_chase_acceleration(square, squares)

        # Blend behaviors together (extracted function clarifies the mixing)
        ax, ay = _blend_accelerations(
            jitter_ax, jitter_ay, directed_ax, directed_ay, CHASE_WEIGHT
        )

        # Step 5: Integrate velocity (extracted function handles clamping)
        _calculate_velocity_from_acceleration(square, ax, ay, dt_seconds, max_speed)

        # Step 6: Integrate position
        square.x += square.vx * dt_seconds
        square.y += square.vy * dt_seconds

        # Step 7: Handle wall collisions (extracted into separate function
        # so the bounce logic is together and doesn't clutter the main loop)
        _bounce_off_walls(square)
```

**Comments explain:**

- ✓ What changed (helper function extracted)
- ✓ Why it helps (readability, clarity of simulation flow)
- ✓ Key concepts (DRY, single responsibility)

---

## 10. Next Steps

1. **Choose a starting point**: Begin with Step 1 (grouping constants)
2. **Make one change at a time**: Test after each step
3. **Write comments as you go**: Explain what changed and why
4. **Compare before/after**: Verify behavior is identical
5. **Celebrate progress**: Each step improves code clarity!
