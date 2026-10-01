# Contributing to LinkedIn Nexus Agent

Thank you for contributing to the open-source LinkedIn Nexus Agent!

## Development Setup
1. Fork and clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the automated test suite:
   ```bash
   python -m pytest
   ```

## Code Guidelines
- Adhere to the **82-Rule Humanizer** principles for any prompts or LLM generation logic.
- Ensure all new routes or skills include automated unit tests under `tests/`.
- Verify 100% test passing rate before submitting PRs.
