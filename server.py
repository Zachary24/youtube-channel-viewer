import time
from math import ceil
import os
import glob
import urllib.request, urllib.parse, urllib.error
from flask import Flask, render_template, url_for
from jinja2.exceptions import TemplateNotFound
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
app = Flask(__name__)
filesList = []
@app.route('/')
def index():
    try:
        for (path, folders, files) in os.walk('templates'):
            files = [file.replace('videos_', '').replace('.html', '') for file in files]
            filePaths = [int(file) for file in files if file.isdigit()]
        filesList.clear()
        filesList.extend(filePaths)
        filesList.sort()
        return render_template('videos_0.html', filesList=filesList)
    except TemplateNotFound:
        return '''
        <link href="https://fonts.googleapis.com/css?family=Source+Sans+Pro" rel="stylesheet">
        <style>
        body {
            background-color: #131313;
            color: white;
            font-family: Source Sans Pro;
            font-size: 15px;
        }
        </style>
        <p>please scrape a channel/playlist before trying to view !</p>'''
@app.route('/scrape/<id>')
def scrape(id):
    deletefiles = glob.glob(os.path.join('templates/', "*.html"))
    for f in deletefiles:
        os.remove(f)
    iteration = 0
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome('driver/chromedriver', options=chrome_options)
    driver.get('https://www.youtube.com/playlist?list=%s&disable_polymer=true' % (id))
    while True:
        try:
            loadmore = driver.find_element_by_class_name('load-more-button')
            driver.execute_script("arguments[0].scrollIntoView();", loadmore)
            time.sleep(2)
            loadmore.click()
            time.sleep(2)
            iteration += 1
            print('iteration: #',iteration)
        except (NoSuchElementException, StaleElementReferenceException):
            try:
                loadmore = driver.find_element_by_class_name('load-more-button')
            except (NoSuchElementException, StaleElementReferenceException):
                print('not visisble')
                titles = driver.find_elements_by_class_name('pl-video')
                size = len(titles)
                parts = size/200
                parts = ceil(parts)
                for part in range(parts):
                    print('page: [%s:%s]' % (part, parts))
                    with open('templates/videos_%s.html' % (part), 'w', encoding="utf8", errors='ignore') as f:
                        f.write('''
                        <div class="page"><div class="content">
                        <link href="https://fonts.googleapis.com/css?family=Source+Sans+Pro" rel="stylesheet">
                        <link rel="stylesheet" type="text/css" href="{{ url_for("static", filename="main.css") }}">''')
                        for title in titles[part*200:part*200+200]:
                            f.write(title.get_attribute('outerHTML').replace('/watch?', 'https://youtube.com/watch?').replace('data-thumb', 'src').replace('src="/yts/img/pixel-vfl3z5WfW.gif"','').replace('<td>', '<div>').replace('</td>', '</div>').replace('<td', '<div').replace('<tr>', '<div>').replace('</tr>', '</div>').replace('<tr', '<div').replace('sqp=-',''))
                        for (path, folders, files) in os.walk('templates'):
                            files = [file.replace('videos_', '').replace('.html', '') for file in files]
                            filePaths = [int(file) for file in files if file.isdigit()]
                        filesList.clear()
                        filesList.extend(filePaths)
                        filesList.sort()
                        f.write('''
                        </div>
                        <div class="footer">
                        {% for file in filesList %}
                        <a class="pageid" href='/serve/videos_{{file}}.html'>{{file}}</a>
                        {% endfor %}
                        </div>
                        </div>
                        ''')
                driver.quit()
                return render_template('videos_0.html', filesList=filesList)
@app.route('/serve/<filename>')
def serve(filename):
    for (path, folders, files) in os.walk('templates'):
        files = [file.replace('videos_', '').replace('.html', '') for file in files]
        filePaths = [int(file) for file in files if file.isdigit()]
    filesList.clear()
    filesList.extend(filePaths)
    filesList.sort()
    return render_template(filename, filesList=filesList)
if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5030)
