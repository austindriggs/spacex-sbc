import glob
import os
import re
import urllib.parse

# 1. Read README content
with open('README.md', 'r', encoding='utf-8') as f:
    readme_text = f.read()

# 2. Extract anything inside attachments/... up to the closing quote or parenthesis
# Handles both standard markdown ![](attachments/...) and HTML <img src="attachments/...">
raw_matches = re.findall(r'attachments/([^"\'\)\n\r]+)', readme_text)

# Decode URL encoding (%20 -> spaces) and strip any lingering whitespaces/quotes
used_images = {
    urllib.parse.unquote(match.strip('"\') ')).strip()
    for match in raw_matches
}

print(f"Found {len(used_images)} referenced image(s) in README.md:")
for img in sorted(used_images):
    print(f"  - {img}")

print("\n--- Scanning attachments/ folder ---")

# 3. Check attachments directory and delete unreferenced files
attachments_dir = 'attachments'
removed_count = 0

if not os.path.exists(attachments_dir):
    print(f"Error: Directory '{attachments_dir}' not found. Make sure you run this script from project root.")
else:
    for filepath in glob.glob(os.path.join(attachments_dir, '*')):
        filename = os.path.basename(filepath)
        
        # Match exact name
        if filename not in used_images and os.path.isfile(filepath):
            print(f"Removing junk file: {filename}")
            os.remove(filepath)
            removed_count += 1

    print(f"\nCleanup complete! Removed {removed_count} junk file(s).")
