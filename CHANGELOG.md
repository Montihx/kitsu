# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Root-level `ARCHITECTURE.md` with a concise production architecture map for frontend/backend layers.
- GitHub Actions CI workflow (`.github/workflows/ci.yml`) with backend and frontend validation jobs.
- `docs/archive/` folder to isolate historical artifacts from active project documentation.

### Changed
- Root `README.md` rewritten to standardize local setup, docker usage, and quality checks for both backend and frontend.
### Phase 1
- Added CI quality gates for backend (`ruff`, `mypy`, `pytest`) and frontend (`eslint`, `tsc`, `vitest`, `next build`).
- Moved repository root artifacts into project subtrees (`docs/archive`, `docs/assets`) to keep top-level focused on active infrastructure files.


### Moved
- Historical planning artifact moved from repository root into `docs/archive/glowing-enchanting-teapot.md`.
