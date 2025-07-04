# AdCopy Pro - AI-Powered Ad Copy Generator

![AdCopy Pro Logo](static/images/logo.png)

AdCopy Pro is an advanced AI-powered platform that helps marketers create optimized ad copy for various platforms. It uses Graph RAG and Agentic RAG techniques to generate high-quality, platform-specific ad content that resonates with your target audience.

## 🌟 Key Features

* **Multi-Platform Support**
  - Generate optimized ad copy for Google Ads, Facebook, Instagram, LinkedIn, and Twitter
  - Platform-specific formatting and character limits
  - Tone adaptation (Professional, Casual, Witty, Urgent)

* **Advanced AI Capabilities**
  - Graph RAG for contextual ad generation
  - Knowledge Graph integration for platform-specific best practices
  - Continuous learning from user feedback

* **Smart Feedback System**
  - Rate generated content
  - Provide detailed feedback
  - Automatic pattern recognition for common issues
  - Continuous model improvement

* **Knowledge Base**
  - Access to marketing guidelines and best practices
  - Platform-specific recommendations
  - Searchable document repository

## 🛠️ Technologies Used

* **Backend**
  - Python 3.9+
  - FastAPI
  - Uvicorn (ASGI server)
  - FAISS (Vector Store)

* **AI/ML**
  - LangGraph for workflow orchestration
  - LangChain for LLM integration
  - SentenceTransformers for embeddings
  - Custom RAG implementation

* **Frontend**
  - HTML5, CSS3, JavaScript (ES6+)
  - Responsive design
  - Interactive UI components

## 🚀 Quick Start

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)
- Node.js (for frontend development, optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/adcopy-pro.git
   cd adcopy-pro
   ```

2. **Set up a virtual environment**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory with your API keys:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   GOOGLE_API_KEY=your_google_api_key
   ```

## 🏃 Running the Application

### Development Mode
```bash
# Start the FastAPI server with hot reload
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Production Mode
For production deployment, use Gunicorn with Uvicorn workers:
```bash
pip install gunicorn

gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
```

### Access the Application
Open your browser and navigate to:
```
http://localhost:8000
```

## 📚 Documentation

For detailed documentation, including API reference and developer guides, see the [Documentation](docs/README.md).

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details on how to get started.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📧 Contact

For questions or support, please contact [your-email@example.com](mailto:your-email@example.com)

Once the server is running, open your web browser and navigate to:

[http://localhost:8000](http://localhost:8000)

## Usage

1.  Enter your original ad text in the provided textarea.
2.  Select the desired tone (e.g., "professional", "casual", "humorous").
3.  Select the target platform (e.g., "Facebook", "Twitter", "LinkedIn").
4.  Click the "Rewrite Ad" button to see the AI-generated ad copy.

## Project Structure

```
. # Project Root
├── ad_copy_agent.py    # Defines the LangGraph nodes and agents
├── index.html          # Frontend HTML for the web interface
├── main.py             # FastAPI application, graph definition, and API endpoints
└── requirements.txt    # Python dependencies
```

## Contributing

Feel free to fork the repository, open issues, and submit pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details. (You might want to create a LICENSE file)

## Contact

For any questions or feedback, please contact [Your Name/Email/LinkedIn]

---

**Note on Logos and Symbols:**
To add your own logos or symbols, replace `path/to/your/logo.png` with the actual path to your image file. You can use Markdown image syntax `![Alt Text](image-path)` for this. Consider placing images in a dedicated `assets/` or `images/` folder within your project.