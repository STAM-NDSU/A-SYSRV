# A-SYSRV


## Getting Started

To run the project, python should be installed on your machine.
Check if it is installed or not using

```
python --version
```

If it is not installed, download and install python from https://www.python.org/downloads/


Then, setup virtual environment (optional)

```
python3 -m venv venv
source venv/bin/activate
```

Then, install the requirements:

```
pip install -r requirements.txt
```

Then, create a .env file and copy contents from .env.example in the project root:

```
mv .env.example .env
```

Then, run the application:

```
flask run --debug  --port 5001
```

