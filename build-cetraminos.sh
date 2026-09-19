#!/usr/bin/env bash
set -e

# ==============================================================================
# Cetraminos WebAssembly (Emscripten) Build Script
# ==============================================================================

# Terminal colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. Verify or load Emscripten (emcc)
if ! command -v emcc &> /dev/null; then
    if [ -f "$HOME/emsdk/emsdk_env.sh" ]; then
        echo -e "${YELLOW}[*] emcc not found in current PATH. Loading ~/emsdk/emsdk_env.sh...${NC}"
        # shellcheck source=/dev/null
        source "$HOME/emsdk/emsdk_env.sh" > /dev/null 2>&1
    fi
fi

if ! command -v emcc &> /dev/null; then
    echo -e "${RED}[!] Error: 'emcc' (Emscripten) was not found on the system.${NC}"
    echo -e "Install Emscripten via emsdk by running:"
    echo -e "  git clone https://github.com/emscripten-core/emsdk.git ~/emsdk"
    echo -e "  cd ~/emsdk && ./emsdk install latest && ./emsdk activate latest"
    echo -e "  source ~/emsdk/emsdk_env.sh"
    exit 1
fi

echo -e "${GREEN}[✓] Emscripten detected: $(emcc -v 2>&1 | head -n 1)${NC}"

# 2. Input and output directories
PORTFOLIO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CETRAMINOS_SRC="${1:-/home/cloud/my_projects/Cetraminos/Cetraminos}"
DEST_DIR="$PORTFOLIO_DIR/frontend/public/games/cetraminos"

if [ ! -d "$CETRAMINOS_SRC/src" ]; then
    echo -e "${RED}[!] Cetraminos directory not found at: $CETRAMINOS_SRC${NC}"
    echo -e "Usage: ./build-cetraminos.sh [path_to_Cetraminos_folder]"
    exit 1
fi

echo -e "${BLUE}[*] Compiling Cetraminos from: $CETRAMINOS_SRC/src${NC}"
echo -e "${BLUE}[*] WebAssembly destination: $DEST_DIR${NC}"

mkdir -p "$DEST_DIR"

# 3. Execute compilation with emcc
cd "$CETRAMINOS_SRC/src"

echo -e "${YELLOW}[*] Generating Cetraminos.js and Cetraminos.wasm with SDL2 MP3 support...${NC}"

emcc \
    backendPieces.c \
    frontendPieces.c \
    main.c \
    music.c \
    randomGenerator.c \
    scoreSystem.c \
    Cetraminos.c \
    menu.c \
    GString.c \
    -O3 \
    -s USE_SDL=2 \
    -s USE_SDL_TTF=2 \
    -s USE_SDL_MIXER=2 \
    -s SDL2_MIXER_FORMATS=mp3 \
    -s WASM=1 \
    -s ASYNCIFY=1 \
    -s ALLOW_MEMORY_GROWTH=1 \
    --preload-file fonts \
    --preload-file CetraminosMusic.mp3 \
    --preload-file CetraminosMusic2.mp3 \
    --preload-file CetraminosMusic_speed1.mp3 \
    --preload-file CetraminosMusic_speed2.mp3 \
    --preload-file CetraminosMusic_speed3.mp3 \
    -o "$DEST_DIR/Cetraminos.js"

echo -e "${GREEN}[✓] Success! Cetraminos compiled to WebAssembly!${NC}"
echo -e "${GREEN}[✓] Generated artifacts in $DEST_DIR:${NC}"
ls -lh "$DEST_DIR/Cetraminos.js" "$DEST_DIR/Cetraminos.wasm" "$DEST_DIR/Cetraminos.data" 2>/dev/null || true
echo -e "${BLUE}[*] Cetraminos is ready to play in your 'Games' tab!${NC}"
