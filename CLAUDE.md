# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Biliup is a live stream recording and Bilibili video upload tool with a hybrid architecture: Rust backend + Python engine + Next.js frontend.

## Architecture

### Rust Crates (`crates/`)
- **biliup**: Core upload library - Bilibili API client for video uploads, credential handling, and download utilities
- **biliup-cli**: CLI application and web server (Axum-based) - handles authentication, uploads, downloads, and serves the WebUI on port 19159
- **stream-gears**: PyO3 bindings that bridge Rust functionality to Python - enables Python to call Rust's high-performance download/upload code

### Python Engine (`biliup/`)
- **engine/**: Download engine with `DownloadBase` abstract class in `download.py` - all platform plugins inherit from this
- **plugins/**: Platform-specific implementations (Bilibili, Douyu, Huya, Twitch, YouTube, etc.) - each file handles stream URL extraction and platform authentication
- **Danmaku/**: Real-time danmaku (chat) capture for various platforms
- **database/**: SQLAlchemy models and Alembic migrations

### Frontend (`app/`)
- Next.js 14 with React 18 and Semi UI component library
- Provides WebUI for managing recordings and uploads

## Build Commands

### Frontend (Next.js)
```bash
npm install      # Install dependencies
npm run dev      # Start development server (localhost:3000)
npm run build    # Production build (outputs to out/)
npm run lint     # ESLint
```

### Python Engine
```bash
maturin dev                 # Build stream-gears and install in development mode
python3 -m biliup           # Run the biliup service (requires npm run build first)
```

### Rust CLI
```bash
cargo build --release --bin biliup    # Build release binary
cargo run                             # Development run
```

### Full Development Setup
```bash
npm run build              # Build frontend first
maturin dev                # Build Python bindings
python3 -m biliup          # Start server (or: biliup server --auth)
```

## Key Technical Details

- Python requires `stream_gears` module (built via maturin from `crates/stream-gears`)
- The Python `__main__.py` calls `stream_gears.main_loop()` which starts the Rust server
- SQLite database is used for configuration and task state
- WebUI is embedded in the Rust binary via `rust-embed`
- Platform plugins follow a pattern: inherit `DownloadBase`, implement `acheck_stream()` for stream detection

## File Naming Conventions

- Platform downloaders: `biliup/plugins/<platform>.py`
- Danmaku handlers: `biliup/Danmaku/<platform>.py`
- Rust server routes: `crates/biliup-cli/src/server/api/`
