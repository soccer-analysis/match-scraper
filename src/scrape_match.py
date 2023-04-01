import gzip

import boto3
import ujson
from typing import Dict, Any

import json5

from unidecode import unidecode

from src.bucket import Bucket
from src.web_driver import Driver


def scrape_match(match_id: str) -> None:
	print(f'Scraping: {match_id}')
	driver = Driver()
	bucket = Bucket()
	key = 'raw/%s.json.gzip' % match_id
	driver.get('https://whoscored.com/Matches/%s/Live' % match_id).wait().remove_popups()
	raw = driver.page_source \
		.split('require.config.params["args"] = ')[-1] \
		.split('</script>')[0] \
		.replace(';', '') \
		.strip()
	data = json5.loads(unidecode(raw))
	if (data['matchCentreData'] or {}).get('elapsed') != 'FT':
		return
	league_link = driver.find_element('//div[@id="breadcrumb-nav"]//a')
	data['league_id'] = int(league_link.get_attribute('href').lower().split('/tournaments/')[-1].split('/')[0])
	data['season'] = int(league_link.text.split('-')[-1].split('/')[0])
	compressed = gzip.compress(ujson.dumps(data).encode())
	bucket.put(key, compressed)


def lambda_handler(event: Dict = None, context: Any = None) -> None:
	sqs = boto3.client('sqs')
	for record in event.get('Records', []):
		[account, queue_name] = record['eventSourceARN'].split(':')[-2:]
		queue_url = sqs.get_queue_url(QueueName=queue_name, QueueOwnerAWSAccountId=account)['QueueUrl']
		try:
			scrape_match(record['body'])
		except Exception as e:
			raise e
		finally:
			sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=record['receiptHandle'])


if __name__ == '__main__':
	scrape_match('1640742')
