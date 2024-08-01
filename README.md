# API for SHOP

## HOW TO INSTALL:

1. **Create and activate virtualenv**
    - Open terminal in the folder where you have the `src` file.
    - Run: `python -m venv venv` (where `venv` is the name of the virtual environment folder).
    - Activate the virtual environment:
        - On Windows: `venv\Scripts\activate`
        - On macOS/Linux: `source venv/bin/activate`
        
2. **Navigate to `src` folder**
    - In terminal, go to the `src` folder: `cd src`

3. **Install requirements**
    - Run: `pip install -r requirements.txt`

4. **Create migrations**
    - Run: `python manage.py makemigrations`
    - Run: `python manage.py migrate`

5. **Run the server**
    - Run: `python manage.py runserver`

6. **Follow instructions in the terminal**
