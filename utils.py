from playwright.sync_api import sync_playwright, Locator
from constants import sample_line


class Field:
    def __init__(self,
                 handle: Locator,
                 label: str,
                 required: bool,
                 field_type: str,
                 options: list[Locator] = None
                 ):

        self.handle = handle
        self.label = label
        self.required = required
        self.field_type = field_type
        self.options = options


    def fill_field(self, value=None):
        if self.field_type == 'text':
            self.handle.locator('input, textarea').first.fill(value)

        elif self.field_type in ['radio', 'checkbox']:
            self.options[0].evaluate('(elem) => elem.click()')

        elif self.field_type == 'file':
            self.handle.locator('input').set_input_files(['dummy-pic.png'])

        elif self.field_type == 'select':
            self.handle.locator('select').select_option(index=2)



def get_field_obj(field: Locator) -> Field:
    label = field.locator('label .application-label').first.text_content().lower()
    required = True if field.locator('.required').first.all() else False

    if required:
        label = label[:-1]

    if field.locator('textarea').first.all():
        field_type = 'text'
    elif field.locator('select').first.all():
        field_type = 'select'
    else:
        field_type = field.locator('input').first.get_attribute('type')


    field_obj = None

    if field_type in ['text', 'file']:
        field_obj = Field(field, label, required, field_type)
    elif field_type == 'select':
        field_obj = Field(field, label, required, field_type)
    elif field_type in ['radio', 'checkbox']:
        options = field.locator('ul input').all()
        field_obj = Field(field, label, required, field_type, options)
    else:
        print('New field type', field_type)
        raise Exception('New field type.....')

    return field_obj



class FirefoxController:
    def __init__(self, user_data_dir, headless):
        self.p = sync_playwright().start()

        self.context = self.p.firefox.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=headless,
            no_viewport=True,
            args=["--start-maximized"]
        )

        self.page = self.context.pages[0]



    def go_to_job(self, url: str):
        self.page.goto(url)
        job_description = self.page.locator('[data-qa="job-description"]').text_content()

        if '/apply' not in url.lower():
            form_link = self.page.wait_for_selector('.postings-btn-wrapper a').get_attribute('href')
            self.page.goto(form_link)

        return job_description



    def upload_resume(self, info):
        self.page.set_input_files('#resume-upload-input', [info['resume']])



    def fill_basic_info(self, info):
        self.page.fill('[name="name"]', info['name'])
        self.page.fill('[name="email"]', info['email'])
        self.page.fill('[name="phone"]', info['phone'])
        self.page.fill('[name="org"]', info['company'])

    def fill_links(self, info: dict) -> None:
        links_heading_locator = self.page.locator('h4', has_text='links')
        links_form = self.page.locator('.application-form', has=links_heading_locator).first
        fields = links_form.locator('.application-question').all()

        field_objs = []
        for f1 in fields:
            field_obj = get_field_obj(f1)
            field_objs.append(field_obj)

        for f in field_objs:
            if 'linked' in f.label and 'linkedin_url' in info:
                f.handle.locator('input').first.fill(info['linkedin_url'])

            elif 'twitter' in f.label and 'twitter_url' in info:
                f.handle.locator('input').first.fill(info['twitter_url'])

            elif 'github' in f.label and 'github_url' in info:
                f.handle.locator('input').first.fill(info['github_url'])

            elif any([a in f.label for a in ['other', 'sample', 'blog', 'portfolio']]) and 'other_url' in info:
                f.handle.locator('input').first.fill(info['other_url'])
            else:
                f.handle.locator('input').first.fill('No URL')


    @staticmethod
    def fill_additional_form(additional_form: Locator):
        additional_fields = additional_form.locator('.application-question').all()

        additional_fields_obj = []
        for f in additional_fields:
            field_obj = get_field_obj(f)
            additional_fields_obj.append(field_obj)

        for f in additional_fields_obj:
            if f.required:
                f.fill_field(sample_line)


    def fill_additional_info(self, additional_info):
        self.page.fill('textarea[name="comments"]', additional_info)


    def submit_form(self):
        # click submit
        btn = self.page.query_selector('button#btn-submit')
        self.page.evaluate('(elem) => elem.click()', btn)

        # check if successfully submitted
        text = self.page.locator('[data-qa="msg-submit-success"]').text_content(timeout=50000)
        print(text)