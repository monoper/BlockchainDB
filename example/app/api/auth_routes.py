import os
import uuid
from pycognito import Cognito
from fastapi import APIRouter, Depends, status
from .blockchain import BlockchainDb
from .client_models import Client
from .provider_models import Provider
from .util import verify_auth_header
from .auth_models import RegisterClient, RegisterProvider, SignIn, ConfirmSignUp, \
                         ChangePassword, ConfirmForgotPassword, ForgotPassword, Token, \
                         User, SignInResponse


api = APIRouter(
    prefix="/api/auth",
    tags=["authentication"],
    dependencies=[Depends(BlockchainDb)],
    responses={404: {"description": "Not found"}},
)

@api.get('/verify-token',
            status_code=status.HTTP_200_OK,
            dependencies=[Depends(verify_auth_header)])
def verify_token():
    pass


@api.post('/register-client', response_model=str, status_code=status.HTTP_200_OK)
def register_client(client: RegisterClient, database: BlockchainDb = Depends()):
    aws_cognito = Cognito(os.environ['USER_POOL_ID'], os.environ['USER_POOL_WEB_CLIENT_ID'])

    aws_cognito.username = client.username
    aws_cognito.set_base_attributes(email=client.username, name=f'{client.name.firstName}')
    aws_cognito.add_custom_attributes(usertype='client')
    response = aws_cognito.register(client.username, client.password)

    client.address.addressId = uuid.uuid4()

    database.commit_transaction(Client(clientId=response['UserSub'],
                            name=client.name,
                            phoneNumbers=client.phoneNumbers,
                            address=client.address,
                            dateOfBirth=client.dateOfBirth,
                            email=client.email).dict(),
                            'CREATE', 'Client', 'clientId', response['UserSub'])
    return response['UserSub']

@api.post('/register-provider', response_model=str, status_code=status.HTTP_200_OK)
def register_provider(provider: RegisterProvider, database: BlockchainDb = Depends()):
    aws_cognito = Cognito(os.environ['USER_POOL_ID'], os.environ['USER_POOL_WEB_CLIENT_ID'])

    aws_cognito.username = provider.username
    aws_cognito.set_base_attributes(email=provider.username, name=f'{provider.name.firstName}')
    aws_cognito.add_custom_attributes(usertype='provider')    
    response = aws_cognito.register(provider.username, provider.password)

    for providable_treatment in provider.providableTreatments:
        providable_treatment.providableTreatmentId = uuid.uuid4()

    for address in provider.addresses:
        address.addressId = uuid.uuid4()
    try:
        database.commit_transaction(Provider(providerId=response['UserSub'],
                                name=provider.name,
                                phoneNumbers=provider.phoneNumbers,
                                addresses=provider.addresses,
                                dateOfBirth=provider.dateOfBirth,
                                email=provider.email,
                                providableTreatments=provider.providableTreatments).dict(),
                                'CREATE', 'Provider', 'providerId', response['UserSub'])
        return response['UserSub']
    except:
        aws_cognito.delete_user()
        return status.HTTP_400_BAD_REQUEST

@api.post("/sign-in", response_model=SignInResponse, status_code=status.HTTP_200_OK)
def sign_in(user_sign_in: SignIn):
    aws_cognito = Cognito(os.environ['USER_POOL_ID'], os.environ['USER_POOL_WEB_CLIENT_ID'])
    aws_cognito.username = user_sign_in.username
    aws_cognito.authenticate(password=user_sign_in.password)
    user = aws_cognito.get_user(attr_map={"usertype": "custom:usertype","user_id":"sub"})
    usertype = user._data["custom:usertype"]
    user_id = user.sub
    resp = {"user": User(userId=user_id, username=user.username, usertype=usertype), "token":Token(**aws_cognito.__dict__)}
    return SignInResponse(**resp)

@api.post("/confirm-registration", status_code=status.HTTP_200_OK)
def confirm_registration(confirm_sign_up: ConfirmSignUp):
    aws_cognito = Cognito(os.environ['USER_POOL_ID'], os.environ['USER_POOL_WEB_CLIENT_ID'])
    aws_cognito.confirm_sign_up(confirm_sign_up.verificationCode, username=confirm_sign_up.username)

@api.post("/sign-out", status_code=status.HTTP_200_OK)
def sign_out(token: str = Depends(verify_auth_header)):
    aws_cognito = Cognito(os.environ['USER_POOL_ID'],
                                os.environ['USER_POOL_WEB_CLIENT_ID'],
                                access_token=token)
    aws_cognito.logout()

@api.post("/change-password", status_code=status.HTTP_200_OK)
def change_password(user_change_password: ChangePassword, token: str = Depends(verify_auth_header)):
    aws_cognito = Cognito(os.environ['USER_POOL_ID'],
                                os.environ['USER_POOL_WEB_CLIENT_ID'],
                                access_token=token)
    aws_cognito.change_password(user_change_password.old_password, user_change_password.new_password)

@api.post("/forgot-password", status_code=status.HTTP_200_OK)
def forgot_password(user_forgot_password: ForgotPassword):
    aws_cognito = Cognito(os.environ['USER_POOL_ID'],
                            os.environ['USER_POOL_WEB_CLIENT_ID'])

    aws_cognito.username = user_forgot_password.username
    aws_cognito.add_custom_attributes(email=user_forgot_password.username)

    aws_cognito.initiate_forgot_password()

@api.post("/confirm-forgot-password", status_code=status.HTTP_200_OK)
def confirm_forgot_password(user_confirm_forgot_password: ConfirmForgotPassword):
    aws_cognito = Cognito(os.environ['USER_POOL_ID'],
                            os.environ['USER_POOL_WEB_CLIENT_ID'])

    aws_cognito.username = user_confirm_forgot_password.username
    aws_cognito.add_custom_attributes(email=user_confirm_forgot_password.username)

    aws_cognito.confirm_forgot_password(user_confirm_forgot_password.verification_code,
                                        user_confirm_forgot_password.new_password)
