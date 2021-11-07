![Badge](https://img.shields.io/static/v1?label=LANGUAGE%20USED&message=PYTHON&labelColor=505050&color=3776AB&style=for-the-badge&logoWidth=20&logoColor=3776AB&logo=python)
![Badge](https://img.shields.io/static/v1?label=USES&message=DJANGO&labelColor=505050&color=092E20&style=for-the-badge&logoWidth=20&logoColor=092E20&logo=django)
![Badge](https://img.shields.io/static/v1?label=Created%20By&message=Paudom&labelColor=505050&color=F5B047&style=for-the-badge&logoWidth=20&logoColor=F5B047&logo=adafruit)
![Badge](https://img.shields.io/static/v1?label=Version&message=1.5.0&labelColor=505050&color=43AA8B&style=for-the-badge&logoWith=20&logoColor=43AA8B&logo=addthis)

# ChessRepertoire
Welcome to Chess Repertoire, an interactive webpage to review and practice your own chess repertoire. 

It allows you to record your chess repertoire digitally including openings and variations.

## Setup and Installation
You have two options:

- **Released Versions**: Donwload the released versions and follow those intructions.

- **Normal Installation**: Follow the next steps to install by your own.

### Normal Installation

Python is a must. The dependency libraries are specified in the `requirements.txt`

To install `Chess Repertoire` the following steps are encouraged:

1. Start a virtual environment:
```bash
virtualenv ${environment_name}
```

2. Activate the virtualenv and install all dependencies
```bash
source ${environment_name}/bin/activate
pip install -r requirements.txt
```

## Start Chess Repertoire
1. Start Database
```bash
cd chess_repertoire
python3 manage.py makemigrations
python3 manage.py migrate
```

2. Create super user
```bash
python3 manage.py createsuperuser
```
This way you can delete openings and variations accessing as a superuser using `/admin`

3. Start Webpage
```
python3 manage.py runserver
```
This will start a webpage at: `http://127.0.0.1/8000`

## How it works
At the start the Database will be empty, so you will need to add new openings. To add Openings click the button `New Opening` at the end of the home page.

Once added you will be able to modify it, see it's information, go to their variations, but never delete. This way it's impossible to lose your opening repertoire. 

As before, at first no variations are recorded in the Database. To add them, click `New Variation`. When adding variations, there are two important inputs.

1. **PGN FILE**: you need to add pgn files containing all the moves you want to review/practice.

2.  **IMAGE FILE**: I recomend you to upload an image of the starting position of the variation. This image can be obtained using `chess.com/analysis` when downloading pgn, there's the image option.

As Openings you can modify, review and practice them but not delete them.

> In the case you need to remove openings or variations, you can go to: http://127.0.0.1/8000/admin. A super user account will be required to access to the admin site. There you can access to all Openings and Variations and remove the ones you do not want.
