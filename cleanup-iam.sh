#!/bin/bash

# Chirp Demo - IAM Cleanup Script
# This script removes the service account and its permissions created for the Chirp Demo application

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
fi

print_status "Using project: $PROJECT_ID"

# Service account configuration
SERVICE_ACCOUNT_NAME="chirp-demo-sa"
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
CREDENTIALS_FILE="${HOME}/chirp-demo-credentials.json"

# Confirmation prompt
echo ""
print_warning "This script will remove the following resources:"
echo "  • Service account: $SERVICE_ACCOUNT_EMAIL"
echo "  • IAM role bindings for the service account"
echo "  • Local credentials file: $CREDENTIALS_FILE"
echo ""
echo "This action cannot be undone. Are you sure? (yes/no)"
read -r confirmation

if [[ "$confirmation" != "yes" ]]; then
    echo "Cleanup cancelled."
    exit 0
fi

# Check if service account exists
if ! gcloud iam service-accounts describe "$SERVICE_ACCOUNT_EMAIL" --project="$PROJECT_ID" &>/dev/null; then
    print_warning "Service account $SERVICE_ACCOUNT_EMAIL does not exist."
else
    # Remove IAM policy bindings
    print_status "Removing IAM policy bindings..."
    
    # Only Speech-to-Text has a specific client role to remove
    echo "  Removing roles/speech.client..."
    gcloud projects remove-iam-policy-binding "$PROJECT_ID" \
        --member="serviceAccount:$SERVICE_ACCOUNT_EMAIL" \
        --role="roles/speech.client" \
        --quiet 2>/dev/null || true
    
    # Text-to-Speech doesn't have a specific role, just uses authentication
    echo "  Note: Text-to-Speech API doesn't use a specific IAM role"
    
    # List and delete service account keys
    print_status "Deleting service account keys..."
    
    # Get all keys for the service account
    keys=$(gcloud iam service-accounts keys list \
        --iam-account="$SERVICE_ACCOUNT_EMAIL" \
        --project="$PROJECT_ID" \
        --format="value(name)" \
        --filter="keyType:USER_MANAGED" 2>/dev/null || echo "")
    
    if [ -n "$keys" ]; then
        while IFS= read -r key; do
            if [ -n "$key" ]; then
                key_id=$(echo "$key" | rev | cut -d'/' -f1 | rev)
                echo "  Deleting key: $key_id"
                gcloud iam service-accounts keys delete "$key_id" \
                    --iam-account="$SERVICE_ACCOUNT_EMAIL" \
                    --project="$PROJECT_ID" \
                    --quiet
            fi
        done <<< "$keys"
    else
        print_status "No user-managed keys found."
    fi
    
    # Delete the service account
    print_status "Deleting service account: $SERVICE_ACCOUNT_EMAIL"
    gcloud iam service-accounts delete "$SERVICE_ACCOUNT_EMAIL" \
        --project="$PROJECT_ID" \
        --quiet
fi

# Remove local credentials file
if [ -f "$CREDENTIALS_FILE" ]; then
    print_status "Removing local credentials file: $CREDENTIALS_FILE"
    rm -f "$CREDENTIALS_FILE"
else
    print_warning "Local credentials file not found: $CREDENTIALS_FILE"
fi

# Check for backup files
backup_files=$(ls "${CREDENTIALS_FILE}.backup."* 2>/dev/null || true)
if [ -n "$backup_files" ]; then
    print_warning "Found backup credential files:"
    echo "$backup_files"
    echo "Do you want to remove these backup files as well? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        rm -f "${CREDENTIALS_FILE}.backup."*
        print_status "Backup files removed."
    else
        print_status "Backup files retained."
    fi
fi

# Optional: Disable APIs (commented out by default)
# Uncomment these lines if you want to disable the APIs as well
# print_warning "Do you want to disable the Google Cloud APIs? (y/n)"
# echo "Note: This may affect other applications using these APIs."
# read -r response
# if [[ "$response" =~ ^[Yy]$ ]]; then
#     print_status "Disabling Google Cloud APIs..."
#     gcloud services disable speech.googleapis.com --project="$PROJECT_ID" --quiet || true
#     gcloud services disable texttospeech.googleapis.com --project="$PROJECT_ID" --quiet || true
# fi

echo ""
print_status "Cleanup complete! 🧹"
echo ""
echo "The following have been removed:"
echo "  • Service account and all its keys"
echo "  • IAM role bindings"
echo "  • Local credentials file"
echo ""
echo "If you had set environment variables, you may want to remove them:"
echo "  unset GOOGLE_CLOUD_PROJECT"
echo "  unset GOOGLE_APPLICATION_CREDENTIALS"
echo ""
echo "Also remove them from your shell profile if you added them there."