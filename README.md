# FastPool Backend

A Django-based backend service for the FastPool application.

## Prerequisites

- Python 3.x
- PostgreSQL
- pip

## Setup

<span style="color: red; font-weight: bold;">Note:</span> <span style="font-weight: bold;">Please follow the instructions carefully.</span>

1. Clone the repository

```bash
git clone <repository-url> fastpool-be
cd fastpool-be
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Configure environment variables
   Create a `.env` file in the root directory with the following variables:

```
NAME=your_db_name
USER=your_db_user
PASSWORD=your_db_password
HOST=your_db_host
PORT=your_db_port
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

4. Run migrations

```bash
python manage.py migrate
```

5. Start the development server

```bash
python manage.py runserver
```

## API Documentation

[To be added]

## Contributing

[To be added]

## License

[To be added]
