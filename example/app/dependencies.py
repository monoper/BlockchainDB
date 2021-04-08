"""Dependency injection configuration"""

from injector import singleton
from .api.blockchain import BlockchainDb


def configure_dependencies(binder):
    """Service configurations"""
    binder.bind(BlockchainDb, to=BlockchainDb, scope=singleton)
