# Contributing

## Getting Started

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest src/tests/`)
5. Commit (`git commit -m 'Add amazing feature'`)
6. Push (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Development Guidelines

- Follow PEP 8 for Python code
- Each microservice must include a `/health` endpoint
- Add type hints to all function signatures
- Write tests for new functionality
- Update API reference docs when adding endpoints

## Code Style

- Python: PEP 8, type hints required, docstrings for public APIs
- Frontend: TypeScript, ESLint, Prettier config included
- Commits: Conventional commits format (`feat:`, `fix:`, `docs:`, etc.)

## Architecture Principles

- Services are stateless and independently deployable
- Communication via Dapr service invocation or events
- No direct database access between services — each owns its data
- Use the shared base module (`services/shared/base.py`) for common patterns
