# Bibilary

Welcome to the Bibilary! This repository contains a Flask application for Library Management System.

## Getting Started

Follow these steps to set up and run the Flask application locally:

### Prerequisites

- [Python](https://www.python.org/) installed on your machine (version 3.6 or higher).

### Clone the Repository

```bash
git clone https://github.com/matrixmang0/Bibilary.git

cd Bibilary
```

### Create a Virtual Environment

#### On Windows
```bash
python -m venv venv
```

#### On macOS/Linux
```bash
python3 -m venv venv
```

### Activate the Virtual Environment

#### On Windows

```bash
venv\Scripts\activate
```

#### On macOS/Linux

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the Flask Application

### Set the Flask app environment variable

#### On Windows

```bash
set FLASK_APP=app
```

#### On macOS/Linux
```bash
export FLASK_APP=app
```

### Enable development mode for live-reloading

#### On Windows
```bash
set FLASK_ENV=development
```

#### On macOS/Linux
```bash
export FLASK_ENV=development
```

### Run the Flask app

```bash
flask run
```

Visit http://localhost:5000 in your web browser to see the running application.
