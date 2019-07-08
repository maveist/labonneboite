"""
Test search using isochrone filters: car.
"""

import time
import re
import urllib.parse

from parameterized import parameterized
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from labonneboite.common.maps.constants import ISOCHRONE_DURATIONS_MINUTES
from .base import LbbSeleniumTestCase


DURATIONS = [(duration, ) for duration in ISOCHRONE_DURATIONS_MINUTES]


class TestSearchSelectingCar(LbbSeleniumTestCase):

    def setUp(self):
        super().setUp()
        url = self.url_for(
            'search.entreprises',
            l='Metz+57050',
            occupation='comptabilite',
            tr='car',
            lat='49.119146',
            lon='6.176026'
        )
        self.driver.get(url)

        # Click on the Memo button.
        memo_button = WebDriverWait(self.driver, 20)\
            .until(
                EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "J'ai compris"))
            )
        memo_button.click()

        # Wait until the Memo overlay is invisible.
        WebDriverWait(self.driver, 20)\
            .until(
                EC.invisibility_of_element_located((By.XPATH, "//div[@class='introjs-overlay']"))
            )

        # Accept RGPD, otherwise selecting isochrone filters is not possible. ¯\_(ツ)_/¯
        self.driver.find_element_by_xpath("//button[@class='rgpd-accept']").click()


    @parameterized.expand(DURATIONS)
    def test_isochrone_search(self, duration):
        """
        Test an isochrone search selecting "car" and "{duration} minutes".
        """

        # Store current results
        results_sentence = self.driver.find_element_by_css_selector('h1.lbb-result-info').text
        primitive_results = re.match(r'(\d+)', results_sentence).group()

        # Click on "min"
        self.driver.find_element_by_css_selector('.switch-element[data-switch-value="duration"]')\
            .click()

        # Travel modes should be visible now
        car_button = self.driver.find_element_by_css_selector(
            '.travelmode-choices a.visible[data-travelmode="car"]'
        )
        self.assertTrue(car_button.is_displayed())

        # Filtering by duration should be available now
        durations_options = self.driver.find_element_by_css_selector('#isochrone-durations')
        self.assertTrue(durations_options.is_displayed())

        # click on another duration
        durations_options.find_element_by_css_selector(f'input[value="{duration}"]').click()

        # The page should reload with a new search.
        time.sleep(1)

        # Assert the selected duration and its mode are part of the url.
        current_url = self.driver.current_url
        url = urllib.parse.urlparse(current_url)
        parameters = dict(urllib.parse.parse_qsl(url.query))

        self.assertEqual(parameters['tr'], 'car')
        self.assertEqual(parameters['dur'], str(duration))

        results_sentence = self.driver.find_element_by_css_selector('h1.lbb-result-info').text
        last_results = re.match(r'(\d+)', results_sentence).group()

        # We should have less results filtering with 15 minutes than in 10km.
        self.assertLessEqual(last_results, primitive_results)


    # test duration
