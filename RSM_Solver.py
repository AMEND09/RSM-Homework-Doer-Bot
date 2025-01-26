from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
from PIL import Image
import io
import pix2tex
from pix2tex.cli import LatexOCR
from ollama import chat, ChatResponse

def initialize_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')
    return webdriver.Chrome(options=options)

def login_to_rsm(driver, username, password):
    driver.get("https://student.russianschool.com/student-portal/content/assignment/78119203")
    
    # Wait for login form
    wait = WebDriverWait(driver, 20)
    userField = wait.until(EC.presence_of_element_located((By.ID, "username")))
    userField.send_keys(username)
    
    passField = driver.find_element("id", "password")
    passField.send_keys(password)
    
    signinBtn = driver.find_element(By.CSS_SELECTOR, "#loginBtn")
    signinBtn.click()
    
    # Wait for login to complete
    time.sleep(5)

def get_question_image(driver, question_num):
    driver.get(f"https://student.russianschool.com/student-portal/content/assignment/78119203?problem={question_num}")
    
    # Wait for question to load with multiple possible selectors
    wait = WebDriverWait(driver, 20)
    try:
        questionElement = wait.until(EC.presence_of_element_located((
            By.CSS_SELECTOR, 
            '.assignment-question, .question-text, .problem-content, div[class*="question"]'
        )))
    except TimeoutException:
        # If not found, try to get the main content area
        questionElement = wait.until(EC.presence_of_element_located((
            By.CSS_SELECTOR, 
            '#content-wrapper, #main-content'
        )))
    
    # Ensure the element is in view
    driver.execute_script("arguments[0].scrollIntoView(true);", questionElement)
    time.sleep(2)  # Wait for any animations
    
    return questionElement.screenshot_as_png

def process_question(image_bytes):
    img = Image.open(io.BytesIO(image_bytes))
    model = LatexOCR()
    return model(img)

def extract_thinking(text):
    import re
    thinking = re.findall(r'<think>(.*?)</think>', text, flags=re.DOTALL)
    return '\n'.join(thinking).strip()

def clean_solution(text):
    import re
    # Remove content within <think> tags
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    
    # Fix common LaTeX formatting issues
    text = text.replace('$f(x$', '$f(x)$')
    text = text.replace('\\$', '$')
    text = re.sub(r'\[[\s\n]*\]', '', text)  # Remove empty brackets
    
    # Handle equations in square brackets
    text = re.sub(r'\[(.*?)\]', lambda m: '\n$$' + m.group(1).strip() + '$$\n', text, flags=re.DOTALL)
    
    # Handle inline math with better parentheses matching
    text = re.sub(r'\$([^$]+?)\$', lambda m: '$' + m.group(1).replace('\\$', '$').strip() + '$', text)
    
    # Clean up spaces around math delimiters
    text = re.sub(r'\s*\$\s*', '$', text)
    text = re.sub(r'\s*\$\$\s*', '$$', text)
    
    # Clean up any extra whitespace
    text = re.sub(r'\n\s*\n', '\n\n', text.strip())
    return text

def get_solution(latex_text):
    response: ChatResponse = chat(model='deepseek-r1:latest', messages=[
        {
            'role': 'user',
            'content': '''Solve the following math problem step by step. Format your response as follows:

1. Use LaTeX notation:
   - Enclose inline math in $...$
   - Put multi-line equations in [...]
   - Use proper LaTeX commands (\\frac, \\implies, etc.)
2. Put thinking in <think></think> tags
3. Number each step
4. Put each equation on its own line

Problem to solve: ''' + latex_text,
        },
    ])
    raw_text = response['message']['content']
    return clean_solution(raw_text), extract_thinking(raw_text)

def solve_problem(username, password, question_num):
    driver = initialize_driver()
    try:
        login_to_rsm(driver, username, password)
        question_img = get_question_image(driver, question_num)
        latex_form = process_question(question_img)
        solution, thinking = get_solution(latex_form)
        return latex_form, solution, thinking
    finally:
        driver.quit()

def solve_from_latex(latex_text):
    """Solve problem from direct LaTeX input"""
    solution, thinking = get_solution(latex_text)
    return latex_text, solution, thinking

def solve_from_image(image_bytes):
    """Solve problem from uploaded image"""
    latex_text = process_question(image_bytes)
    solution, thinking = get_solution(latex_text)
    return latex_text, solution, thinking
