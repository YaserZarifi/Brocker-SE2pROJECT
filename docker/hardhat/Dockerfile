# ==============================================
# BourseChain Hardhat - Local Ethereum Node
# Sprint 6 - Docker
# ==============================================

FROM docker.arvancloud.ir/node:20-alpine

WORKDIR /app

# Install dependencies
COPY contracts/package.json contracts/package-lock.json* ./
RUN npm ci 2>/dev/null || npm install

# Copy contracts source
COPY contracts/ .

# Compile Solidity contracts
RUN npx hardhat compile

# Expose JSON-RPC port
EXPOSE 8545

# Health check (Node.js TCP check - nc not available in node:alpine)
HEALTHCHECK --interval=10s --timeout=5s --retries=5 \
    CMD node -e "const s=require('net').connect(8545,'localhost',()=>{s.end();process.exit(0)});s.on('error',()=>process.exit(1));setTimeout(()=>process.exit(1),3000)"

# Start Hardhat node (listen on all interfaces)
CMD ["npx", "hardhat", "node", "--hostname", "0.0.0.0"]
