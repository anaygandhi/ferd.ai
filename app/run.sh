
#!/bin/bash

# Define colors
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
NC="\033[0m" # No Color

# Get CLI args 
DEV=$1

# 1. Check if dev mode
if [ $DEV == "dev" ]; then 

    # Info print
    echo -e "${YELLOW} Running DEV mode...${NC}"

    # Remove /out/ dir if it exists
    echo -e "${YELLOW}Checking for /out/ directory...${NC}"
    if [ -d "out" ]; then
        rm -rf out
        echo -e "${GREEN}Removed /out/ directory.${NC}"
    fi

    # Run "npm run electron:build" to rebuild the /out/ dir 
    echo -e "${YELLOW}Running 'npm run electron:build'...${NC}"
    npm run electron:build
    echo -e "${GREEN}Electron build completed.${NC}"
fi 

# 2. Run "npm run start" in background
echo -e "${YELLOW}Starting 'npm run start' in background...${NC}"
npm run start &
START_PID=$!
echo -e "${GREEN}Started 'npm run start' (PID: $START_PID).${NC}"

# 3. Run "npm run electron"
echo -e "${YELLOW}Running 'npm run electron'...${NC}"
npm run electron

# CLEANUP: kill background process on exit
echo -e "${YELLOW}Cleaning up background 'npm run start' process...${NC}"
kill $START_PID 2>/dev/null && echo -e "${GREEN}Stopped background process.${NC}" || echo -e "${YELLOW}Background process already stopped.${NC}"




