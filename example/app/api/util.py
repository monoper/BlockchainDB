"""Utility functions"""

import json
import uuid
import os
from datetime import datetime
from pycognito import Cognito
from fastapi import Depends, HTTPException
from fastapi.security.http import HTTPBearer, HTTPBasicCredentials
from .common_models import AppointmentStatus, Provinces, Appointment, \
                            Address, Name, PhoneNumbers, ProvidableTreatment, \
                             PrescribedTreatment, Notes
from .provider_models import Provider
from .client_models import Client, LinkedProvider

auth = HTTPBearer()

async def verify_auth_header(authorization: HTTPBasicCredentials = Depends(auth)):
    """
    Verifies the credentials sent in the authorisation header with cognito
    """
    try:
        aws_cognito = Cognito(os.environ['USER_POOL_ID'],
                                os.environ['USER_POOL_WEB_CLIENT_ID'],
                                access_token=authorization.credentials)
        if aws_cognito.get_user() is None:
            raise HTTPException(status_code=403)

        return authorization.credentials
    except Exception as forbidden:
        raise HTTPException(status_code=403) from forbidden


class HelperEncoder(json.JSONEncoder):
    """
    Helper for JSON decoding of classes
    """
    def default(self, o):
        if isinstance(o, uuid.UUID):
            return str(o)

        if isinstance(o, datetime):
            return o.isoformat()

        if isinstance(o, Provinces):
            return o.value

        if isinstance(o, AppointmentStatus):
            return o.value

        if isinstance(o,
                     (Address,
                        Appointment,
                        Client,
                        Name,
                        PhoneNumbers,
                        ProvidableTreatment,
                        Provider,
                        LinkedProvider, 
                        PrescribedTreatment, 
                        Notes)):
            return o.__dict__

        return json.JSONEncoder.default(self, o)
