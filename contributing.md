# Contributing to AgenticAds

We welcome contributions from the community! Here's how you can help improve AgenticAds.

## 🚀 Ways to Contribute

### 1. Report Bugs
- Use the GitHub Issues page to report bugs
- Include detailed steps to reproduce the issue
- Add screenshots if applicable
- Mention your environment (OS, Python version, Node.js version)

### 2. Suggest Features
- Check existing issues to avoid duplicates
- Create a new issue with the "enhancement" label
- Describe the feature and its use case
- Consider implementation approach if you're familiar with the codebase

### 3. Code Contributions
- Fork the repository
- Create a feature branch: `git checkout -b feature/amazing-feature`
- Make your changes
- Add tests if applicable
- Ensure all tests pass
- Commit with clear messages: `git commit -m 'Add some amazing feature'`
- Push to your fork: `git push origin feature/amazing-feature`
- Open a Pull Request

## 🛠️ Development Setup

### Prerequisites
- **Python 3.10+** (required for backend)
- **Node.js 16+** (for frontend)
- **MongoDB** (local or Atlas cluster)

### Getting Started

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/agentic-ads.git
   cd agentic-ads
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env  # Configure your environment
   python main.py
   ```

3. **Frontend Setup**
   ```bash
   cd ../  # Back to root
   npm install
   npm run dev
   ```

## 📝 Code Guidelines

### General Principles
- Follow **SOLID principles** in your code
- Write **clean, readable code** with proper documentation
- Add **type hints** for Python code
- Use **TypeScript** for new frontend features
- Follow existing **naming conventions**

### Python Backend
- Use **type hints** for all function parameters and return types
- Write **docstrings** for public functions and classes
- Follow **PEP 8** style guidelines
- Add **unit tests** for new functionality
- Use **async/await** for I/O operations

### React Frontend
- Use **functional components** with hooks
- Follow **custom hooks pattern** for business logic
- Use **TypeScript interfaces** for props and state
- Write **descriptive component names**
- Add **PropTypes** or TypeScript for type checking

### CSS/Styling
- Use **CSS variables** for consistent theming
- Follow **BEM methodology** for class naming
- Keep **component styles scoped**
- Use **responsive design** principles

## 🧪 Testing

### Running Tests
```bash
# Backend tests (if added)
cd backend
python -m pytest

# Frontend tests (if added)
npm test
```

### Writing Tests
- Add tests for new features
- Test both **happy path** and **edge cases**
- Use **descriptive test names**
- Mock external dependencies

## 📚 Documentation

- Update **README.md** for user-facing changes
- Add **inline comments** for complex logic
- Update **type definitions** when changing interfaces
- Document **environment variables** in setup guides

## 🔄 Pull Request Process

1. **Create a feature branch** from `main`
2. **Make your changes** following the guidelines above
3. **Add tests** if applicable
4. **Update documentation** if needed
5. **Ensure all tests pass**
6. **Submit your PR** with a clear description

### PR Template
```
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] Manual testing completed

## Screenshots
Add screenshots if UI changes

## Checklist
- [ ] Code follows project style
- [ ] Tests pass
- [ ] Documentation updated
- [ ] TypeScript types updated (if applicable)
```

## 🏆 Recognition

Contributors will be acknowledged in the README and our social channels. Significant contributions may lead to maintainer status.

## 📞 Support

If you need help or have questions:
- Open an issue for bugs or feature requests
- Join our community discussions
- Contact the maintainers directly

---

Thank you for contributing to AgenticAds! 🚀
