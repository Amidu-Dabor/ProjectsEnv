# Mac terminal command to clean up language model files and caches

# Create a cleanup script
cat > ~/cleanup_llm_models.sh << 'EOF'
#!/bin/bash

echo "Starting cleanup of language model files and caches on macOS..."

# Clean Hugging Face cache
echo "Cleaning Hugging Face cache..."
rm -rf ~/.cache/huggingface/

# Clean alternate locations
echo "Cleaning alternate Hugging Face locations..."
rm -rf ~/huggingface/
rm -rf ~/Library/Caches/huggingface/

# Clean pip cache
echo "Cleaning pip cache..."
pip cache purge

# Clean PyTorch hub cache
echo "Cleaning PyTorch hub cache..."
rm -rf ~/.cache/torch/
rm -rf ~/Library/Caches/torch/

# Clean temporary directories
echo "Cleaning temporary directories..."
find /tmp -name "*llama*" -exec rm -rf {} \; 2>/dev/null || true
find /tmp -name "*meta*" -exec rm -rf {} \; 2>/dev/null || true
find /tmp -name "*model*" -exec rm -rf {} \; 2>/dev/null || true
find ~/Library/Caches -name "*llama*" -exec rm -rf {} \; 2>/dev/null || true
find ~/Library/Caches -name "*meta*" -exec rm -rf {} \; 2>/dev/null || true

# Clean CUDA/MPS cache
echo "Cleaning GPU memory cache..."
python -c "import torch; torch.cuda.empty_cache() if hasattr(torch, 'cuda') else None; torch.mps.empty_cache() if hasattr(torch, 'mps') else None" 2>/dev/null || echo "Failed to clean GPU cache"

# Clean Safetensors cache
echo "Cleaning safetensors cache if present..."
rm -rf ~/.cache/safetensors/

# Check for model directories in common locations
echo "Checking for model directories in common locations..."
COMMON_DIRS=(
  "$HOME/models"
  "$HOME/Documents/models"
  "$HOME/Downloads/models"
  "./models"
  "./meta-llama"
)

for dir in "${COMMON_DIRS[@]}"; do
  if [ -d "$dir" ]; then
    echo "Found potential model directory: $dir"
    echo "Large files in this directory:"
    find "$dir" -type f -size +100M -exec ls -lh {} \; | sort -k5hr | head -10
    
    read -p "Do you want to remove $dir? (y/n): " choice
    if [ "$choice" = "y" ] || [ "$choice" = "Y" ]; then
      rm -rf "$dir"
      echo "Removed $dir"
    else
      echo "Skipping $dir"
    fi
  fi
done

# Clean homebrew caches if installed
if command -v brew >/dev/null 2>&1; then
  echo "Cleaning Homebrew cache..."
  brew cleanup
fi

echo "Cleanup complete!"
echo "Note: If you've downloaded models to custom locations, you may need to remove those manually."
EOF

# Make the script executable
# chmod +x ./cleanup_llm_models.sh

# Run the script
# ./cleanup_llm_models.sh
