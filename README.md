# Static website Generator

This project transforms articles written in Markdown into a static html website.
You can use it in two different modes:
1. Just generate html and save it
2. Watch the changes in your templates and css files and automatically re-generate website (very convinient for developing).


## Usage
1. Install requirements `pip install -r requirements.txt`
2. Run `python sitegen.py` to create your website.
3. **[Optional]** Run `python sitegen.py watch` to start a livereload server. You can access your website at http://127.0.0.1:5500
 and every time you save changes in your template or css file website will be generated again so you won't need to do it manually to see the changes.


# Project Goals

The code is written for educational purposes. Training course for web-developers - [DEVMAN.org](https://devman.org)
