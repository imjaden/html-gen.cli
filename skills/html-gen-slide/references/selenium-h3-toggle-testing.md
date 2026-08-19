# Selenium Testing for Slide Template

## H3 Toggle Visibility Test

Test `.toc-h3` hidden by default and toggleable via the H3 switch:

```python
class TestH3Toggle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        opts = Options()
        opts.add_argument('--headless')
        opts.add_argument('--no-sandbox')
        svc = Service(CHROMEDRIVER_PATH)
        cls.driver = webdriver.Chrome(service=svc, options=opts)

    def setUp(self):
        # CRITICAL: headless Chrome defaults to 800×600 which triggers
        # @media (max-width: 768px) → sidebar hidden → elements not interactable
        self.driver.set_window_size(1280, 800)
        self.driver.get('file://' + str(DEMO_HTML))

    def test_h3_hidden_by_default(self):
        h3s = self.driver.find_elements(By.CSS_SELECTOR, '.toc-h3')
        for h3 in h3s:
            self.assertEqual(h3.value_of_css_property('display'), 'none')

    def test_h3_toggle_visible(self):
        toggle = self.driver.find_element(By.ID, 'h3Toggle')
        toggle.click()
        h3s = self.driver.find_elements(By.CSS_SELECTOR, '.toc-h3')
        for h3 in h3s:
            self.assertNotEqual(h3.value_of_css_property('display'), 'none')

    def test_h3_toggle_hidden_again(self):
        toggle = self.driver.find_element(By.ID, 'h3Toggle')
        toggle.click(); time.sleep(0.15)  # show
        toggle.click(); time.sleep(0.15)  # hide
        h3s = self.driver.find_elements(By.CSS_SELECTOR, '.toc-h3')
        for h3 in h3s:
            self.assertEqual(h3.value_of_css_property('display'), 'none')
```

## CSS Specificity Debugging

When `display: none` doesn't work despite correct CSS:

1. Check if a higher-specificity rule overrides it (e.g. `.slide-toc a { display: block }` beats `.toc-h3 { display: none }`)
2. Use DevTools → Computed Styles to see which rule wins
3. Fix: match or exceed specificity (e.g. `.slide-toc .toc-h3 { display: none }`)
