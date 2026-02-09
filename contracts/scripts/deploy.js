/**
 * Deploy TransactionLedger to local Hardhat network.
 *
 * Usage:
 *   npx hardhat run scripts/deploy.js --network localhost
 *
 * Prerequisites:
 *   npx hardhat node   (running in another terminal)
 */

const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  console.log("Deploying TransactionLedger...");

  const TransactionLedger =
    await hre.ethers.getContractFactory("TransactionLedger");
  const ledger = await TransactionLedger.deploy();
  await ledger.waitForDeployment();

  const address = await ledger.getAddress();
  console.log("TransactionLedger deployed to:", address);

  // --- Save deployment info to contracts/deployments/ ---
  const deploymentDir = path.join(__dirname, "..", "deployments");
  if (!fs.existsSync(deploymentDir)) {
    fs.mkdirSync(deploymentDir, { recursive: true });
  }

  const deploymentInfo = {
    address: address,
    network: hre.network.name,
    chainId: (await hre.ethers.provider.getNetwork()).chainId.toString(),
    deployer: (await hre.ethers.getSigners())[0].address,
    timestamp: new Date().toISOString(),
  };

  fs.writeFileSync(
    path.join(deploymentDir, "localhost.json"),
    JSON.stringify(deploymentInfo, null, 2)
  );

  // --- Also save to Django blockchain_service for easy access ---
  const djangoPath = path.join(
    __dirname,
    "..",
    "..",
    "backend",
    "blockchain_service",
    "contract_address.json"
  );
  fs.writeFileSync(
    djangoPath,
    JSON.stringify(
      {
        address: address,
        transactionHash: "",
        blockNumber: 0,
      },
      null,
      2
    )
  );

  console.log("Deployment info saved to:");
  console.log("  -", path.join(deploymentDir, "localhost.json"));
  console.log("  -", djangoPath);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
