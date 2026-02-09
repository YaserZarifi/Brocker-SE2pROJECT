"""
Management command to deploy the TransactionLedger smart contract.

Usage:
    python manage.py deploy_contract

Prerequisites:
    1. Compile the contract:  cd contracts && npx hardhat compile
    2. Start Hardhat node:    cd contracts && npx hardhat node
"""

from django.core.management.base import BaseCommand, CommandError

from blockchain_service.service import BlockchainService


class Command(BaseCommand):
    help = "Deploy the TransactionLedger smart contract to the local Hardhat network"

    def handle(self, *args, **options):
        self.stdout.write("Deploying TransactionLedger contract...")

        service = BlockchainService()
        address = service.deploy_contract()

        if address:
            self.stdout.write(
                self.style.SUCCESS(f"Contract deployed successfully at: {address}")
            )
            self.stdout.write(
                "Contract address saved to blockchain_service/contract_address.json"
            )
        else:
            raise CommandError(
                "Failed to deploy contract. Ensure:\n"
                "  1. Hardhat node is running (cd contracts && npx hardhat node)\n"
                "  2. Contract is compiled (cd contracts && npx hardhat compile)\n"
                "  3. BLOCKCHAIN_ENABLED=True in settings"
            )
