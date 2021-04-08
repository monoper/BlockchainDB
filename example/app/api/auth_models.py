"""
Models that are used during the authentication process and
for adding new clients/providers
"""

from typing import List
from datetime import datetime
from pydantic import BaseModel, EmailStr
from .common_models import Address, Name, PhoneNumbers
from .provider_models import ProvidableTreatment


class RegisterClient(BaseModel):
    """
    Model for client registration
    """
    username: str
    password: str
    name: Name
    phoneNumbers: PhoneNumbers
    address: Address
    dateOfBirth: datetime
    email: EmailStr


class RegisterProvider(BaseModel):
    """
    Model for provider registration
    """
    username: str
    password: str
    name: Name
    phoneNumbers: PhoneNumbers
    addresses: List[Address]
    dateOfBirth: datetime
    email: EmailStr
    providableTreatments: List[ProvidableTreatment]


class SignIn(BaseModel):
    """
    Model for sign in
    """
    username: str
    password: str


class ConfirmSignUp(BaseModel):
    """
    Model for confirming sign up
    """
    username: str
    verificationCode: str


class ForgotPassword(BaseModel):
    """
    Model for forgot password
    """
    username: str


class ConfirmForgotPassword(BaseModel):
    """
    Model for confirming a client forgotten password
    """
    username: str
    verification_code: str
    new_password: str


class ChangePassword(BaseModel):
    """
    Model for changing a password
    """
    old_password: str
    new_password: str

class User(BaseModel):
    """
    Model for user
    """
    userId: str
    username: str
    usertype: str

class Token(BaseModel):
    """
    Model for auth token
    """
    id_token: str
    access_token: str
    refresh_token: str

class SignInResponse(BaseModel):
    """
    Model for sign in response
    """
    user: User
    token: Token
