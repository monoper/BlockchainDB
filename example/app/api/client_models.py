from typing import List
from datetime import datetime
from pydantic import BaseModel, EmailStr
from .common_models import Address, Name, PhoneNumbers


class LinkedProvider(BaseModel):
    providerId: str
    providerName: str
    hasAccess: bool


class Client(BaseModel):
    clientId: str
    name: Name
    phoneNumbers: PhoneNumbers
    address: Address
    dateOfBirth: datetime
    email: EmailStr
    linkedProviders: List[LinkedProvider] = []
