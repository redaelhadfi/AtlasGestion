# Atlas Management - Setup Guide

## Prerequisites

- **Python**
- **Django Framework**
- **Bootstrap**
- **CSS**
- **JavaScript**

---

## 1. Installing Python

### Download Python:
1. Visit the official Python website: [https://www.python.org/downloads/](https://www.python.org/downloads/).
2. Download the latest version of Python.

### Install Python:
1. Ensure you select the option **"Add Python to PATH"** during installation.
2. Complete the installation by following the instructions.

### Verify Installation:
1. Open a terminal or command prompt and run:
   ```bash
   python --version
   ```
2. You should see the installed Python version.

---

## 2. Create and Activate a Virtual Environment

### Create the Virtual Environment:
1. Navigate to the directory where you want to create your project.
2. Run:
   ```bash
   python -m venv env
   ```
   This will create a virtual environment named `env`.

### Activate the Virtual Environment:
- **Windows**:
  ```bash
  env\Scripts\activate
  ```
- **macOS/Linux**:
  ```bash
  source env/bin/activate
  ```

You’ll notice the terminal prompt changes, indicating the virtual environment is active.

---

## 3. Install Django and Dependencies

### Install Django:
1. Ensure the virtual environment is active.
2. Run:
   ```bash
   pip install django
   ```

### Install Dependencies from `requirements.txt`:
```bash
pip install -r requirements.txt
```

### Fixing Installation Errors:
1. If errors occur during installation, read the error messages in the console.
2. Install any missing libraries manually:
   ```bash
   pip install library_name
   ```

---

## 4. Configure the Database

### Local Database (SQL Server on Windows 10):
1. Configure your database settings in the project's files, such as in `settings.py`:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'mssql',
           'NAME': 'ddbbAtlasGestion1',
           'USER': 'sa',
           'PASSWORD': 'bddPassw',
           'HOST': 'AlanPC\\SQLEXPRESS',
           'PORT': '',
           'OPTIONS': {
               'driver': 'ODBC Driver 17 for SQL Server',
               'extra_params': 'TrustServerCertificate=yes;',
           },
       }
   }
   ```

### Optional: Test Database (PostgreSQL):
1. Update `settings.py` to use a test database:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'bbdd_atlas_gestion',
           'USER': 'ghotless',
           'PASSWORD': 'M0nst3r',
           'HOST': '64.23.159.80',
           'PORT': '5433',
       },
   }
   ```
2. Install the PostgreSQL driver:
   ```bash
   pip install psycopg2
   ```

---

## 5. Apply Migrations

### Apply Initial Migrations:
1. Run:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

### Create a Superuser:
1. Run:
   ```bash
   python manage.py createsuperuser
   ```
2. Provide a username, email, and password when prompted.

---

## 6. Start the Development Server

1. Run the server:
   ```bash
   python manage.py runserver
   ```
2. Access the project in your browser at: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 7. Optional: Configure Static Files

If using a different hosting setup or deploying to production:
1. Update `settings.py`:
   ```python
   STATIC_ROOT = BASE_DIR / 'staticfiles'
   ```
2. Collect static files:
   ```bash
   python manage.py collectstatic
   ```

---

## 8. Workflow in the Application

After running the project, follow these steps:

1. **Log in as an admin.**
2. **Create a Business.**
3. **Create a Staff User**:
   - Link the user to the created business.
   - Assign them manager permissions.
   - Ensure the user is marked as **Staff Manager**.
   - Log out of the admin account and log in with the new Staff Manager account.
4. **Create a Supplier.**
5. **Register a Product in Inventory**:
   - Products can have classifications such as **variable** or **clothing** (optional checkboxes).
   - For variable pricing, an additional boolean field `is_variable` is used to handle local pricing.
6. **Restock Inventory**:
   - Use the Purchase Records section to create a restock entry and update stock levels.
   - The form will require a registered supplier (step 4).

---

## 9. Sales Functionality

1. Once the setup is complete, you can process sales in two ways:
   - **Receipt (Boleta)**:
     - Uses the `price` and `discount` fields from the Product model.
   - **Invoice (Factura)**:
     - Uses the `wholesale_price` and `wholesale_discount` fields.

2. These processes are managed independently to avoid conflicts.
