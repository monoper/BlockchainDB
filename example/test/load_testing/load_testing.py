import asyncio
import json
import uuid

import requests

async def create_client_request():
    client_id = str(uuid.uuid4())
    url = 'http://localhost:5000/client/{}'.format(client_id)
    print('Using url: {}'.format(url))

    json_data = build_json_client_payload(client_id)

    resp = requests.post(url, json=json_data)

    for i in range(0, 500):
        await asyncio.gather(
            put_request(url, json_data),
            put_request(url, json_data),
            put_request(url, json_data),
            put_request(url, json_data),
            put_request(url, json_data),
            put_request(url, json_data),
            put_request(url, json_data),
            put_request(url, json_data),
            put_request(url, json_data),
            put_request(url, json_data),
            put_request(url, json_data)
        )

    print(resp)


def build_json_client_payload(client_id):
    data = '{"name":{"firstName":"W","middleName":"A","lastName":"H"},"phoneNumbers":{"home":"1234567890","mobile":"1234567890","work":"1234567890"},"address":{"unit":1,"streetAddress":"123 fake street","city":"Fake City","province":0,"country":"Canada","postalCode":"l1l1l1"},"dateOfBirth":"2021-01-29 23:50:58.272613","email":"a@a.com"}'
    json_data = json.loads(data)
    json_data['clientId'] = client_id

    return json_data


async def put_request(url, json_payload):
    resp = requests.put(url, json=json_payload)
    return resp.status_code


asyncio.run(create_client_request())

