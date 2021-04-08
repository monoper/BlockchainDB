from pydantic import BaseModel, ValidationError, EmailStr, validator
from typing import List
from datetime import datetime
import random
import asyncio
import json
import requests
import logging
import uuid
from enum import Enum


class Provinces(Enum):
    Ontario = 0
    Manitoba = 1
    Quebec = 2
    Newfoundland = 3
    Saskatchewan = 4
    PrinceEdwardIsland = 5
    BritishColumbia = 6
    NovaScotia = 7
    Yukon = 8
    NorthwestTerritories = 9
    Nunavut = 10
    NewBrunswick = 11


class Name(BaseModel):
    firstName: str
    middleName: str
    lastName: str


class PhoneNumbers(BaseModel):
    mobile: str
    home: str
    work: str

class ProvidableTreatment(BaseModel):
    name: str
    description: str

class Address(BaseModel):
    unit: str
    streetAddress: str
    city: str
    province: Provinces 
    country: str
    postalCode: str

    @validator('country')
    def country_must_be_canada(cls, v):
        if v.lower() != 'canada':
            raise ValueError("Only Canada is supported as a country.")
        return v


class Appointment(BaseModel):
    appointmentId: str = str(uuid.uuid4())
    clientId: str
    providerId: str
    reasonForAppointment: str
    address: Address
    date: datetime
    status: int 
    attended: bool
    cancellationReason: str

class RegisterProvider(BaseModel):
    username: str
    password: str
    name: Name
    phoneNumbers: PhoneNumbers
    addresses: List[Address]
    dateOfBirth: datetime
    email: EmailStr
    providableTreatments: List[ProvidableTreatment]


class HelperEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, uuid.UUID):
            return str(o)
        
        if isinstance(o, datetime):
            return o.isoformat()

        if isinstance(o, Provinces):
            return o.value

        return json.JSONEncoder.default(self, o)

def build_provider():
    name = get_name()

    number_of_addresses = random.randint(1, 5)
    number_of_providable_treatments = random.randint(1, 7)

    address = []
    providableTreatments = []

    for i in range(0, random.randint(1, 7)):
        address.append(get_address())

    for i in range(0, random.randint(1, 7)):
        providable_treatment = get_providable_treatments()
        treatment_exists = False

        for providableTreatment in providableTreatments:
            if providableTreatment.name == providable_treatment.name:
                treatment_exists = True

        if not treatment_exists:
            providableTreatments.append(providable_treatment)

    phone_numbers = get_phone_numbers()
    email = get_email(name)

    return RegisterProvider(**{
        'username': email,
        'password': 'Password!@3',
        'name': name,
        'phoneNumbers': phone_numbers,
        'addresses': address,
        'dateOfBirth': datetime(1950 + random.randint(0, 40), random.randint(1, 12), random.randint(1, 28)), 
        'providableTreatments':providableTreatments,
        'email':email
    })

def get_phone_numbers():
    return PhoneNumbers(**{
        'mobile': '1234567890',
        'work': '1234567890',
        'home': '1234567890'
    })

def get_email(name: Name):
    return f'{name.firstName}.{name.lastName}@monoper.io'


def get_name():
    first_names = ['john', 'sally', 'kate', 'samina', 'anne', 'will', 'catherine', 'ayla', 'kayla', 'katrina', 'rebecca', 'robert', 'sam', 'eric', 'greg']
    last_names = ['smythe', 'smith', 'johnson', 'wali', 'erikson', 'takamora', 'harper', 'miller', 'jones', 'davis', 'garcia']

    first_name = first_names[random.randint(0, len(first_names)-1)]
    middle_name = first_names[random.randint(0, len(first_names)-1)]
    last_name = last_names[random.randint(0, len(last_names)-1)]

    return Name(**{'firstName':first_name, 'middleName': middle_name, 'lastName': last_name})


def get_address():
    cities = ['toronto', 'vancouver', 'montreal', 'winnipeg', 'halifax', 'london', 'paris', 'huntsville']
    street_addresses = ['main', 'yonge', 'queen', 'dundas', 'lord', 'red', 'blue', 'ontario', 'durham']
    street_suffixes = ['street', 'avenue', 'boulevard', 'circle']

    unit = random.randint(0, 99)
    city = cities[random.randint(0, len(cities)-1)]
    street_address = street_addresses[random.randint(0, len(street_addresses)-1)]
    street_suffix = street_suffixes[random.randint(0, len(street_suffixes)-1)]
    postal_code = 'l1l1w2'

    return Address(**{
        'unit': unit,
        'streetAddress': f'{street_address} {street_suffix}',
        'city': city,
        'province': random.randint(0, 11),
        'country': 'canada',
        'postalCode': postal_code
    })


def get_providable_treatments():
    treatment_names = ['back massage', 'skin cleanse', 'general check up', 'blood testing', 'MRI scan', 'CT scan', 'cancer screening']

    treatment_name = treatment_names[random.randint(0, len(treatment_names)-1)]

    return ProvidableTreatment(**{
        'name': treatment_name,
        'description': treatment_name
    })


def create_provider():
    url = 'https://api.dev.blockmedisolutions.com/api/auth/register-provider'
    print(f'Using url: {url}')

    data = build_provider()

    json_data = json.dumps(data.dict(), cls=HelperEncoder)

    print(json_data)
    print(data.json())
    resp = requests.post(url, data=data.json())
    print(resp)
    print(resp.content)

if __name__ == "__main__":
    create_provider()
