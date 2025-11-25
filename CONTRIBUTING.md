# Contributing to Judgment in Fifteen Days

Thank you for your interest in contributing to this project!

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- A clear description of the problem
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Screenshots (if applicable)
- Your system information (OS, Python version)

### Suggesting Features

Feature suggestions are welcome! Please create an issue with:
- A clear description of the feature
- Why this feature would be useful
- How it should work

### Code Contributions

1. Fork the repository
2. Create a new branch for your feature (`git checkout -b feature/AmazingFeature`)
3. Make your changes
4. Test your changes thoroughly
5. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
6. Push to the branch (`git push origin feature/AmazingFeature`)
7. Open a Pull Request

### Code Style

- Follow PEP 8 style guidelines for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions focused and concise

### Adding New Content

#### Adding New Days

Edit `Chinese Text.csv` and `English Text.csv` to add content for new days. Follow the existing format:
- Day number
- Narrative text
- Options A, B, C
- Result texts
- Settlement messages

#### Adding Images

- Place images in the root directory
- Follow naming convention: `Day X.PNG` for backgrounds
- Ensure images are optimized for size
- Use PNG format for UI elements

#### Adding Audio

- Audio files should be in MP3 format
- Ensure proper licensing (CC0 or compatible)
- Document the source and license in `LICENSE.md`

### Translation

To add a new language:
1. Create new CSV files (e.g., `French Text.csv`)
2. Translate all game content
3. Test the game with the new language
4. Update the language selection dialog in `runner_redesigned.py`

### Testing

Before submitting:
- Test the game with both languages (Chinese and English)
- Ensure all days play correctly
- Check that audio works properly
- Verify fullscreen mode works
- Test on different screen resolutions if possible

## Development Setup

```bash
# Clone the repository
git clone https://github.com/Huicong967/Judgment-in-Fifteen-Days.git

# Install dependencies
pip install Pillow pygame

# Run the game
python start_game_new.py
```

## Questions?

If you have questions about contributing, feel free to create an issue with the "question" label.

## Code of Conduct

- Be respectful and constructive
- Focus on what is best for the project
- Show empathy towards other contributors
