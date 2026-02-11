"""
BourseChain Blockchain Service
Sprint 4 - Web3.py integration with Hardhat local network

Provides:
  - Connection to the local Hardhat Ethereum network (localhost:8545)
  - Deployment & interaction with the TransactionLedger smart contract
  - Recording matched stock transactions on-chain
  - Verification of on-chain transaction records

Architecture:
  - Singleton service with lazy initialization
  - Non-blocking: matching engine works even if blockchain is unavailable
  - Contract ABI read from Hardhat artifacts (contracts/artifacts/)
  - Deployed address stored in contract_address.json
"""

import json
import logging
import os
from pathlib import Path

from django.conf import settings

logger = logging.getLogger(__name__)

# Paths: use Django BASE_DIR (project root = /app in Docker)
CONTRACT_ARTIFACTS_PATH = (
    settings.BASE_DIR
    / "contracts"
    / "artifacts"
    / "contracts"
    / "TransactionLedger.sol"
    / "TransactionLedger.json"
)

# Contract address: use env/config for Docker shared volume, else default path
_DEFAULT_CONTRACT_FILE = Path(__file__).resolve().parent / "contract_address.json"
CONTRACT_ADDRESS_FILE = Path(
    os.environ.get("BLOCKCHAIN_CONTRACT_ADDRESS_FILE", str(_DEFAULT_CONTRACT_FILE))
)


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------
_service_instance = None


def get_blockchain_service():
    """Return the module-level BlockchainService singleton."""
    global _service_instance
    if _service_instance is None:
        _service_instance = BlockchainService()
    return _service_instance


def reset_blockchain_service():
    """Reset the singleton (useful in tests)."""
    global _service_instance
    if _service_instance is not None:
        _service_instance._initialized = False
        _service_instance._contract = None
        _service_instance._web3 = None
        _service_instance._account = None
    _service_instance = None


# ---------------------------------------------------------------------------
# Service class
# ---------------------------------------------------------------------------
class BlockchainService:
    """Service for interacting with the TransactionLedger smart contract."""

    def __init__(self):
        self._web3 = None
        self._contract = None
        self._account = None
        self._initialized = False

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------

    def _ensure_initialized(self):
        """Lazy-initialize Web3 connection and contract reference."""
        if self._initialized:
            return True

        if not getattr(settings, "BLOCKCHAIN_ENABLED", False):
            logger.debug("Blockchain service is disabled (BLOCKCHAIN_ENABLED=False)")
            return False

        try:
            from web3 import Web3

            rpc_url = getattr(
                settings, "BLOCKCHAIN_RPC_URL", "http://127.0.0.1:8545"
            )
            self._web3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={"timeout": 5}))

            if not self._web3.is_connected():
                logger.warning(
                    "Cannot connect to blockchain node at %s. "
                    "Make sure Hardhat node is running (npx hardhat node).",
                    rpc_url,
                )
                return False

            # Account from private key
            private_key = getattr(settings, "BLOCKCHAIN_PRIVATE_KEY", "")
            if private_key:
                self._account = self._web3.eth.account.from_key(private_key)
                self._web3.eth.default_account = self._account.address

            # Load contract (ABI + address)
            self._load_contract()

            self._initialized = True
            logger.info(
                "Blockchain service initialized – connected to %s (chain %s)",
                rpc_url,
                self._web3.eth.chain_id,
            )
            return True

        except Exception as exc:
            logger.error("Failed to initialize blockchain service: %s", exc)
            return False

    def _load_contract(self):
        """Load the contract ABI from Hardhat artifacts and the deployed address."""
        from web3 import Web3

        if not CONTRACT_ARTIFACTS_PATH.exists():
            logger.warning(
                "Contract artifacts not found at %s. "
                "Run 'npx hardhat compile' in the contracts/ directory.",
                CONTRACT_ARTIFACTS_PATH,
            )
            return

        with open(CONTRACT_ARTIFACTS_PATH, "r", encoding="utf-8") as fh:
            artifact = json.load(fh)
        abi = artifact["abi"]

        address = self._get_contract_address()
        if not address:
            logger.warning(
                "Contract address not found. "
                "Deploy with: python manage.py deploy_contract"
            )
            return

        self._contract = self._web3.eth.contract(
            address=Web3.to_checksum_address(address),
            abi=abi,
        )
        logger.info("Contract loaded at %s", address)

    @staticmethod
    def _get_contract_address():
        """Read deployed contract address from settings or JSON file."""
        addr = getattr(settings, "BLOCKCHAIN_CONTRACT_ADDRESS", "")
        if addr:
            return addr

        if CONTRACT_ADDRESS_FILE.exists():
            with open(CONTRACT_ADDRESS_FILE, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            return data.get("address", "")

        return ""

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def is_available(self):
        """Return True when blockchain node is reachable and contract is loaded."""
        try:
            return self._ensure_initialized() and self._contract is not None
        except Exception:
            return False

    def get_status(self):
        """Return a dict describing the current blockchain connection."""
        if not self._ensure_initialized():
            return {
                "status": "disconnected",
                "network": "hardhat-local",
                "message": "Blockchain service is not connected. Is Hardhat node running?",
            }

        try:
            chain_id = self._web3.eth.chain_id
            block_number = self._web3.eth.block_number
            trade_count = 0

            if self._contract:
                trade_count = self._contract.functions.tradeCount().call()

            return {
                "status": "connected",
                "network": "hardhat-local",
                "chainId": chain_id,
                "blockNumber": block_number,
                "contractAddress": (
                    self._contract.address if self._contract else None
                ),
                "accountAddress": (
                    self._account.address if self._account else None
                ),
                "tradeCount": trade_count,
            }
        except Exception as exc:
            logger.error("Error getting blockchain status: %s", exc)
            return {
                "status": "error",
                "network": "hardhat-local",
                "message": str(exc),
            }

    # ------------------------------------------------------------------
    # Record transaction
    # ------------------------------------------------------------------

    def record_transaction(self, transaction):
        """
        Record a Transaction on the blockchain.

        Args:
            transaction: ``transactions.models.Transaction`` instance.

        Returns:
            ``str`` – hex tx hash (with 0x prefix) **or** ``None`` on failure.
        """
        if not self.is_available():
            logger.warning(
                "Blockchain not available – skipping on-chain recording for TX %s",
                transaction.id,
            )
            return None

        try:
            # Convert Python UUIDs → bytes16
            tx_id_bytes = transaction.id.bytes
            buyer_id_bytes = transaction.buyer.id.bytes
            seller_id_bytes = transaction.seller.id.bytes

            tx_func = self._contract.functions.recordTrade(
                tx_id_bytes,
                transaction.stock.symbol,
                int(transaction.price),
                transaction.quantity,
                int(transaction.total_value),
                buyer_id_bytes,
                seller_id_bytes,
            )

            # Build, sign, send
            nonce = self._web3.eth.get_transaction_count(self._account.address)
            gas_estimate = tx_func.estimate_gas({"from": self._account.address})

            built_tx = tx_func.build_transaction(
                {
                    "from": self._account.address,
                    "nonce": nonce,
                    "gas": gas_estimate + 10_000,
                    "gasPrice": self._web3.eth.gas_price,
                }
            )

            signed_tx = self._web3.eth.account.sign_transaction(
                built_tx, self._account.key
            )
            raw = signed_tx.raw_transaction
            tx_hash = self._web3.eth.send_raw_transaction(raw)

            receipt = self._web3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)

            if receipt["status"] == 1:
                hash_hex = receipt["transactionHash"].hex()
                if not hash_hex.startswith("0x"):
                    hash_hex = "0x" + hash_hex
                logger.info(
                    "TX %s recorded on-chain – hash %s", transaction.id, hash_hex
                )
                return hash_hex

            logger.error(
                "On-chain TX reverted for transaction %s", transaction.id
            )
            return None

        except Exception as exc:
            logger.error(
                "Error recording TX %s on blockchain: %s",
                transaction.id,
                exc,
            )
            return None

    # ------------------------------------------------------------------
    # Verify transaction
    # ------------------------------------------------------------------

    def verify_transaction(self, transaction_id):
        """
        Verify a transaction exists on the blockchain.

        Args:
            transaction_id: UUID (string or ``uuid.UUID``).

        Returns:
            ``dict`` with verification details.
        """
        if not self.is_available():
            return {"verified": False, "error": "Blockchain not available"}

        try:
            import uuid as uuid_mod

            if isinstance(transaction_id, str):
                transaction_id = uuid_mod.UUID(transaction_id)

            tx_id_bytes = transaction_id.bytes

            exists, timestamp = self._contract.functions.verifyTrade(
                tx_id_bytes
            ).call()

            if exists:
                trade_data = self._contract.functions.getTrade(tx_id_bytes).call()
                return {
                    "verified": True,
                    "onChain": True,
                    "stockSymbol": trade_data[0],
                    "price": trade_data[1],
                    "quantity": trade_data[2],
                    "totalValue": trade_data[3],
                    "timestamp": timestamp,
                }

            return {
                "verified": False,
                "onChain": False,
                "message": "Transaction not found on blockchain",
            }

        except Exception as exc:
            logger.error("Error verifying TX %s: %s", transaction_id, exc)
            return {"verified": False, "error": str(exc)}

    # ------------------------------------------------------------------
    # Deploy contract (used by management command)
    # ------------------------------------------------------------------

    def deploy_contract(self):
        """
        Deploy the TransactionLedger contract via Web3.

        Returns:
            ``str`` – deployed contract address or ``None``.
        """
        if not getattr(settings, "BLOCKCHAIN_ENABLED", False):
            logger.error("Blockchain is disabled in settings")
            return None

        try:
            from web3 import Web3

            rpc_url = getattr(
                settings, "BLOCKCHAIN_RPC_URL", "http://127.0.0.1:8545"
            )
            self._web3 = Web3(
                Web3.HTTPProvider(rpc_url, request_kwargs={"timeout": 10})
            )

            if not self._web3.is_connected():
                logger.error("Cannot connect to %s", rpc_url)
                return None

            private_key = getattr(settings, "BLOCKCHAIN_PRIVATE_KEY", "")
            if not private_key:
                logger.error("BLOCKCHAIN_PRIVATE_KEY not set")
                return None

            self._account = self._web3.eth.account.from_key(private_key)
            self._web3.eth.default_account = self._account.address

            # Read artifact
            if not CONTRACT_ARTIFACTS_PATH.exists():
                logger.error(
                    "Artifacts not found at %s – run 'npx hardhat compile'",
                    CONTRACT_ARTIFACTS_PATH,
                )
                return None

            with open(CONTRACT_ARTIFACTS_PATH, "r", encoding="utf-8") as fh:
                artifact = json.load(fh)

            abi = artifact["abi"]
            bytecode = artifact["bytecode"]

            Contract = self._web3.eth.contract(abi=abi, bytecode=bytecode)

            nonce = self._web3.eth.get_transaction_count(self._account.address)
            tx = Contract.constructor().build_transaction(
                {
                    "from": self._account.address,
                    "nonce": nonce,
                    "gas": 3_000_000,
                    "gasPrice": self._web3.eth.gas_price,
                }
            )

            signed_tx = self._web3.eth.account.sign_transaction(
                tx, self._account.key
            )
            raw = signed_tx.raw_transaction
            tx_hash = self._web3.eth.send_raw_transaction(raw)

            receipt = self._web3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)

            if receipt["status"] != 1:
                logger.error("Contract deployment reverted")
                return None

            contract_address = receipt["contractAddress"]

            # Persist address
            CONTRACT_ADDRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(CONTRACT_ADDRESS_FILE, "w", encoding="utf-8") as fh:
                json.dump(
                    {
                        "address": contract_address,
                        "transactionHash": receipt["transactionHash"].hex(),
                        "blockNumber": receipt["blockNumber"],
                    },
                    fh,
                    indent=2,
                )

            # Activate contract reference
            self._contract = self._web3.eth.contract(
                address=contract_address, abi=abi
            )
            self._initialized = True

            logger.info("Contract deployed at %s", contract_address)
            return contract_address

        except Exception as exc:
            logger.error("Contract deployment failed: %s", exc)
            return None
