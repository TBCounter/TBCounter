# TBCounter

Selenium chests parser for totalbattle

## DEV Requirements

- python 3.9
- [tesserractOCR](https://github.com/tesseract-ocr/tesseract)

## Launch once 

- create venv `python -m venv venv`
- activate venv `source venv/bin/activate` or `venv\Scripts\activate`
- install requirements `pip install -r requirements.txt`
- edit robot.py **main** finction, change login and password (hashed by HS256)
- add [selenium webdriver](https://chromedriver.chromium.org/downloads) for your google chrome version
- launch robot.py `python robot.py`

## Launch webserver

### Frontend

#### requirements:

- node js
- nginx or apache

#### launch:

- install nginx or apache
- configure nginx (or apache) for vue-router history mode (redirect every request to /)
- `yarn install` in `/front` directory
- `yarn build`
- move `/front/dist` folder to apache or nginx working directory

### Backend

#### requirements:

- all steps in **Launch once** paragraph
- uvicorn
- postgresql
- alembic

#### launch:

- create `.env` file using `.env.template` 
- edit `main.py` main function
- run `python main.py`
database should be created automatically
- migrate database `alembic upgrade head`

### support


support me [on patreon](https://patreon.com/Omega394) or [boosty](https://boosty.to/omega_soft)
