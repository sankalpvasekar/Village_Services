# Village Services

A Django-based platform connecting local workers with job opportunities to reduce poverty through economic empowerment.

---

## 🌟 Overview

Village Services connects skilled local workers with job opportunities, helping communities thrive and individuals achieve financial independence through sustainable employment.

### Key Features

- **Local Community Focus**: Connect workers with opportunities in their community
- **Poverty Reduction**: Create sustainable employment opportunities
- **AI-Powered Matching**: Advanced algorithms match workers with the best opportunities
- **Resource Support**: Comprehensive community resources and support systems
- **Separate Dashboards**: Different interfaces for job recruiters and local workers

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/sankalpvasekar/Village_Services.git
   cd Village_Services
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database**

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a superuser (optional)**

   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**

   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Open your browser and go to `http://127.0.0.1:8000/`
   - The admin panel is available at `http://127.0.0.1:8000/admin/`

## 🎯 User Types

### Local Workers

- Find local job opportunities
- Build professional profiles
- Access community resources
- Get skill development support
- Receive AI-powered job recommendations

### Job Recruiters

- Post job opportunities
- Connect with local talent
- Support community development
- Manage applications
- Contribute to poverty reduction

## 🔧 Key Features

### Home Page

- Poverty-focused messaging and community impact
- Separate registration options for workers and recruiters
- Impact statistics and community benefits

### User Dashboards

- **Worker Dashboard**: Job opportunities, applications, profile management
- **Recruiter Dashboard**: Posted jobs, applications, job management
- **Resources Section**: Community support, skill development, financial assistance

### AI Job Recommendations

- Skill-based job matching
- Personalized recommendations
- Community resource recommendations

### Community Resources

- Skill development programs
- Financial support resources
- Health and wellness programs
- Legal assistance
- Emergency support
- Community groups and mentorship

## 🛠️ Technology Stack

- **Backend**: Django 4.2
- **Frontend**: HTML5, CSS3, JavaScript
- **Styling**: Tailwind CSS
- **Database**: SQLite (development), PostgreSQL (production)
- **AI/ML**: Custom recommendation algorithms

##  Deployment

### Production Setup

1. **Environment Variables**

   ```bash
   export DEBUG=False
   export SECRET_KEY='your-secret-key'
   export ALLOWED_HOSTS='your-domain.com'
   ```

2. **Database Setup**

   ```bash
   # For PostgreSQL
   pip install psycopg2-binary
   ```

3. **Static Files**

   ```bash
   python manage.py collectstatic
   ```

4. **Web Server**
   - Use Gunicorn or uWSGI
   - Configure Nginx as reverse proxy
   - Set up SSL certificates

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Django community for the excellent framework
- Tailwind CSS for the beautiful styling system
- Local communities for inspiration and feedback
- Contributors and supporters of poverty reduction initiatives

## 🎯 Mission

Our mission is to reduce poverty through local economic empowerment by connecting talent with opportunity, providing resources and support to help communities thrive.

---

**Village Services** - Empowering communities through local work opportunities.
