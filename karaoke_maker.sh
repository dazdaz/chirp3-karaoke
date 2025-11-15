#!/bin/bash
#
# Karaoke Maker - Enhanced UVR-CLI Wrapper for macOS
# Create karaoke tracks with full instrumental, guide vocals, or reduced vocals
#
# Installation:
#   brew install --cask ultimate-vocal-remover
#   brew install ffmpeg  # Required for vocal reduction
#   chmod +x karaoke_maker.sh
#
# Usage:
#   ./karaoke_maker.sh -i <input> -o <output> [-m model] [-t target] [-v volume]
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
TARGET="instrumental"  # vocals, instrumental, or reduced-vocals
FORMAT=""
VOCAL_VOLUME="0.3"  # 30% vocal volume for reduced-vocals mode

print_usage() {
    printf "${BLUE}Karaoke Maker - Create Perfect Karaoke Tracks${NC}\n\n"
    printf "${GREEN}Usage:${NC}\n"
    printf "  $0 -i <input> -o <output> [options]\n\n"
    printf "${GREEN}Required:${NC}\n"
    printf "  -i <path>         Input file or directory\n"
    printf "  -o <path>         Output directory\n\n"
    printf "${GREEN}Options:${NC}\n"
    printf "  -m <model>        Model to use (auto-detected if not specified)\n"
    printf "                    Options: vocal-hq, vocal-fast, instrumental, demucs\n"
    printf "  -t <target>       Target output (default: instrumental)\n"
    printf "                    - instrumental: Full instrumental (no vocals)\n"
    printf "                    - vocals: Vocals only\n"
    printf "                    - reduced-vocals: Instrumental with quiet guide vocals\n"
    printf "  -v <volume>       Vocal volume for reduced-vocals mode (0.0-1.0, default: 0.3)\n"
    printf "  -f <format>       Force output format: MP3 or FLAC (auto-detected)\n"
    printf "  -h                Show this help message\n\n"
    printf "${GREEN}Examples:${NC}\n"
    printf "  # Create full instrumental karaoke track\n"
    printf "  $0 -i \"/path/to/song.mp3\" -o \"/path/to/output/\"\n\n"
    printf "  # Create karaoke with 20%% guide vocals\n"
    printf "  $0 -i \"song.mp3\" -o \"output/\" -t reduced-vocals -v 0.2\n\n"
    printf "  # Process directory with 40%% guide vocals\n"
    printf "  $0 -i \"/Music/Songs/\" -o \"/Music/Karaoke/\" -t reduced-vocals -v 0.4\n\n"
    printf "  # Extract vocals only\n"
    printf "  $0 -i \"/Music/Songs/\" -o \"/Music/Vocals/\" -t vocals\n\n"
    printf "${GREEN}Available Models:${NC}\n"
    printf "  vocal-hq         Kim_Vocal_2 - High quality vocal separation\n"
    printf "  vocal-fast       MDX23C-InstVoc HQ - Faster vocal separation\n"
    printf "  instrumental     Demucs_v4_hybrid - Best for instrumental extraction\n"
    printf "  demucs           Same as instrumental\n\n"
    printf "${GREEN}Target Modes:${NC}\n"
    printf "  instrumental     Pure instrumental, no vocals (for karaoke experts)\n"
    printf "  reduced-vocals   Instrumental + quiet guide vocals (helps singers stay on track)\n"
    printf "  vocals          Vocals only (for practice or remixing)\n\n"
    printf "${GREEN}Notes:${NC}\n"
    printf "  - File format (MP3/FLAC) is auto-detected from input files\n"
    printf "  - Batch mode enabled automatically for directories\n"
    printf "  - Reduced-vocals mode requires ffmpeg (brew install ffmpeg)\n"
    printf "  - Typical vocal volumes: 0.2 (soft guide), 0.3 (balanced), 0.4 (pronounced)\n"
}

# Check if required tools are installed
check_installation() {
    if [ ! -f "$UVR_CLI" ]; then
        printf "${RED}Error: UVR-CLI not found at: $UVR_CLI${NC}\n"
        printf "${YELLOW}Install with: brew install --cask ultimate-vocal-remover${NC}\n"
        exit 1
    fi
    
    if [ ! -x "$UVR_CLI" ]; then
        printf "${YELLOW}Making UVR-CLI executable...${NC}\n"
        chmod +x "$UVR_CLI"
    fi
    
    # Check for ffmpeg if using reduced-vocals
    if [ "$TARGET" == "reduced-vocals" ]; then
        if ! command -v ffmpeg &> /dev/null; then
            printf "${RED}Error: ffmpeg is required for reduced-vocals mode${NC}\n"
            printf "${YELLOW}Install with: brew install ffmpeg${NC}\n"
            exit 1
        fi
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

# Mix instrumental and vocals with reduced vocal volume
mix_reduced_vocals() {
    local instrumental="$1"
    local vocals="$2"
    local output="$3"
    local vol="$4"
    
    printf "${BLUE}Mixing instrumental with ${vol}x vocal volume...${NC}\n"
    
    # Use ffmpeg to mix the tracks
    # -filter_complex: Mix instrumental at full volume + vocals at reduced volume
    if ffmpeg -y -i "$instrumental" -i "$vocals" \
        -filter_complex "[1:a]volume=${vol}[v];[0:a][v]amix=inputs=2:duration=first" \
        "$output" &>/dev/null; then
        printf "${GREEN}✅ Mixed track created: $(basename "$output")${NC}\n"
        return 0
    else
        printf "${RED}❌ Failed to mix tracks${NC}\n"
        return 1
    fi
}

# Process a single file with reduced vocals
process_reduced_vocals_single() {
    local input="$1"
    local output_dir="$2"
    local basename=$(basename "$input")
    local filename="${basename%.*}"
    local ext="${basename##*.}"
    
    printf "\n${YELLOW}Processing: $basename${NC}\n"
    printf "${BLUE}Step 1/3: Extracting instrumental...${NC}\n"
    
    # Extract instrumental
    local temp_inst="$output_dir/.temp_${filename}_instrumental.$ext"
    "$UVR_CLI" -i "$input" -o "$output_dir" -m "$MODEL" -f "$FORMAT" --no_gui &>/dev/null
    
    # UVR outputs files with _(Instrumental) suffix
    local uvr_inst="$output_dir/${filename}_(Instrumental).$ext"
    if [ -f "$uvr_inst" ]; then
        mv "$uvr_inst" "$temp_inst"
    else
        printf "${RED}❌ Failed to extract instrumental${NC}\n"
        return 1
    fi
    
    printf "${BLUE}Step 2/3: Extracting vocals...${NC}\n"
    
    # Extract vocals (need to run UVR again or look for vocals output)
    local temp_vocals="$output_dir/.temp_${filename}_vocals.$ext"
    local uvr_vocals="$output_dir/${filename}_(Vocals).$ext"
    
    if [ -f "$uvr_vocals" ]; then
        mv "$uvr_vocals" "$temp_vocals"
    else
        # Run extraction for vocals if not already outputted
        "$UVR_CLI" -i "$input" -o "$output_dir" -m "Kim_Vocal_2" -f "$FORMAT" --no_gui &>/dev/null
        uvr_vocals="$output_dir/${filename}_(Vocals).$ext"
        if [ -f "$uvr_vocals" ]; then
            mv "$uvr_vocals" "$temp_vocals"
        else
            printf "${RED}❌ Failed to extract vocals${NC}\n"
            rm -f "$temp_inst"
            return 1
        fi
    fi
    
    printf "${BLUE}Step 3/3: Mixing with reduced vocals ($VOCAL_VOLUME volume)...${NC}\n"
    
    # Mix the tracks
    local output="$output_dir/${filename}_(Reduced_Vocals).$ext"
    if mix_reduced_vocals "$temp_inst" "$temp_vocals" "$output" "$VOCAL_VOLUME"; then
        # Clean up temp files
        rm -f "$temp_inst" "$temp_vocals"
        return 0
    else
        rm -f "$temp_inst" "$temp_vocals"
        return 1
    fi
}

# Parse command line arguments
while getopts "i:o:m:t:f:v:h" opt; do
    case $opt in
        i) INPUT_PATH="$OPTARG" ;;
        o) OUTPUT_DIR="$OPTARG" ;;
        m) MODEL="$OPTARG" ;;
        t) TARGET="$OPTARG" ;;
        f) FORMAT="$OPTARG" ;;
        v) VOCAL_VOLUME="$OPTARG" ;;
        h) print_usage; exit 0 ;;
        \?) printf "${RED}Invalid option: -$OPTARG${NC}\n"; print_usage; exit 1 ;;
    esac
done

# Check required arguments
if [ -z "$INPUT_PATH" ] || [ -z "$OUTPUT_DIR" ]; then
    printf "${RED}Error: Input and output paths are required${NC}\n\n"
    print_usage
    exit 1
fi

# Validate input exists
if [ ! -e "$INPUT_PATH" ]; then
    printf "${RED}Error: Input path does not exist: $INPUT_PATH${NC}\n"
    exit 1
fi

# Validate target
if [[ ! "$TARGET" =~ ^(vocals|instrumental|reduced-vocals)$ ]]; then
    printf "${RED}Error: Invalid target '$TARGET'. Must be: vocals, instrumental, or reduced-vocals${NC}\n"
    exit 1
fi

# Validate vocal volume
if [[ ! "$VOCAL_VOLUME" =~ ^0?\.[0-9]+$|^1\.0$|^1$ ]]; then
    printf "${RED}Error: Invalid vocal volume '$VOCAL_VOLUME'. Must be between 0.0 and 1.0${NC}\n"
    exit 1
fi

# Check installation
check_installation

# Auto-detect format if not specified
if [ -z "$FORMAT" ]; then
    FORMAT=$(detect_format "$INPUT_PATH")
    printf "${BLUE}Auto-detected format: ${GREEN}$FORMAT${NC}\n"
fi

# Auto-select model if not specified
if [ -z "$MODEL" ]; then
    MODEL=$(auto_select_model)
    printf "${BLUE}Auto-selected model: ${GREEN}$MODEL${NC}\n"
else
    MODEL=$(get_model_name "$MODEL")
    printf "${BLUE}Using model: ${GREEN}$MODEL${NC}\n"
fi

# Create output directory if it doesn't exist
mkdir -p "$OUTPUT_DIR"

# Display mode
if [ "$TARGET" == "reduced-vocals" ]; then
    printf "${BLUE}Mode: ${GREEN}Reduced Vocals (${VOCAL_VOLUME}x volume)${NC}\n"
elif [ "$TARGET" == "vocals" ]; then
    printf "${BLUE}Mode: ${GREEN}Vocals Only${NC}\n"
else
    printf "${BLUE}Mode: ${GREEN}Full Instrumental${NC}\n"
fi

# Determine if batch processing is needed
if [ -d "$INPUT_PATH" ]; then
    IS_BATCH=true
    printf "${BLUE}Processing directory in batch mode${NC}\n"
else
    IS_BATCH=false
    printf "${BLUE}Processing single file${NC}\n"
fi

# Handle reduced-vocals mode
if [ "$TARGET" == "reduced-vocals" ]; then
    if [ "$IS_BATCH" = true ]; then
        # Process all files in directory
        for file in "$INPUT_PATH"/*.{mp3,flac,MP3,FLAC} 2>/dev/null; do
            [ -f "$file" ] || continue
            process_reduced_vocals_single "$file" "$OUTPUT_DIR"
        done
    else
        # Process single file
        process_reduced_vocals_single "$INPUT_PATH" "$OUTPUT_DIR"
    fi
    
    printf "\n${GREEN}✅ Reduced vocals processing completed!${NC}\n"
    printf "${BLUE}Output saved to: ${GREEN}$OUTPUT_DIR${NC}\n"
    exit 0
fi

# Standard UVR processing for instrumental or vocals
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
printf "\n${YELLOW}Executing:${NC}\n"
printf "${GREEN}%s${NC}\n\n" "${CMD[*]}"

# Execute command
"${CMD[@]}"

# Check exit status
if [ $? -eq 0 ]; then
    printf "\n${GREEN}✅ Processing completed successfully!${NC}\n"
    printf "${BLUE}Output saved to: ${GREEN}$OUTPUT_DIR${NC}\n"
else
    printf "\n${RED}❌ Processing failed!${NC}\n"
    exit 1
fi
