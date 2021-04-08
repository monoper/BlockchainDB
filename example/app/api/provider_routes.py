"""Routes for provider api"""
import uuid
from typing import Optional
from fastapi import Depends, APIRouter, status
from fastapi.exceptions import HTTPException
from .provider_models import Provider, ProviderSearchResult
from .common_models import Appointment, Provinces, ProvidableTreatment, AppointmentStatus, Address
from .blockchain import BlockchainDb
from .util import verify_auth_header
from .client_models import Client, LinkedProvider

api = APIRouter(
    prefix="/api/provider",
    tags=["providers"],
    dependencies=[Depends(BlockchainDb),Depends(verify_auth_header)],
    responses={404: {"description": "Not found"}},
)

@api.get("/{provider_id}", response_model=Provider, status_code=status.HTTP_200_OK)
def get_provider(provider_id: str, database: BlockchainDb = Depends()):
    """Returns a single provider"""
    result = database.find_one('Provider', {'providerId': provider_id})

    if result is None:
        raise HTTPException(status_code=404, detail='Provider not found')

    return Provider(**result)

@api.put("/{provider_id}", status_code=status.HTTP_200_OK)
def update_provider(provider_id: str, provider: Provider, database: BlockchainDb = Depends()):
    """Updates a provider"""
    if provider.providerId != provider_id:
        raise HTTPException(status_code=400,
                            detail='Provider id in query parameter doesn\'t match payload')

    database.commit_transaction(provider, 'EDIT', 'Provider', 'providerId', provider_id)

@api.get("/{provider_id}/providable-treatments", status_code=status.HTTP_200_OK)
def get_provider_providable_treatments(provider_id: str, database: BlockchainDb = Depends()):
    """Gets the treatments a provider can provide to a client"""
    result = database.find_one('Provider', {'providerId': provider_id})

    if result is None:
        raise HTTPException(status_code=404, detail='Provider not found')

    return Provider(**result).providableTreatments

@api.post("/{provider_id}/providable-treatments", status_code=status.HTTP_200_OK)
def add_provider_providable_treatment(provider_id: str, providableTreatment: ProvidableTreatment,
                                        database: BlockchainDb = Depends()):
    """Adds a treatments that a provider can provide to a client"""
    result = database.find_one('Provider', {'providerId': provider_id})

    if result is None:
        raise HTTPException(status_code=404, detail='Provider not found')

    provider = Provider(**result)

    for existing_providable_treatment in provider.providableTreatments:
        if existing_providable_treatment.name.lower() == providableTreatment.name.lower():
            raise HTTPException(status_code=400,
                                detail=f'Providable treatment: \
                                        {providableTreatment.name} already exists')

    providableTreatment.providableTreatmentId = str(uuid.uuid4())
    provider.providableTreatments.append(providableTreatment)

    database.commit_transaction(provider, 'EDIT', 'Provider', 'providerId', provider_id)

@api.post("/{provider_id}/address", status_code=status.HTTP_200_OK)
def add_provider_address(provider_id: str, address: Address,
                                        database: BlockchainDb = Depends()):
    """
    Adds provider address
    """
    result = database.find_one('Provider', {'providerId': provider_id})

    if result is None:
        raise HTTPException(status_code=404, detail='Provider not found')

    provider = Provider(**result)
    address.addressId = str(uuid.uuid4())
    provider.addresses.append(address)

    database.commit_transaction(provider, 'EDIT', 'Provider', 'providerId', provider_id)

@api.delete("/{provider_id}/providable-treatments/{providable_treatment_id}", status_code=status.HTTP_200_OK)
def delete_provider_providable_treatment(provider_id: str,
                                        providable_treatment_id: str,
                                        database: BlockchainDb = Depends()):
    """Adds a treatments that a provider can provide to a client"""
    result = database.find_one('Provider', {'providerId': provider_id})

    if result is None:
        raise HTTPException(status_code=404, detail='Provider not found')

    provider = Provider(**result)

    providable_treatments = []

    for existing_providable_treatment in provider.providableTreatments:
        if existing_providable_treatment.providableTreatmentId != providable_treatment_id:
            providable_treatments.append(existing_providable_treatment)

    provider.providableTreatments = providable_treatments

    database.commit_transaction(provider, 'EDIT', 'Provider', 'providerId', provider_id)

@api.delete("/{provider_id}/address/{address_id}", status_code=status.HTTP_200_OK)
def delete_provider_address(provider_id: str,
                                        address_id: str,
                                        database: BlockchainDb = Depends()):
    """
    Removes an address from a provider
    """
    result = database.find_one('Provider', {'providerId': provider_id})

    if result is None:
        raise HTTPException(status_code=404, detail='Provider not found')

    provider = Provider(**result)

    addresses = []

    for existing_address in provider.addresses:
        if existing_address.addressId != address_id:
            addresses.append(existing_address)

    provider.addresses = addresses

    database.commit_transaction(provider, 'EDIT', 'Provider', 'providerId', provider_id)

@api.get("/{provider_id}/appointments", status_code=status.HTTP_200_OK)
def get_provider_appointments(provider_id: str, database: BlockchainDb = Depends()):
    """Gets appointments that are assigned to a provider"""
    result = database.find('Appointment', {'providerId': provider_id})

    if result is None:
        return {}

    return result

@api.get("/{provider_id}/appointments/{appointment_id}", status_code=status.HTTP_200_OK)
def get_provider_appointment(provider_id: str, appointment_id: str,
                                database: BlockchainDb = Depends()):
    """Gets a single appoint that is assigned to a provider"""
    result = database.find_one('Appointment',
                            {'providerId': provider_id, 'appointmentId': appointment_id})

    if result is None:
        raise HTTPException(status_code=404, detail='Appointment not found')

    return result

@api.put("/{provider_id}/appointments/{appointment_id}/accept", status_code=status.HTTP_200_OK)
def accept_provider_appointment(provider_id: str,
                                appointment_id: str,
                                database: BlockchainDb = Depends()):
    """Accepts an appointment that is assigned to a provider"""
    appointment = database.find_one('Appointment',
                              {'providerId': provider_id, 'appointmentId': appointment_id})

    if appointment is None:
        raise HTTPException(status_code=404, detail='Appointment not found')
    
    updated_appointment = Appointment(**appointment)

    updated_appointment.status = AppointmentStatus.Accepted

    #need to add protect so that only 1 create block can exist for a given ID
    result = database.commit_transaction(updated_appointment, 'EDIT',
                                    'Appointment', 'appointmentId', appointment_id)

    return result

@api.put("/{provider_id}/appointments/{appointment_id}/reject", status_code=status.HTTP_200_OK)
def reject_provider_appointment(provider_id: str,
                                appointment_id: str,
                                database: BlockchainDb = Depends()):
    """Rejects an appointment that is assigned to a provider"""
    appointment = database.find_one('Appointment',
                                {'providerId': provider_id, 'appointmentId': appointment_id})

    if appointment is None:
        raise HTTPException(status_code=404, detail='Appointment not found')

    updated_appointment = Appointment(**appointment)

    updated_appointment.status = AppointmentStatus.Rejected

    #need to add protect so that only 1 create block can exist for a given ID
    result = database.commit_transaction(updated_appointment, 'EDIT',
                                    'Appointment', 'appointmentId', appointment_id)

    return result

@api.put("/{provider_id}/appointments/{appointment_id}", status_code=status.HTTP_200_OK)
def update_provider_appointment(provider_id: str,
                                appointment_id: str,
                                appointment: Appointment,
                                database: BlockchainDb = Depends()):
    if appointment.providerId != provider_id or appointment.appointmentId != appointment_id:
        raise HTTPException(status_code=400,
                            detail='Provider id in query parameter doesn\'t match payload')

    existing_appointment = Appointment(**database.find_one('Appointment',
                            {'providerId': provider_id, 'appointmentId': appointment_id}))

    if existing_appointment.status == AppointmentStatus.Completed \
        or existing_appointment.status == AppointmentStatus.Rejected:
        raise HTTPException(status_code=400,
                            detail='Cannot update a completed or rejected appointment')

    #need to add protect so that only 1 create block can exist for a given ID
    result = database.commit_transaction(appointment, 'EDIT',
                                    'Appointment', 'appointmentId', appointment_id)

    related_client_result = database.find_one('Client', { 'clientId': appointment.clientId})

    if related_client_result is None:
        raise HTTPException(status_code=404, detail='Client related to appointment not found')

    related_client = Client(**related_client_result)

    if not any(linked_provider.providerId == appointment.providerId
                for linked_provider in related_client.linkedProviders):
        raise HTTPException(status_code=403)
    
    if result is None:
        raise HTTPException(status_code=404, detail='Appointment not found')

    return result

@api.get("/search/available", status_code=status.HTTP_200_OK)
def search_provider(name: Optional[str]=None, city: Optional[str]=None,
                    province: Optional[Provinces]=None, database: BlockchainDb = Depends()):
    """Searches for a provider based on nothing, a name, a city or a province"""
    query = {}

    if name is not None:
        name_query = { "name.firstName": { '$regex' : f'^{name}'} }
        query = {**name_query}
#
    if city is not None:
        city_query = { "address.city": { '$regex' : f'^{city}'} }
        query = {**query, **city_query}

    if province is not None:
        province_query = { "address.province": province }
        query = {**query, **province_query}

    raw_results = database.find('Provider', query)

    results = []

    for raw_result in raw_results:
        results.append(ProviderSearchResult(**raw_result))

    return results
