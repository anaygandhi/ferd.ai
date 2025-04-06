
#!/bin/bash

# Define colors
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
NC="\033[0m" # No Color

# 1. Remove /out/ dir if it exists
echo -e "${YELLOW}Step 1: Checking for /out/ directory...${NC}"
if [ -d "out" ]; then
    rm -rf out
    echo -e "${GREEN}Removed /out/ directory.${NC}"
else
    echo -e "${YELLOW}/out/ directory does not exist, skipping.${NC}"
fi

# 2. Run "npm run electron:build"
echo -e "${YELLOW}Step 2: Running 'npm run electron:build'...${NC}"
npm run electron:build
echo -e "${GREEN}Electron build completed.${NC}"


# 3. Run "npm run start" in background
echo -e "${YELLOW}Step 3: Starting 'npm run start' in background...${NC}"
npm run start &
START_PID=$!
echo -e "${GREEN}Started 'npm run start' (PID: $START_PID).${NC}"

# 4. Run "npm run electron"
echo -e "${YELLOW}Step 4: Running 'npm run electron'...${NC}"
npm run electron

# Optional: kill background process on exit
echo -e "${YELLOW}Cleaning up background 'npm run start' process...${NC}"
kill $START_PID 2>/dev/null && echo -e "${GREEN}Stopped background process.${NC}" || echo -e "${YELLOW}Background process already stopped.${NC}"




