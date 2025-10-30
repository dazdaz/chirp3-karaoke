#!/bin/bash

# Chirp Demo - IAM Setup Script
# This script creates a service account and grants necessary permissions for the Chirp Demo application

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    print_error "gcloud CLI is not installed. Please install it first."
    echo "Visit: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Get project ID
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    echo "No default project set. Please enter your Google Cloud Project ID:"
    read -r PROJECT_ID
    if [ -z "$PROJECT_ID" ]; then
        print_error "Project ID is required."
        exit 1
    fi
    gcloud config set project "$PROJECT_ID"
fi

print_status "Using project: $PROJECT_ID"

# Service account configuration
SERVICE_ACCOUNT_NAME="chirp-demo-sa"
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
CREDENTIALS_FILE="${HOME}/chirp-demo-credentials.json"

# Check if service account already exists
if gcloud iam service-accounts describe "$SERVICE_ACCOUNT_EMAIL" --project="$PROJECT_ID" &>/dev/null; then
    print_warning "Service account $SERVICE_ACCOUNT_EMAIL already exists."
    echo "Do you want to continue and update its permissions? (y/n)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo "Setup cancelled."
        exit 0
    fi
else
    # Create service account
    print_status "Creating service account: $SERVICE_ACCOUNT_NAME"
    gcloud iam service-accounts create "$SERVICE_ACCOUNT_NAME" \
        --display-name="Chirp Demo Service Account" \
        --project="$PROJECT_ID"
    
    # Wait for service account to be available
    print_status "Waiting for service account to be available..."
    sleep 5
    
    # Verify service account exists
    max_retries=5
    retry_count=0
    while [ $retry_count -lt $max_retries ]; do
        if gcloud iam service-accounts describe "$SERVICE_ACCOUNT_EMAIL" --project="$PROJECT_ID" &>/dev/null; then
            print_status "Service account is ready"
            break
        else
            retry_count=$((retry_count + 1))
            if [ $retry_count -eq $max_retries ]; then
                print_error "Service account creation failed or is taking too long"
                exit 1
            fi
            echo "  Waiting for service account to propagate... (attempt $retry_count/$max_retries)"
            sleep 3
        fi
    done
fi

# Enable required APIs
print_status "Enabling required Google Cloud APIs..."

apis=(
    "speech.googleapis.com"
    "texttospeech.googleapis.com"
)

for api in "${apis[@]}"; do
    echo "  Enabling $api..."
    gcloud services enable "$api" --project="$PROJECT_ID" || true
done

# Grant required IAM roles
print_status "Granting IAM roles to service account..."

# Speech-to-Text requires the client role
echo "  Granting roles/speech.client..."
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
    --role="roles/speech.client" \
    --condition=None \
    --quiet

# Text-to-Speech API doesn't have a specific client role
# Authentication alone is sufficient with the API enabled
print_status "Text-to-Speech API access granted via authentication (no specific role required)"

# Create and download service account key
print_status "Creating service account key..."

# Check if credentials file already exists
if [ -f "$CREDENTIALS_FILE" ]; then
    print_warning "Credentials file already exists at: $CREDENTIALS_FILE"
    echo "Do you want to create a new key and overwrite the existing file? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        # Backup existing file
        backup_file="${CREDENTIALS_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
        mv "$CREDENTIALS_FILE" "$backup_file"
        print_status "Existing credentials backed up to: $backup_file"
        
        gcloud iam service-accounts keys create "$CREDENTIALS_FILE" \
            --iam-account="$SERVICE_ACCOUNT_EMAIL" \
            --project="$PROJECT_ID"
    else
        print_status "Using existing credentials file."
    fi
else
    gcloud iam service-accounts keys create "$CREDENTIALS_FILE" \
        --iam-account="$SERVICE_ACCOUNT_EMAIL" \
        --project="$PROJECT_ID"
fi

# Set file permissions
chmod 600 "$CREDENTIALS_FILE"
print_status "Credentials saved to: $CREDENTIALS_FILE"

# Print environment variables to set
echo ""
print_status "Setup complete! 🎉"
echo ""
echo "To use the Chirp Demo application, set these environment variables:"
echo ""
echo "  export GOOGLE_CLOUD_PROJECT=\"$PROJECT_ID\""
echo "  export GOOGLE_APPLICATION_CREDENTIALS=\"$CREDENTIALS_FILE\""
echo ""
echo "You can add these to your shell profile (~/.bashrc or ~/.zshrc) for persistence."
echo ""
echo "To verify the setup, run:"
echo "  gcloud auth application-default print-access-token"