from typing import Union

import boto3
import botocore

from src.env import DATA_LAKE_BUCKET


class Bucket:
	def __init__(self):
		self.__s3 = boto3.client('s3')

	def contains(self, key: str) -> bool:
		try:
			self.__s3.head_object(Bucket=DATA_LAKE_BUCKET, Key=key)
		except botocore.exceptions.ClientError as e:
			if e.response['Error']['Code'] == '404':
				return False
			raise e
		return True

	def put(self, key: str, content: Union[str, bytes]) -> None:
		self.__s3.put_object(Bucket=DATA_LAKE_BUCKET, Key=key, Body=content)
