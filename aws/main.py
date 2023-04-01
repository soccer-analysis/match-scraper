from aws_cdk import Stack, App, Duration
from aws_cdk.aws_events import Rule, Schedule
from aws_cdk.aws_events_targets import LambdaFunction
from aws_cdk.aws_lambda_event_sources import SqsEventSource
from aws_cdk.aws_sqs import Queue
from constructs import Construct
from shared_infrastructure import create_function, get_stack_output
from shared_infrastructure.function import Allow


class MatchScraperStack(Stack):
	def __init__(self, scope: Construct):
		super().__init__(scope, 'soccer-analysis-match-scraper')
		match_id_queue = Queue(self, 'match-id-queue', retention_period=Duration.days(1),
							   visibility_timeout=Duration.minutes(15), receive_message_wait_time=Duration.seconds(20))

		bucket_name = get_stack_output('soccer-analysis-shared-infrastructure', 'bucket')
		bucket_arn = get_stack_output('soccer-analysis-shared-infrastructure', 'bucket-arn')

		create_function(
			self,
			name='backfill-match-ids',
			cmd='src.backfill_match_ids.lambda_handler',
			env={
				'BUCKET': bucket_name,
				'MATCH_ID_QUEUE_URL': match_id_queue.queue_url
			},
			memory_size=1024,
			reserved_concurrent_executions=1,
			allows=[
				Allow(
					actions=['s3:GetObject', 's3:ListBucket'],
					resources=[bucket_arn, f'{bucket_arn}/*']
				),
				Allow(
					actions=['sqs:SendMessage'],
					resources=[match_id_queue.queue_arn]
				)
			]
		)

		scrape_current_match_ids = LambdaFunction(create_function(
			self,
			name='scrape-current-match-ids',
			cmd='src.scrape_current_match_ids.lambda_handler',
			env={
				'BUCKET': bucket_name,
				'MATCH_ID_QUEUE_URL': match_id_queue.queue_url
			},
			memory_size=512,
			reserved_concurrent_executions=1,
			allows=[
				Allow(
					actions=['s3:GetObject', 's3:ListBucket'],
					resources=[bucket_arn, f'{bucket_arn}/*']
				),
				Allow(
					actions=['sqs:SendMessage'],
					resources=[match_id_queue.queue_arn]
				)
			]
		))

		Rule(self, 'twice-daily', schedule=Schedule.cron(hour='1,18', minute='0')) \
			.add_target(scrape_current_match_ids)

		scrape_match = create_function(
			self,
			name='scrape-match',
			cmd='src.scrape_match.lambda_handler',
			env={
				'BUCKET': bucket_name
			},
			memory_size=512,
			reserved_concurrent_executions=100,
			allows=[
				Allow(
					actions=['s3:PutObject'],
					resources=[f'{bucket_arn}/*']
				)
			]
		)
		scrape_match.add_event_source(SqsEventSource(match_id_queue, batch_size=1))


if __name__ == '__main__':
	app = App()
	MatchScraperStack(app)
	app.synth()
