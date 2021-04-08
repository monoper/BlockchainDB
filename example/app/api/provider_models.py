from typing import List
from datetime import datetime
from pydantic import BaseModel, EmailStr
from .common_models import Address, Name, PhoneNumbers, ProvidableTreatment

class Provider(BaseModel):
    """Model of a provider"""
    providerId: str
    name: Name
    phoneNumbers: PhoneNumbers
    addresses: List[Address]
    dateOfBirth: datetime
    email: EmailStr
    providableTreatments: List[ProvidableTreatment]

class ProviderSearchResult(BaseModel):
    """Result of a provider search"""
    providerId: str
    name: Name
    phoneNumbers: PhoneNumbers
    addresses: List[Address]
    providableTreatments: List[ProvidableTreatment]
