from datetime import datetime
import pytz
import boto3
import os

# define your AWS region  
region = os.environ['AWS_REGION']

# define our CloudEvents client
client = boto3.client('events')

# Configure the current time in GMT and convert it to local time (US Central)
utc_time = datetime.utcnow().replace(tzinfo=pytz.utc)
# Set your timezone here!
cst_timezone = pytz.timezone('US/Central')
cst_time = utc_time.astimezone(cst_timezone)

# This will show the offset in seconds for DST ⏰
# If it's zero, we're not in DST
is_dst = cst_time.tzinfo._dst.seconds != 0

# Set your new cron expressions for the needed schedule adjusted for DST
if is_dst:
  cron_schedule = 'cron(0 12 ? * * *)'

else:
  cron_schedule = 'cron(0 13 ? * * *)'

# Set the name of your AWS Event rules here
CRON_DST_RULE = "CRON RULE NAME HERE"

# Fetch the targets of our current cron rules
cron_dst_settings = client.list_targets_by_rule(Rule=CRON_DST_RULE)

# Remove targets from current rules
client.remove_targets(
  Rule=CRON_DST_RULE,
  Ids=[(cron_dst_settings['Targets'][0]['Id'])]
)

# Delete rules
client.delete_rule(Name=CRON_DST_RULE)

# Add new rules
client.put_rule(
  Name=CRON_DST_RULE,
  ScheduleExpression=cron_schedule,
  State='ENABLED',
  Description="Automatic trigger for the function."
)

# Add back our targets
client.put_targets(
  Rule=CRON_DST_RULE,
  Targets=[
    {
      'Id': cron_dst_settings['Targets'][0]['Id'],
      'Arn':cron_dst_settings['Targets'][0]['Arn'],
      'Input': cron_dst_settings['Targets'][0]['Input']
    }
  ]
)
