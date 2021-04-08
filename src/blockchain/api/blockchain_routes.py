"""Routes that are related to the actual blockchain"""

from fastapi import Depends, APIRouter, status
from ..blockchain import Blockchain as BlockchainDb
from ..models import ProposedBlock

api = APIRouter(
    prefix="/api/blockchain",
    tags=["blockchain"],
    dependencies=[Depends(BlockchainDb)],
    responses={404: {"description": "Not found"}},
)

@api.get("/health")
def get_client(database: BlockchainDb = Depends()):
    """Endpoint to validate the blockchain as a whole"""
    return 200 if database.validate() else 400

@api.post("/validate-block", status_code=status.HTTP_200_OK)
def update_client(proposed_block: ProposedBlock, database: BlockchainDb = Depends()):
    """Endpoint to validate a single block"""
    return database.get_proposed_block_hash(proposed_block)
