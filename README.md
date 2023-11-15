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

## Results

Steps and screenshots of the working prototype:

1. Landing Screen where a user can click on **Choose a file** button to select fasta file containing sequences 
![UI](docs/readme/step1.png?raw=true "UI")
2. After clicking the **Choose a file** button, File explore window opens and user can proceed to select desired fasta file to provide as Input
![UI](docs/readme/step2.png?raw=true "File Select")
3. Fasta file is uploaded to the server and being processed to generate predictions for the provided sequences
![UI](docs/readme/step3.png?raw=true "Processing")
4. Finally, the analysis of the sequence is completed and a snippet of prediction is shown in the Table. User can click on the **Download Results** button to download overall prediction results in the *csv* format.
![UI](docs/readme/step4.png?raw=true "Dispaly")