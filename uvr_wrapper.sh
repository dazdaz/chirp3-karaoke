#!/bin/bash
#
# UVR-CLI Wrapper Script for macOS
# Simplifies usage of Ultimate Vocal Remover CLI
#
# Installation:
#   brew install --cask ultimate-vocal-remover
#   chmod +x uvr_wrapper.sh
#
# Usage:
#   ./uvr_wrapper.sh -i <input> -o <output> [-m model] [-t vocals|instrumental]
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
UVR_CLI="/Applications/Ultimate Vocal Remover.app/Contents/MacOS/UVR-CLI-macOS"
MODEL=""
OUTPUT_DIR=""
INPUT_PATH=""
TARGET="instrumental"  # vocals or instrumental
FORMAT=""

# Model presets
MODEL_VOCAL_HIGH_QUALITY="Kim_Vocal_2"
MODEL_VOCAL_FAST="MDX23C-InstVoc HQ"
MODEL_INSTRUMENTAL="Demucs_v4_hybrid"

print_usage() {
    cat << EOF
${BLUE}UVR-CLI Wrapper - Ultimate Vocal Remover Helper${NC}

${GREEN}Usage:${NC}
  $0 -i <input> -o <output> [options]

${GREEN}Required:${NC}
  -i <path>         Input file or directory
  -o <path>         Output directory

${GREEN}Options:${NC}
  -m <model>        Model to use (auto-detected if not specified)
                    Options: vocal-hq, vocal-fast, instrumental, demucs
  -t <target>       Target output: vocals or instrumental (default: instrumental)
  -f <format>       Force output format: MP3 or FLAC (auto-detected if not specified)
  -h                Show this help message

${GREEN}Examples:${NC}
  # Process single file (auto-detect format and model)
  $0 -i "/path/to/song.flac" -o "/path/to/output/"
  
  # Process directory with high-quality vocal removal
  $0 -i "/Music/Songs/" -o "/Music/Instrumentals/" -m vocal-hq
  
  # Extract vocals only
  $0 -i "/Music/Songs/" -o "/Music/Vocals/" -t vocals -m vocal-fast

${GREEN}Available Models:${NC}
  vocal-hq         Kim_Vocal_2 - High quality vocal separation
  vocal-fast       MDX23C-InstVoc HQ - Faster vocal separation
  instrumental     Demucs_v4_hybrid - Best for instrumental extraction
  demucs           Same as instrumental

${GREEN}Notes:${NC}
  - File format (MP3/FLAC) is auto-detected from input files
  - If processing directory, uses batch + recursive mode
  - Script checks if UVR-CLI is installed
EOF
}

# Check if UVR-CLI is installed
check_installation() {
    if [ ! -f "$UVR_CLI" ]; then
        echo -e "${RED}Error: UVR-CLI not found at: $UVR_CLI${NC}"
        echo -e "${YELLOW}Install with: brew install --cask ultimate-vocal-remover${NC}"
        exit 1
    fi
    
    if [ ! -x "$UVR_CLI" ]; then
        echo -e "${YELLOW}Making UVR-CLI executable...${NC}"
        chmod +x "$UVR_CLI"
    fi
}

# Auto-detect file format from input
detect_format() {
    local input="$1"
    
    if [ -f "$input" ]; then
        # Single file
        if [[ "$input" =~ \.flac$ ]]; then
            echo "FLAC"
        elif [[ "$input" =~ \.mp3$ ]]; then
            echo "MP3"
        else
            echo "MP3"  # Default to MP3
        fi
    elif [ -d "$input" ]; then
        # Directory - check first audio file found
        local first_flac=$(find "$input" -maxdepth 1 -iname "*.flac" -print -quit)
        local first_mp3=$(find "$input" -maxdepth 1 -iname "*.mp3" -print -quit)
        
        if [ -n "$first_flac" ]; then
            echo "FLAC"
        elif [ -n "$first_mp3" ]; then
            echo "MP3"
        else
            echo "MP3"  # Default to MP3
        fi
    else
        echo "MP3"  # Default
    fi
}

# Convert model preset to actual model name
get_model_name() {
    case "$1" in
        vocal-hq|high-quality)
            echo "Kim_Vocal_2"
            ;;
        vocal-fast|fast)
            echo "MDX23C-InstVoc HQ"
            ;;
        instrumental|demucs)
            echo "Demucs_v4_hybrid"
            ;;
        *)
            # If it's not a preset, assume it's a full model name
            echo "$1"
            ;;
    esac
}

# Auto-select model based on target
auto_select_model() {
    if [ "$TARGET" == "vocals" ]; then
        echo "Kim_Vocal_2"
    else
        echo "Demucs_v4_hybrid"
    fi
}

# Parse command line arguments
while getopts "i:o:m:t:f:h" opt; do
    case $opt in
        i) INPUT_PATH="$OPTARG" ;;
        o) OUTPUT_DIR="$OPTARG" ;;
        m) MODEL="$OPTARG" ;;
        t) TARGET="$OPTARG" ;;
        f) FORMAT="$OPTARG" ;;
        h) print_usage; exit 0 ;;
        \?) echo -e "${RED}Invalid option: -$OPTARG${NC}"; print_usage; exit 1 ;;
    esac
done

# Check required arguments
if [ -z "$INPUT_PATH" ] || [ -z "$OUTPUT_DIR" ]; then
    echo -e "${RED}Error: Input and output paths are required${NC}\n"
    print_usage
    exit 1
fi

# Validate input exists
if [ ! -e "$INPUT_PATH" ]; then
    echo -e "${RED}Error: Input path does not exist: $INPUT_PATH${NC}"
    exit 1
fi

# Check installation
check_installation

# Auto-detect format if not specified
if [ -z "$FORMAT" ]; then
    FORMAT=$(detect_format "$INPUT_PATH")
    echo -e "${BLUE}Auto-detected format: ${GREEN}$FORMAT${NC}"
fi

# Auto-select model if not specified
if [ -z "$MODEL" ]; then
    MODEL=$(auto_select_model)
    echo -e "${BLUE}Auto-selected model: ${GREEN}$MODEL${NC}"
else
    MODEL=$(get_model_name "$MODEL")
    echo -e "${BLUE}Using model: ${GREEN}$MODEL${NC}"
fi

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Determine if batch processing is needed
if [ -d "$INPUT_PATH" ]; then
    IS_BATCH=true
    echo -e "${BLUE}Processing directory in batch mode${NC}"
else
    IS_BATCH=false
    echo -e "${BLUE}Processing single file${NC}"
fi

# Build command
CMD=("$UVR_CLI")
CMD+=("-i" "$INPUT_PATH")
CMD+=("-o" "$OUTPUT_DIR")
CMD+=("-m" "$MODEL")
CMD+=("-f" "$FORMAT")
CMD+=("--no_gui")

if [ "$IS_BATCH" = true ]; then
    CMD+=("--batch")
    CMD+=("--recursive")
fi

# Display command
echo -e "\n${YELLOW}Executing:${NC}"
echo -e "${GREEN}${CMD[@]}${NC}\n"

# Execute command
"${CMD[@]}"

# Check exit status
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✅ Processing completed successfully!${NC}"
    echo -e "${BLUE}Output saved to: ${GREEN}$OUTPUT_DIR${NC}"
else
    echo -e "\n${RED}❌ Processing failed!${NC}"
    exit 1
fi
