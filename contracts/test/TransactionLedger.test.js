const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("TransactionLedger", function () {
  let ledger;
  let owner;
  let other;

  beforeEach(async function () {
    [owner, other] = await ethers.getSigners();
    const TransactionLedger =
      await ethers.getContractFactory("TransactionLedger");
    ledger = await TransactionLedger.deploy();
  });

  describe("Deployment", function () {
    it("should set the deployer as owner", async function () {
      expect(await ledger.owner()).to.equal(owner.address);
    });

    it("should start with zero trade count", async function () {
      expect(await ledger.tradeCount()).to.equal(0);
    });
  });

  describe("recordTrade", function () {
    it("should record a trade successfully", async function () {
      const txId = ethers.randomBytes(16);
      const buyerId = ethers.randomBytes(16);
      const sellerId = ethers.randomBytes(16);

      await expect(
        ledger.recordTrade(
          txId,
          "FOLD1",
          50000,
          10,
          500000,
          buyerId,
          sellerId
        )
      ).to.emit(ledger, "TradeRecorded");

      expect(await ledger.tradeCount()).to.equal(1);
    });

    it("should store correct trade data", async function () {
      const txId = ethers.randomBytes(16);
      const buyerId = ethers.randomBytes(16);
      const sellerId = ethers.randomBytes(16);

      await ledger.recordTrade(
        txId,
        "SAPA1",
        75000,
        20,
        1500000,
        buyerId,
        sellerId
      );

      const trade = await ledger.getTrade(txId);
      expect(trade.stockSymbol).to.equal("SAPA1");
      expect(trade.price).to.equal(75000n);
      expect(trade.quantity).to.equal(20n);
      expect(trade.totalValue).to.equal(1500000n);
    });

    it("should reject duplicate trade IDs", async function () {
      const txId = ethers.randomBytes(16);
      const buyerId = ethers.randomBytes(16);
      const sellerId = ethers.randomBytes(16);

      await ledger.recordTrade(
        txId,
        "FOLD1",
        50000,
        10,
        500000,
        buyerId,
        sellerId
      );

      await expect(
        ledger.recordTrade(
          txId,
          "FOLD1",
          50000,
          10,
          500000,
          buyerId,
          sellerId
        )
      ).to.be.revertedWith("Trade already recorded");
    });

    it("should reject zero price", async function () {
      const txId = ethers.randomBytes(16);
      const buyerId = ethers.randomBytes(16);
      const sellerId = ethers.randomBytes(16);

      await expect(
        ledger.recordTrade(txId, "FOLD1", 0, 10, 0, buyerId, sellerId)
      ).to.be.revertedWith("Price must be positive");
    });

    it("should reject zero quantity", async function () {
      const txId = ethers.randomBytes(16);
      const buyerId = ethers.randomBytes(16);
      const sellerId = ethers.randomBytes(16);

      await expect(
        ledger.recordTrade(txId, "FOLD1", 50000, 0, 0, buyerId, sellerId)
      ).to.be.revertedWith("Quantity must be positive");
    });

    it("should only allow owner to record trades", async function () {
      const txId = ethers.randomBytes(16);
      const buyerId = ethers.randomBytes(16);
      const sellerId = ethers.randomBytes(16);

      await expect(
        ledger
          .connect(other)
          .recordTrade(txId, "FOLD1", 50000, 10, 500000, buyerId, sellerId)
      ).to.be.revertedWith("Only owner can call this function");
    });
  });

  describe("verifyTrade", function () {
    it("should verify an existing trade", async function () {
      const txId = ethers.randomBytes(16);
      const buyerId = ethers.randomBytes(16);
      const sellerId = ethers.randomBytes(16);

      await ledger.recordTrade(
        txId,
        "FOLD1",
        50000,
        10,
        500000,
        buyerId,
        sellerId
      );

      const [exists, timestamp] = await ledger.verifyTrade(txId);
      expect(exists).to.be.true;
      expect(timestamp).to.be.gt(0);
    });

    it("should return false for non-existent trade", async function () {
      const txId = ethers.randomBytes(16);
      const [exists, timestamp] = await ledger.verifyTrade(txId);
      expect(exists).to.be.false;
      expect(timestamp).to.equal(0);
    });
  });

  describe("getTrade", function () {
    it("should revert for non-existent trade", async function () {
      const txId = ethers.randomBytes(16);
      await expect(ledger.getTrade(txId)).to.be.revertedWith("Trade not found");
    });
  });

  describe("getAllTradeIds", function () {
    it("should return all recorded trade IDs", async function () {
      const txId1 = ethers.randomBytes(16);
      const txId2 = ethers.randomBytes(16);
      const buyerId = ethers.randomBytes(16);
      const sellerId = ethers.randomBytes(16);

      await ledger.recordTrade(
        txId1,
        "FOLD1",
        50000,
        10,
        500000,
        buyerId,
        sellerId
      );
      await ledger.recordTrade(
        txId2,
        "SAPA1",
        30000,
        5,
        150000,
        buyerId,
        sellerId
      );

      const ids = await ledger.getAllTradeIds();
      expect(ids.length).to.equal(2);
    });
  });

  describe("Multiple trades", function () {
    it("should correctly count multiple trades", async function () {
      const buyerId = ethers.randomBytes(16);
      const sellerId = ethers.randomBytes(16);

      for (let i = 0; i < 5; i++) {
        const txId = ethers.randomBytes(16);
        await ledger.recordTrade(
          txId,
          `STK${i}`,
          (i + 1) * 10000,
          (i + 1) * 5,
          (i + 1) * 50000,
          buyerId,
          sellerId
        );
      }

      expect(await ledger.tradeCount()).to.equal(5);
      const ids = await ledger.getAllTradeIds();
      expect(ids.length).to.equal(5);
    });
  });
});
