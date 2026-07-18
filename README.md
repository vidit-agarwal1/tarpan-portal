# Tarpan Foundation Portal

A web-based beneficiary management system for the Tarpan Foundation.

## Tech Stack
- Python 3.14
- Django 5.2
- PostgreSQL (via Supabase)

Setup Instructions

1. Clone the repository
git clone <repo-url>
cd tarpan-portal

2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # on Windows: venv\Scripts\activate

3. Install dependencies
pip install -r requirements.txt

4. Create a .env file in the project root
See the .env.example file for required variables.

5. Run migrations
python manage.py migrate

6. Create admin accounts
python manage.py shell
>>> from accounts.models import AdminAccount
>>> a = AdminAccount(username='yourusername')
>>> a.set_password('yourpassword')
>>> a.save()
>>> exit()

7. Run the development server
python manage.py runserver
