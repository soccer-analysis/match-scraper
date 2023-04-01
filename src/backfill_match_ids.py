import boto3
from typing import Dict, Any
from tqdm import tqdm

from src.env import MATCH_ID_QUEUE_URL
from src.bucket import Bucket
from src.scrape_util import region_tournaments, enqueue_match_ids
from src.web_driver import Driver


def lambda_handler(event: Dict = None, context: Any = None) -> None:
	bucket = Bucket()
	queue = boto3.resource('sqs').Queue(MATCH_ID_QUEUE_URL)
	driver = Driver()
	for region, tournament in tqdm(region_tournaments):
		driver.get('https://www.whoscored.com/Regions/%s/Tournaments/%s' % (region, tournament)).wait() \
			.remove_popups()
		while True:
			enqueue_match_ids(driver, bucket, queue)
			previous_day_button = driver.find_element('//a[contains(@class, "previous")]')
			is_disabled = 'is-disabled' in previous_day_button.get_attribute('class')
			if is_disabled:
				break
			previous_day_button.click()
			driver.wait()


if __name__ == '__main__':
	lambda_handler()
