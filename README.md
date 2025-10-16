# 🎯 CareerMatch AI - Resume Screener Agent

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-green.svg)](https://github.com/features/actions)

An AI-powered resume screening web application designed to automate and enhance the candidate selection process for recruiters and HR professionals. Built with modern cloud-native architecture and CI/CD automation.

## ✨ Features

- 🤖 **AI-Powered Analysis:** Advanced NLP and ML models for intelligent resume screening
- 📄 **Multi-Format Support:** Parse PDF, DOCX, and text resumes
- 🔍 **Smart Matching:** Automatically match candidates to job requirements
- 👤 **User Authentication:** Secure login and user management system
- 📊 **Job Tracking:** Track and manage job postings and applications
- 💬 **AI Chatbot:** Interactive resume analysis and Q&A
- 🎨 **Modern UI:** Clean, responsive Streamlit interface
- 🐳 **Docker Ready:** Containerized for easy deployment
- 🚀 **CI/CD Pipeline:** Automated testing and deployment
- ☁️ **Cloud Native:** Deploy to Railway, Render, AWS, Azure, or GCP

## 🏗️ Tech Stack

- **Frontend:** Streamlit
- **Backend:** Python 3.11
- **Database:** MySQL 8.0
- **AI/ML:** Transformers, Sentence-Transformers, spaCy, NLTK
- **Containerization:** Docker & Docker Compose
- **CI/CD:** GitHub Actions
- **Cloud Platforms:** Railway, Render, AWS, Azure, GCP

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- MySQL 8.0+
- Git
- Docker (optional, for containerized deployment)

### Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Prachi5555/CareerMatch-AI.git
   cd CareerMatch-AI
   ```

2. **Set up environment:**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit .env with your credentials
   # Set DB_USER, DB_PASSWORD, etc.
   ```

3. **Create virtual environment:**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Setup database:**
   ```bash
   python setup_mysql.py
   ```

6. **Run the application:**
   ```bash
   streamlit run resume_chatbot.py
   ```

7. **Access the app:**
   Open your browser to `http://localhost:8501`

### Docker Deployment

```bash
# Start application with MySQL
docker-compose up -d

# View logs
docker-compose logs -f

# Stop application
docker-compose down
```

## 📦 Project Structure

```
CareerMatch-AI/
├── .github/
│   └── workflows/          # CI/CD pipelines
├── auth.py                 # Authentication system
├── config.py              # Configuration management
├── database.py            # Database operations
├── resume_parser.py       # Resume parsing logic
├── resume_chatbot.py      # Main Streamlit app
├── job_tracker.py         # Job tracking features
├── free_ai_analyzer.py    # AI analysis engine
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Multi-container setup
├── railway.json          # Railway deployment config
├── render.yaml           # Render deployment config
├── .env.example          # Environment template
└── DEPLOYMENT.md         # Deployment guide
```

## 🌐 Cloud Deployment

This application is production-ready and can be deployed to multiple cloud platforms:

### Railway (Recommended)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway up
```

### Render
- Push to GitHub
- Connect repository in Render dashboard
- Auto-deploys using `render.yaml`

### Docker-based Platforms (AWS, Azure, GCP)
```bash
docker build -t resume-screener .
# Push to your container registry
# Deploy using platform-specific tools
```

📖 **Full deployment guide:** See [DEPLOYMENT.md](DEPLOYMENT.md)

## 🔧 Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
# Database
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=resume_analyzer

# Application
APP_ENV=development
DEBUG=True
SECRET_KEY=your-secret-key
```

### Database Setup

The application automatically creates required tables on first run. To manually setup:

```bash
python setup_mysql.py
```

## 🧪 Testing & CI/CD

### Automated Testing

GitHub Actions automatically runs tests on every push:
- Code quality checks (flake8, black)
- Security scanning (bandit)
- Docker build verification

### Manual Testing

```bash
# Install test dependencies
pip install pytest flake8 black

# Run linting
flake8 .

# Check code formatting
black --check .
```

## 📊 Features in Detail

### 1. Resume Parsing
- Extract text from PDF and DOCX files
- Identify key information (skills, experience, education)
- Support for multiple resume formats

### 2. AI Analysis
- Semantic similarity matching
- Skill extraction and categorization
- Experience level assessment
- Education verification

### 3. Job Tracking
- Create and manage job postings
- Track applications per job
- Filter and search candidates

### 4. User Management
- Secure authentication system
- User profiles and preferences
- Role-based access control

## 🛠️ Development

### Adding New Features

1. Create a feature branch
2. Make your changes
3. Run tests locally
4. Submit a pull request

### Code Style

- Follow PEP 8 guidelines
- Use type hints where applicable
- Add docstrings to functions
- Format code with `black`

## 🐛 Troubleshooting

### Common Issues

**Database Connection Error:**
```bash
# Check MySQL is running
mysql -u root -p

# Verify credentials in .env file
```

**Module Not Found:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Docker Issues:**
```bash
# Clear Docker cache
docker system prune -a

# Rebuild containers
docker-compose up --build
```

## 📈 Roadmap

- [ ] Advanced analytics dashboard
- [ ] Bulk resume upload
- [ ] Email notifications
- [ ] API endpoints for integrations
- [ ] Multi-language support
- [ ] Resume template matching
- [ ] Interview scheduling integration

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

**Prachi5555** - *Initial work* - [GitHub](https://github.com/Prachi5555)

## 🙏 Acknowledgments

- Streamlit for the amazing web framework
- HuggingFace for transformer models
- The open-source community

## 📞 Support

- 📧 Create an issue for bug reports
- 💬 Discussions for questions and ideas
- 📚 Check [DEPLOYMENT.md](DEPLOYMENT.md) for deployment help

---

**⭐ Star this repository if you find it helpful!**

*Built with ❤️ by Prachi5555*