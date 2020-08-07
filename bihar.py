#!/usr/bin/env python
# coding: utf-8

"""
!pip install selenium lxml
!pip install anticaptchaofficial
!pip install google-cloud-storage
"""

import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select

#from IPython.core.display import Image, display

from glob import glob


CHROMEDRIVER_PATH = '/opt/tools/webdriver/chromedriver'

LOCAL_PATH = '/opt/data/bihar-all/'
GCS_BUCKET = 'in-electoral-rolls-2020'
GCS_PATH = 'bihar/'

ANTI_CAPTCHA_API_KEY = '<<<<< PUT ANTI_CAPTCHA_API_KEY HERE >>>>>'
CAPTCHA_IMAGE_PATH = '/opt/data/bihar-all/captcha'
WRONG_CAPTCHA_IMAGE_PATH = '/opt/data/bihar-all/wrong-captcha'

GOOGLE_APPLICATION_CREDENTIALS = "/opt/credentials/in-electoral-rolls-1e1ef7e603c3.json"
GOOGLE_CLOUD_PROJECT = 'in-electoral-rolls'


from google.cloud import storage
import os

def upload_files_to_gcs():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS 
    storage_client = storage.Client()
    bucket = storage_client.bucket(GCS_BUCKET, user_project=GOOGLE_CLOUD_PROJECT)
    for fn in glob(os.path.join(LOCAL_PATH, '*.pdf')):
        try:
            bfn = os.path.basename(fn)
            blob = bucket.blob(os.path.join(GCS_PATH, bfn))
            print(fn, blob)
            blob.upload_from_filename(fn)
            os.unlink(fn)
        except Exception as e:
            print(e)

from anticaptchaofficial.antinetworking import *
from base64 import b64encode
from io import BytesIO

class MyImageCaptcha(antiNetworking):

    def solve_and_return_solution(self, file_obj, **kwargs):
        img_str = b64encode(file_obj.getbuffer()).decode('ascii')
        task_data = {
            "type": "ImageToTextTask",
            "body": img_str,
            "phrase": self.phrase,
            "case": self.case,
            "numeric": self.numeric,
            "math": self.math,
            "minLength": self.minLength,
            "maxLength": self.maxLength,
        }
        task_data.update(kwargs)
        if self.create_task({
            "clientKey": self.client_key,
            "task": task_data
        }) == 1:
            self.log("created task with id "+str(self.task_id))
        else:
            self.log("could not create task")
            self.log(self.err_string)
            return 0

        task_result = self.wait_for_result(60)
        if task_result == 0:
            return 0
        else:
            return task_result["solution"]["text"]
        
    def report_wrong_captcha(self):
        data = {"clientKey": self.client_key,
                "taskId": self.task_id
        }
        return self.make_request('reportIncorrectImageCaptcha', data)


solver = MyImageCaptcha()
solver.set_verbose(0)
solver.set_key(ANTI_CAPTCHA_API_KEY)

print("account balance: " + str(solver.get_balance()))


def create_webdriver():
    options = Options()

    options.add_experimental_option("prefs", {
        "download.default_directory": LOCAL_PATH,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
        })
    
    options.add_argument('headless')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('--remote-debugging-port=9222')

    driver = webdriver.Chrome(CHROMEDRIVER_PATH, options=options)

    return driver


def close_webdriver(driver):
    try:
        print('Closing current webdriver...')
        driver.close()
    except Exception as e:
        print(e)


### FIXME: Doesn't work in Headless mode
def get_downloaded_files(driver):
    if not driver.current_url.startswith("chrome://downloads"):
        driver.get("chrome://downloads/")
    
    return driver.execute_script(         "return  document.querySelector('downloads-manager')  "
        " .shadowRoot.querySelector('#downloadsList')         "
        " .items.filter(e => e.state === 'COMPLETE')          "
        " .map(e => { e.uploaded = true; return (e.filePath || e.file_path || e.fileUrl || e.file_url)});")

### FIXME: Doesn't work in Headless mode
def clear_downloaded_files(driver):
    if not driver.current_url.startswith("chrome://downloads"):
        driver.get("chrome://downloads/")

    driver.execute_script(         "document.querySelector('downloads-manager')      "
        " .shadowRoot.querySelectorAll('downloads-item')  "
        " .forEach(e => {if (e.data.uploaded) e.shadowRoot.getElementById('remove').click()})")


driver = create_webdriver()
driver.get('http://ele.bihar.gov.in/pdfsearch/')

try:
    assembly_segment_index = int(sys.argv[1])
except:
    assembly_segment_index = 0

try:
    last_part_no_index = int(sys.argv[2])
except:
    last_part_no_index = None

print('Start scraper...(segment=%d,part=%r)' % (assembly_segment_index, last_part_no_index))

n = 0
sel = Select(driver.find_element_by_xpath('//select[@id="DropDownList1"]'))
while assembly_segment_index < len(sel.options):
    try:
        sel.select_by_index(assembly_segment_index)
        sel2 = Select(driver.find_element_by_xpath('//select[@id="DropDownList2"]'))
        if last_part_no_index:
            part_no_index = last_part_no_index
        else:
            part_no_index = 0
        while part_no_index < len(sel2.options):
            sel2.select_by_index(part_no_index)
            rtype = driver.find_element_by_xpath('//input[@id="rb_0"]')
            rtype.click()
            refresh = driver.find_element_by_xpath('//input[@id="ImageButton2"]')
            refresh.click()
            msg = driver.find_element_by_xpath('//span[@id="lblMessage"]')
            driver.execute_script("arguments[0].innerText = ''", msg)
            img = driver.find_element_by_xpath('//img')
            fobj = BytesIO(img.screenshot_as_png)
            if False:
                src = img.get_attribute('src')
                img2 = Image(url=src)
                display(img2)
            if True:
                while True:
                    print("account balance: " + str(solver.get_balance()))
                    captcha_text = solver.solve_and_return_solution(fobj)
                    if captcha_text != 0:
                        print("captcha text "+captcha_text)
                        break
                    else:
                        print("task finished with error "+solver.error_code)
                        # TODO: error handling
                        if solver.error_code == 'ERROR_NO_SLOT_AVAILABLE':
                            time.sleep(15)
                        if solver.error_code == 'ERROR_ZERO_CAPTCHA_FILESIZE':
                            time.sleep(5)
            else:
                captcha_text = input()
                print(captcha_text)
            txt = driver.find_element_by_xpath('//input[@name="txtCaptcha"]')
            txt.clear()
            txt.send_keys(captcha_text)
            btn = driver.find_element_by_xpath('//input[@name="ImagshowMR"]')
            btn.click()
            msg = driver.find_element_by_xpath('//span[@id="lblMessage"]')
            print(msg.text)
            if msg.text.find('invalid') == -1:
                print('Save captcha...')
                #img.screenshot(CAPTCHA_IMAGE_PATH + ('/%s.png' % captcha_text))
                with open(CAPTCHA_IMAGE_PATH + ('/%s.png' % captcha_text), 'wb') as f:
                    f.write(fobj.getbuffer())
                n += 1
                part_no_index += 1
                #break
            else:
                print('Report Wrong Captcha...')
                #img.screenshot(WRONG_CAPTCHA_IMAGE_PATH + ('/%s.png' % captcha_text))
                with open(WRONG_CAPTCHA_IMAGE_PATH + ('/%s.png' % captcha_text), 'wb') as f:
                    f.write(fobj.getbuffer())
                solver.report_wrong_captcha()
                print('Retry...')
            sel2 = Select(driver.find_element_by_xpath('//select[@id="DropDownList2"]'))
        print(assembly_segment_index, part_no_index, n)
        #driver.get('http://ele.bihar.gov.in/pdfsearch/')
        upload_files_to_gcs()
        sel = Select(driver.find_element_by_xpath('//select[@id="DropDownList1"]'))
        assembly_segment_index += 1
        last_part_no_index = None
        #break
    except Exception as e:
        last_part_no_index = part_no_index
        print(e)
        print(assembly_segment_index, part_no_index, n)
        time.sleep(60)
        close_webdriver(driver)
        while True:
            try:
                print('Try to create new webdriver...')
                driver = create_webdriver()
                driver.get('http://ele.bihar.gov.in/pdfsearch/')
                sel = Select(driver.find_element_by_xpath('//select[@id="DropDownList1"]'))
                break
            except Exception as e:
                print(e)
                close_webdriver(driver)
                time.sleep(30)

print("account balance: " + str(solver.get_balance()))
time.sleep(60)
driver.close()
