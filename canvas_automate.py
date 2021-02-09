import os
import sys
import getpass
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.common.exceptions import StaleElementReferenceException

# The main function runs the entire program.
# In the main function, the objective is to
# retieve the file a user wishes to submit,
# then pass the file path to the navigate_canvas
# function to turn in the file.
def main():
    class_name, assignment, file_name = get_argvs()     
    file_path = find_file_path(file_name)
    navigate_canvas(class_name, assignment, file_path)
    return

# Return the agruments included from the commmand line.
# First argument should be the class name, for example CSC133.
# Second argument should be assignment name based off Canvas, for example Homework 1.
# Last argument should be the file itself, for example project1.java.
def get_argvs():
    return sys.argv[1], sys.argv[2], sys.argv[3]

# Look for the file requested by the user. If found, return the
# directory path to the file, otherwise return nothing.
def find_file_path(file_name):
    file_paths = []
    for root, dirs, files in os.walk('/Users/Jose/'):
        if file_name in files:
            return os.path.join(root,file_name)
    return None

# The functions emmulates the process of submitting and
# uploading an assignment onto Canvas. The process goes a follows:
# Sign into Canvas -> Navigate to class -> Navigate to assignment
# submission page -> Submit assgnment.
# The Google Chrome webdriver is to be created as well.
# The function does not return anything.
def navigate_canvas(class_name, assignment, file_to_upload):
    #option = webdriver.ChromeOptions()
    #option.add_argument('headless')
    with webdriver.Chrome() as driver:
        driver.get('https://csus.instructure.com/courses')
        driver = sign_into_canvas(driver)
        driver = find_class_in_canvas(driver, class_name)
        driver = find_assignment(driver, assignment)
        driver = submit_assignment(driver, file_to_upload)
        #wait for the webpage to confirm the assignment was submitted.
        time.sleep(5)
    return       

# Sign into canvas using the username and password provided by the user.
# First find the path to the HTML tags for the username and passowrd.
# Then submit the users credentials to the respective tags. Last simulate
# the clicking of the enter button and return the webdriver.
def sign_into_canvas(driver):
    #static paths to the name and password HTML input elements
    name_input_elem_xpath = '/html/body/div/div/div/div/div/div/div/form/div[1]/div/input'
    pass_input_elem_xpath = '/html/body/div/div/div/div/div/div/div/form/div[2]/div/input'
    username = input('Enter username: ')
    password = getpass.getpass('Enter password: ')
    #submit username to input tag
    elem = driver.find_element_by_xpath(name_input_elem_xpath)
    elem.clear()
    elem.send_keys(username)
    #submit password to input tag
    elem = driver.find_element_by_xpath(pass_input_elem_xpath)
    elem.clear()
    elem.send_keys(password)
    elem.send_keys(Keys.RETURN)
    return driver

# Webscrap the current web page in order to retrieve HTML table containing
# the user's classes. Retrieve the number of rows and columns as well.
# If the class is found, navigate the webdriver to the class home page 
# otherwise keep the webdriver on current page.
def find_class_in_canvas(driver, class_name):
     #retrieve the HTML webtable containing the user's classes
    webTableElem = driver.find_element_by_xpath('//*[@id="my_courses_table"]')
    numOfRows = len(webTableElem.find_elements_by_xpath("//tr"))
    numOfColumns = len(webTableElem.find_elements_by_xpath("//tr[2]/td"))
    classes = []
    class_name = class_name.upper()
    for i in range(1, numOfRows):
        #get class name from the web table and store it in a variable
        course_name = webTableElem.find_element_by_xpath("//tr["+str(i)+"]/td[2]").text 
        if class_name in course_name:
            #simulates a user clicking on a class, which navigates to class home page.
            webTableElem.find_element_by_xpath("//tr["+str(i)+"]/td[2]").click() 
            return driver
    return driver

# Navigates to the class home page. Class home page contains course navigation links
# to things such as assignments, discussions, grades, files etc. Find the assignments
# navigation link. Once on the assignments page, find the assignment the user wishes
# submit and navigate to the assignment submission page.
# Function returns the webdriver.
def find_assignment(driver, assignment):
    #locate the HTML list element containing all course navigation links
    section_tabs = driver.find_elements_by_class_name("section")
    #index of the first item in list
    li_index = 1
    for tab in section_tabs:
        text = tab.text
        text = text.lower()
        text = text.replace(' ', '')
        if 'assignments' in  text:
            # assignment navigation link found, navigate to assignments page
            driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[2]/div[2]/nav/ul/li["+str(li_index)+"]/a").click()
            break
        li_index += 1
    
    # waits for all assignments to finish loading onto webpage, then retrieves the array of assignments
    elems = WebDriverWait(driver,10).until(lambda driver: driver.find_elements_by_class_name('ig-title'))
    
    #find assignment to submit in the array. if found navigate to assignemtn submission page
    for elem in  elems:
        assignment_name = elem.text
        assignment_name = assignment_name.lower()
        assignment_name = assignment_name.replace(' ', '')
        assignment = assignment.lower()
        if assignment in assignment_name:
            elem.click()
            break
    return driver
    
# Once on the assignment submission page, upload the file to HTML input tag and submit.
# Return the webdriver.
def submit_assignment(driver, file_path):
    #prepare the web page to submit the user's assignment by clicking "Submit Assignment" button.
    submit_button = WebDriverWait(driver,10).until(lambda driver: driver.find_element_by_xpath('//*[@id="assignment_show"]/div[1]/div[2]/a'))
    submit_button.click()
    #find the HTML input tag in order to upload necessary file.
    upload_element = WebDriverWait(driver,10).until(lambda driver: driver.find_element_by_name('attachments[0][uploaded_data]'))
    upload_element.send_keys(file_path)
    #simulate the user clicking submit on the web page.
    submit_button = driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[2]/div[3]/div[1]/div/div[2]/div/form/table/tbody/tr[5]/td/button[2]")
    submit_button.submit()
    return driver

#Execute the program
main()
