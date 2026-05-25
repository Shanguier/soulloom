# SoulLoom 🧵

**From conversation fragments to an interactive soul — weave dialogue data into AI personas.**

SoulLoom is an open-source framework that transforms personal chat conversations into interactive AI personas with stage-aware personality. Unlike generic character builders, SoulLoom captures **how a person's expression evolves across different relationship stages** — their verbal tics, humor patterns, emotional rhythms, and interaction heuristics.

---

## Why SoulLoom?

Existing "AI character" approaches either:
- **Manual prompt engineering** — no data grounding, pure guesswork
- **Public persona cloning** — copies from internet, generic, no personal touch
- **Static snapshots** — treats a person as unchanging

SoulLoom solves all three: **data-driven, personal, and stage-aware.**

## The Loom Metaphor

| Concept | Meaning |
|---------|---------|
| **Warp (经线)** | Stable core personality — traits that persist across all stages |
| **Weft (纬线)** | Stage-specific expression — tone, topics, humor that shift over time |
| **Shuttle (梭子)** | The analysis process — moving back and forth across data to weave warp and weft together |

A person is not one thing. They shift depending on:
- How well they know you
- What life stage they're in
- What the relationship context is

SoulLoom captures this.

---

## Pipeline

```
User's chat JSON
    │
    ▼
Phase 1: Thread Sorting (理线)
    │ Data validation, stats overview, target confirmation
    ▼
Phase 2: Color Separation (分色)
    │ Time-distribution analysis, dynamic stage detection
    │ Stage names derived from content + volume — no fixed templates
    ▼
Phase 3: Pattern Design (定织)
    │ Choose mode: full weave / per-stage / single stage / custom range
    ▼
Phase 4: Weaving (织造)
    │ Expression DNA extraction → Personality prism → Mental models
    │ → Decision heuristics → Emotional tone curve
    ▼
Phase 5: Finishing (成衣)
    │ Generate deployable Claude Skill with stage selector
```

## Output

An interactive Claude Skill installed at `.claude/skills/[name]-perspective/`:

```
[person]-perspective/
├── SKILL.md                       # Full persona with stage selector
├── references/
│   ├── base-profile.md            # Stable core (warp)
│   ├── stages/                    # Per-stage configs (weft)
│   │   ├── 01-stage-one.md
│   │   └── ...
│   └── sources/
│       └── chat_data.json         # Original data (read-only archive)
```

### What you get:
- **Stage selector** — talk to the person at different phases of the relationship
- **Dynamic response style** — matches the selected era's tone and vocabulary
- **Honesty boundaries** — what this persona knows vs. what it doesn't

---

## Use Cases

| Use Case | Description |
|----------|-------------|
| **Digital legacy** | Preserve a loved one's communication patterns |
| **Creator AI分身** | Turn your own chat history into an AI that answers like you |
| **Character craft** | Game NPCs grounded in real conversation data |
| **Self-reflection** | See your own communication patterns through mined data |
| **Relationship archive** | An interactive memory of a meaningful connection |

---

## Getting Started

```bash
# Clone the repo
git clone https://github.com/Shanguier/soulloom.git
cd soulloom

# The SKILL.md is the main entry point.
# Load it into Claude Code and it will guide you through the pipeline.
```

**Prerequisites:**
- Claude Code (or any Claude-compatible client)
- A chat export JSON file (WhatsApp, Telegram, WeChat, or any format with sender/timestamp/message)

---

## Project Status

SoulLoom has been validated with real-world datasets:
- **2,445 messages / 7 stages** — full pipeline tested
- **30,000+ messages / 8 stages** — scaled verification

Both produced working, stage-aware interactive personas.

---

## License

MIT — free to use, modify, and distribute.

## Links

- **Application for Xiaomi MiMo Orbit 100T Token Plan**: [100t.xiaomimimo.com](https://100t.xiaomimimo.com)
