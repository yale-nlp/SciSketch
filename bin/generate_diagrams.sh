#!/bin/bash

# Get the directory containing this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Get the project root directory (parent of bin)
PROJECT_ROOT="$(dirname "$DIR")"

# Default directories
PARSED_PAPER_DIRECTORY="samples/parsed_papers"
LANGUAGE="drawio"
SAVE_DIRECTORY="generated_diagram"

# Parse command line arguments
SAMPLE_ID=""
while [[ $# -gt 0 ]]; do
  case $1 in
    --sample_id)
      SAMPLE_ID="$2"
      shift 2
      ;;
    --language)
      LANGUAGE="$2"
      shift 2
      ;;
    --parsed_paper_directory)
      PARSED_PAPER_DIRECTORY="$2"
      shift 2
      ;;
    --save_directory)
      SAVE_DIRECTORY="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Build the command
CMD="python ${PROJECT_ROOT}/src/custom_main.py"
CMD+=" --parsed_paper_directory ${PARSED_PAPER_DIRECTORY}"
CMD+=" --language ${LANGUAGE}"
CMD+=" --save_directory ${SAVE_DIRECTORY}"

# Add sample_id if provided
if [ -n "$SAMPLE_ID" ]; then
  CMD+=" --sample_id ${SAMPLE_ID}"
fi

# Print the command being executed
echo "Executing: $CMD"

# Execute the command
eval "$CMD"

echo "Diagram generation complete."