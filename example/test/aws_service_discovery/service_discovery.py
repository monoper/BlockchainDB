import boto3
import json

client = boto3.client('servicediscovery')

services = client.list_services()

for service in services['Services']:
    print(service)
    instances = client.list_instances(
        ServiceId=service['Id'],
        MaxResults=100
    )

    for instance in instances['Instances']:
        print(instance['Attributes']['AWS_INSTANCE_IPV4'])
        print(instance['Attributes']['AWS_INSTANCE_IPV4'])