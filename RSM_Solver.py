from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from PIL import Image
import pix2tex
from pix2tex.cli import LatexOCR
from pix2tex import api
from pix2tex.api import app
import io
from latex2sympy2 import latex2sympy, latex2latex
import os
from sympy import sympify
import sympy

questionNum = 3
username = ['Insert your email/username here']
password = ['Insert your password here']

driver = webdriver.Chrome()

driver.get(f"https://homework.russianschool.com/StudentPortal/#/assignment/65331564?q={questionNum}")

time.sleep(2)

userField = driver.find_element("id", "username")
userField.send_keys(username)

passField = driver.find_element("id", "password")
passField.send_keys(password)

signinBtn = driver.find_element(By.CSS_SELECTOR,"input.gbutton.fl-right.btn-default.btn[value='Sign in']")
signinBtn.click()
time.sleep(5)

#questionElement = driver.find_element(By.ID, "problem-right-part question_text asset")
questionElement = driver.find_element(By.CSS_SELECTOR, '.problem-right-part.question_text.asset')
questionImg = questionElement.screenshot_as_png

with open("RSM-Homework-Doer-Bot-main/questionElement.png", "wb") as f:
    f.write(questionImg)

img = Image.open('RSM-Homework-Doer-Bot-main/questionElement.png')
model = LatexOCR()

latexForm = model(img)
print(latexForm)

sympyForm = latex2sympy(latexForm)
os.system('cls')
print(sympyForm)
print(latexForm)

equation = sympify(sympyForm)

# Calculate the result
result = sympy.N(equation, 10)

print(f"The result of {equation} is: {result}")

driver.quit()