from utils import FirefoxController
from constants import job_urls, headless
import json


with open('input.json', mode='r') as f:
    info = json.load(f)


url = job_urls[4]

con = FirefoxController('firefox-profile', headless)
page = con.page
page.goto(url)


# get job description
job_description = con.go_to_job(url)


con.upload_resume(info)
con.fill_basic_info(info)
con.fill_links(info)



additional_forms = page.locator('[data-qa="additional-cards"]').all()

for form in additional_forms:
    con.fill_additional_form(form)


con.submit_form()