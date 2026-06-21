# Contributing to AUTO DRIVE UPLOADER

Thank you for your interest in contributing! Please follow these guidelines:

## Code Style

- Follow PEP 8 style guidelines
- Use type hints for all functions
- Write docstrings for all modules and classes
- Maximum line length: 100 characters

## Cyberpunk Aesthetic

- Maintain the Matrix-inspired UI design
- Use `bright_cyan` as the accent color
- All dashboard views MUST include the mandatory watermark header:
  ```python
  Panel(Align.center("[bold black]🛠️  DESIGNED BY MANOHAR AVINASH  🛠️[/]"), 
        style="on bright_cyan text bold", box=None)
  ```

## Platform Compatibility

- Test on both Termux and Linux environments
- Use `os.path.expanduser()` for all user paths
- Ensure subprocess commands work cross-platform

## Submitting Changes

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make your changes with clear commit messages
3. Test thoroughly on Termux/Linux
4. Submit a pull request with description

## Reporting Issues

Include:
- Environment (Termux / Linux version)
- Python version
- RClone version
- Full error message and traceback

## Questions?

Open an issue or contact the maintainer.
