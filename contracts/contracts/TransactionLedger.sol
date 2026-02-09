// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/**
 * @title TransactionLedger
 * @notice Records stock brokerage transactions on-chain for transparency and immutability.
 * @dev BourseChain - Amirkabir University SE2 Project (Sprint 4)
 *
 * Each matched trade in the BourseChain brokerage is recorded here as an immutable
 * on-chain record. This provides:
 *   - Tamper-proof transaction audit trail
 *   - Independent verification of trade execution
 *   - Regulatory transparency
 */
contract TransactionLedger {
    // -----------------------------------------------------------------------
    // Types
    // -----------------------------------------------------------------------

    struct Trade {
        bytes16 transactionId; // UUID of the Django Transaction record
        string stockSymbol; // e.g. "FOLD1", "SAPA1"
        uint256 price; // Price per share in IRR (Rial)
        uint256 quantity; // Number of shares traded
        uint256 totalValue; // Total trade value in IRR
        bytes16 buyerId; // UUID of the buyer
        bytes16 sellerId; // UUID of the seller
        uint256 timestamp; // Block timestamp when recorded
        bool exists; // Existence flag for mapping lookups
    }

    // -----------------------------------------------------------------------
    // State
    // -----------------------------------------------------------------------

    address public owner;
    uint256 public tradeCount;

    mapping(bytes16 => Trade) public trades;
    bytes16[] public tradeIds;

    // -----------------------------------------------------------------------
    // Events
    // -----------------------------------------------------------------------

    event TradeRecorded(
        bytes16 indexed transactionId,
        string stockSymbol,
        uint256 price,
        uint256 quantity,
        uint256 totalValue,
        bytes16 buyerId,
        bytes16 sellerId,
        uint256 timestamp
    );

    // -----------------------------------------------------------------------
    // Modifiers
    // -----------------------------------------------------------------------

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }

    // -----------------------------------------------------------------------
    // Constructor
    // -----------------------------------------------------------------------

    constructor() {
        owner = msg.sender;
    }

    // -----------------------------------------------------------------------
    // External Functions
    // -----------------------------------------------------------------------

    /**
     * @notice Record a new trade on the ledger.
     * @param _transactionId UUID bytes of the off-chain Transaction record.
     * @param _stockSymbol   Ticker symbol of the traded stock.
     * @param _price         Price per share in IRR.
     * @param _quantity      Number of shares traded.
     * @param _totalValue    Total trade value in IRR.
     * @param _buyerId       UUID bytes of the buyer.
     * @param _sellerId      UUID bytes of the seller.
     * @return The transactionId that was recorded.
     */
    function recordTrade(
        bytes16 _transactionId,
        string calldata _stockSymbol,
        uint256 _price,
        uint256 _quantity,
        uint256 _totalValue,
        bytes16 _buyerId,
        bytes16 _sellerId
    ) external onlyOwner returns (bytes16) {
        require(!trades[_transactionId].exists, "Trade already recorded");
        require(_price > 0, "Price must be positive");
        require(_quantity > 0, "Quantity must be positive");

        Trade memory trade = Trade({
            transactionId: _transactionId,
            stockSymbol: _stockSymbol,
            price: _price,
            quantity: _quantity,
            totalValue: _totalValue,
            buyerId: _buyerId,
            sellerId: _sellerId,
            timestamp: block.timestamp,
            exists: true
        });

        trades[_transactionId] = trade;
        tradeIds.push(_transactionId);
        tradeCount++;

        emit TradeRecorded(
            _transactionId,
            _stockSymbol,
            _price,
            _quantity,
            _totalValue,
            _buyerId,
            _sellerId,
            block.timestamp
        );

        return _transactionId;
    }

    /**
     * @notice Retrieve full details of a recorded trade.
     * @param _transactionId UUID bytes of the transaction to look up.
     */
    function getTrade(
        bytes16 _transactionId
    )
        external
        view
        returns (
            string memory stockSymbol,
            uint256 price,
            uint256 quantity,
            uint256 totalValue,
            bytes16 buyerId,
            bytes16 sellerId,
            uint256 timestamp
        )
    {
        require(trades[_transactionId].exists, "Trade not found");
        Trade memory t = trades[_transactionId];
        return (
            t.stockSymbol,
            t.price,
            t.quantity,
            t.totalValue,
            t.buyerId,
            t.sellerId,
            t.timestamp
        );
    }

    /**
     * @notice Quick verification: does a trade exist and when was it recorded?
     * @param _transactionId UUID bytes of the transaction.
     * @return exists   Whether the trade exists on-chain.
     * @return timestamp Block timestamp of the recording (0 if not found).
     */
    function verifyTrade(
        bytes16 _transactionId
    ) external view returns (bool exists, uint256 timestamp) {
        Trade memory t = trades[_transactionId];
        return (t.exists, t.timestamp);
    }

    /**
     * @notice Return all recorded trade IDs.
     */
    function getAllTradeIds() external view returns (bytes16[] memory) {
        return tradeIds;
    }
}
