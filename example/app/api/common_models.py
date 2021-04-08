"""Models that are shared between providers, clients and appointments"""
from typing import List
import datetime
from enum import Enum
from pydantic import BaseModel, validator

class ProvidableTreatment(BaseModel):
    """Model for Providable Treatment"""
    providableTreatmentId: str = str('')
    name: str
    description: str

class AppointmentStatus(Enum):
    """Enum model for an appointment status"""
    Pending = 0
    Accepted = 1
    Rejected = 2
    Completed = 3
    InProgress = 4

class Provinces(Enum):
    """Enum model for an province"""
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
    """Model for Name"""
    firstName: str
    middleName: str
    lastName: str


class PhoneNumbers(BaseModel):
    """Model for Providable Treatment"""
    mobile: str
    home: str
    work: str


class Address(BaseModel):
    """Model for Address"""
    addressId: str = str('')
    unit: str
    streetAddress: str
    city: str
    province: Provinces
    country: str
    postalCode: str

    @validator('country')
    def country_must_be_canada(cls, value):
        if value.lower() != 'canada':
            raise ValueError("Only Canada is supported as a country.")
        return value


class PrescribedTreatment(ProvidableTreatment):
    treatmentFrequency: str
    startDate: datetime.datetime
    endDate: datetime.datetime


class Notes(BaseModel):
    noteId: str = str('')
    createdDate: datetime.datetime
    note: str


class Appointment(BaseModel):
    """Model for Appointment"""
    appointmentId: str = str('')
    clientId: str
    providerId: str
    reasonForAppointment: str
    address: Address
    date: datetime.datetime
    status: AppointmentStatus = AppointmentStatus.Pending
    attended: bool
    cancellationReason: str = str('')
    requestedTreatments: List[ProvidableTreatment]
    prescribedTreatments: List[PrescribedTreatment] = []
    notes: List[Notes] = []
