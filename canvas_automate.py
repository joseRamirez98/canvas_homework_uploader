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

def main():
    class_name, assignment, file_name = get_argvs()
    file_path = find_file_path(file_name)
    navigate_canvas(class_name, assignment, file_path)
    return

def get_argvs():
    return sys.argv[1], sys.argv[2], sys.argv[3]

# Look for the file requested by the user. If found, return the full
# directory path to the file.
def find_file_path(file_name):
    file_paths = []
    for root, dirs, files in os.walk('/Users/Jose/'):
        if file_name in files:
            return os.path.join(root,file_name)
    return None

# This function should call over functions to sign into canvas,
# and upload the assignment file. Also, the webdriver should be
# created and closed within this function.
def navigate_canvas(class_name, assignment, file_to_upload):
    #option = webdriver.ChromeOptions()
    #option.add_argument('headless')
    with webdriver.Chrome() as driver:
        driver.get('https://csus.instructure.com/courses')
        driver = sign_into_canvas(driver)
        driver = find_class_in_canvas(driver, class_name)
        driver = find_assignment(driver, assignment)
        driver = submit_assignment(driver, file_to_upload)
        time.sleep(5)
    return       

# Sign into canvas using the username and password provided by the user.
def sign_into_canvas(driver):
    name_input_elem_xpath = '/html/body/div/div/div/div/div/div/div/form/div[1]/div/input'
    pass_input_elem_xpath = '/html/body/div/div/div/div/div/div/div/form/div[2]/div/input'
    username = input('Enter username: ')
    password = getpass.getpass('Enter password: ')
    elem = driver.find_element_by_xpath(name_input_elem_xpath)
    elem.clear()
    elem.send_keys(username)
    elem = driver.find_element_by_xpath(pass_input_elem_xpath)
    elem.clear()
    elem.send_keys(password)
    elem.send_keys(Keys.RETURN)
    return driver

# Once signed into Canvas, find the class entered by the user. If the class is found
# click the the class link to go to the class home page.
def find_class_in_canvas(driver, class_name):
    webTableElem = driver.find_element_by_xpath('//*[@id="my_courses_table"]')
    numOfRows = len(webTableElem.find_elements_by_xpath("//tr"))
    numOfColumns = len(webTableElem.find_elements_by_xpath("//tr[2]/td"))
    classes = []
    class_name = class_name.upper()
    for i in range(1, numOfRows):
        course_name = webTableElem.find_element_by_xpath("//tr["+str(i)+"]/td[2]").text
        if class_name in course_name:
            webTableElem.find_element_by_xpath("//tr["+str(i)+"]/td[2]").click()
            return driver
    return driver

# Navigate from the home page of the class to the assignments tab. When on the
# assignments home page, look for the assignment name provided by the user.
def find_assignment(driver, assignment):
    #look for the assignemnts section tab. if found, click on the anchor element
    section_tabs = driver.find_elements_by_class_name("section")
    li_index = 1
    for tab in section_tabs:
        text = tab.text
        text = text.lower()
        text = text.replace(' ', '')
        if 'assignments' in  text:
            driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[2]/div[2]/nav/ul/li["+str(li_index)+"]/a").click()
            break
        li_index += 1
    
    elems = WebDriverWait(driver,10).until(lambda driver: driver.find_elements_by_class_name('ig-title'))
    
    for elem in  elems:
        assignment_name = elem.text
        assignment_name = assignment_name.lower()
        assignment_name = assignment_name.replace(' ', '')
        assignment = assignment.lower()
        if assignment in assignment_name:
            elem.click()
            break
    return driver
    
# Once on the page submit page of the assignment, upload the file to sumbit for the assignment.
def submit_assignment(driver, file_path):
    submit_button = WebDriverWait(driver,10).until(lambda driver: driver.find_element_by_xpath('//*[@id="assignment_show"]/div[1]/div[2]/a'))
    submit_button.click()
    upload_element = WebDriverWait(driver,10).until(lambda driver: driver.find_element_by_name('attachments[0][uploaded_data]'))
    print(file_path)
    upload_element.send_keys(file_path)
    submit_button = driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[2]/div[3]/div[1]/div/div[2]/div/form/table/tbody/tr[5]/td/button[2]")
    submit_button.submit()
    return driver

main()