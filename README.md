# Village Services

## 🎥 YouTube Demo
(Add YouTube video link here after upload)

## Project Description
A Django-based platform connecting local workers with job opportunities to reduce poverty through economic empowerment. The platform uses AI-powered matching to connect skilled local workers with job opportunities, helping communities thrive and individuals achieve financial independence.

## Tech Stack
- **Backend**: Django 4.2
- **Frontend**: HTML5, CSS3, JavaScript
- **Styling**: Tailwind CSS
- **Database**: SQLite (development), PostgreSQL (production)
- **AI/ML**: Google AI APIs, Custom recommendation algorithms
- **Deployment**: Gunicorn, WhiteNoise

## How to Run
1. Clone the repository:
   ```bash
   git clone https://github.com/sankalpvasekar/Village_Services.git
   cd Village_Services/Local_Free_Lancer_New
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Run the development server:
   ```bash
   python manage.py runserver
   ```

6. Open your browser and go to `http://127.0.0.1:8000/`

## Local Server (Optional)
For serving static files in production:
```bash
python manage.py collectstatic
```
