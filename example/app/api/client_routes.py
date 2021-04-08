import uuid
from typing import List
from fastapi import Depends, APIRouter, status, HTTPException
from .client_models import Client, LinkedProvider
from .provider_models import Provider
from .common_models import Appointment, AppointmentStatus
from .blockchain import BlockchainDb
from .util import verify_auth_header


api = APIRouter(
    prefix="/api/client",
    tags=["clients"],
    dependencies=[Depends(BlockchainDb),Depends(verify_auth_header)],
    responses={404: {"description": "Not found"}},
)

@api.get("/{client_id}", response_model=Client, status_code=status.HTTP_200_OK)
def get_client(client_id: str, database: BlockchainDb = Depends()):
    result = database.find_one('Client', {'clientId': client_id})

    if result is None:
        raise HTTPException(status_code=404, detail='Client not found')

    return Client(**result)

@api.put("/{client_id}", status_code=status.HTTP_200_OK)
def update_client(client_id: str, client: Client, database: BlockchainDb = Depends()):
    if client.clientId != client_id:
        raise HTTPException(status_code=400,
                            detail='Client id in query parameter doesn\'t match payload')

    database.commit_transaction(client, 'EDIT', 'Client', 'clientId', client_id)

@api.get("/{client_id}/appointments",
            response_model=List[Appointment],
            status_code=status.HTTP_200_OK)
def get_client_appointments(client_id: str, database: BlockchainDb = Depends()):
    result = database.find('Appointment', {'clientId': client_id})

    if result is None:
        return []

    return result

@api.get("/{client_id}/appointments/{appointment_id}",
            response_model=Appointment,
            status_code=status.HTTP_200_OK)
def get_client_appointment(client_id: str, appointment_id: str, database: BlockchainDb = Depends()):
    result = database.find_one('Appointment',
                                {'clientId': client_id, 'appointmentId': appointment_id})

    if result is None:
        raise HTTPException(status_code=404, detail='Appointment not found')

    return result

@api.post("/{client_id}/appointments", status_code=status.HTTP_200_OK)
def add_client_appointment(client_id: str, appointment: Appointment,
                            database: BlockchainDb = Depends()):
    if appointment.clientId != client_id:
        raise HTTPException(status_code=400,
                            detail=f'Client id ({client_id}) in query \
                                    parameter doesn\'t match payload \
                                    ({appointment.clientId}) \
                                    {client_id == appointment.clientId}')
    #need to add protect so that only 1 create block can exist for a given ID
    appointment.appointmentId = str(uuid.uuid4())

    provider = Provider(**database.find_one('Provider', {'providerId': appointment.providerId}))
    client = Client(**database.find_one('Client', {'clientId': client_id}))

    if not any(linked_provider.providerId == provider.providerId
                for linked_provider in client.linkedProviders):
        client.linkedProviders.append(LinkedProvider(providerId=provider.providerId, 
            hasAccess=True,
            providerName=f'{provider.name.firstName} {provider.name.lastName}'))

    database.commit_transaction(client, 'EDIT', 'Client', 'clientId', client_id)

    database.commit_transaction(appointment, 'CREATE', 'Appointment',
                            'appointmentId', appointment.appointmentId)

@api.post("/{client_id}/linked-provider/{provider_id}/toggle", status_code=status.HTTP_200_OK)
def toggle_client_linked_provider(client_id: str, provider_id: str,
                            database: BlockchainDb = Depends()):

    client = Client(**database.find_one('Client', {'clientId': client_id}))

    for index, linked_provider in enumerate(client.linkedProviders):
        if linked_provider.providerId == provider_id:
            linked_provider.hasAccess = not linked_provider.hasAccess
            client.linkedProviders[index] = linked_provider

    database.commit_transaction(client, 'EDIT', 'Client', 'clientId', client_id)

@api.put("/{client_id}/appointments/{appointment_id}", status_code=status.HTTP_200_OK)
def update_client_appointment(client_id: str, appointment_id: str,
                                appointment: Appointment, database: BlockchainDb = Depends()):
    if appointment.clientId != client_id or appointment.appointmentId != appointment_id:
        raise HTTPException(status_code=400,
                            detail='Client id in query parameter doesn\'t match payload')

    if appointment.status == AppointmentStatus.Completed \
        or appointment.status == AppointmentStatus.Rejected:
        raise HTTPException(status_code=400,
                            detail='Cannot update a completed or rejected appointment')

    result = database.commit_transaction(appointment, 'EDIT',
                                    'Appointment', 'appointmentId', appointment_id)

    if result is None:
        raise HTTPException(status_code=400, detail='Could not update appointment')

    return result

@api.get("/{client_id}/prescribed-treatments", status_code=status.HTTP_200_OK)
def get_client_prescribed_treatments(client_id: str, database: BlockchainDb = Depends()):
    appointments = database.find('Appointment', { 'clientId' : client_id})

    if appointments is None:
        return []
    
    prescribed_treatments = []

    [prescribed_treatments.extend(appointment.prescribedTreatment) for appointment in appointments]

    return prescribed_treatments
