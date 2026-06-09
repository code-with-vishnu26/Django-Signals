import os
import shutil

# Source paths from the brain artifact directory
brain_dir = r"C:\Users\jilla\\.gemini\antigravity-ide\brain\fbec9635-8f21-4ddd-a26e-6b088c20314b"
target_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "signals_app", "static", "signals_app", "screenshots")

# Create target directory
os.makedirs(target_dir, exist_ok=True)

files_to_copy = [
    "q1_and_q2_results_1781017261747.png",
    "q3_and_class_results_1781017253703.png"
]

print("Copying screenshots to static files...")
for filename in files_to_copy:
    src = os.path.join(brain_dir, filename)
    dst = os.path.join(target_dir, filename)
    if os.path.exists(src):
        shutil.copy(src, dst)
        print(f"Copied: {filename} -> signals_app/static/signals_app/screenshots/{filename}")
    else:
        print(f"Source file not found: {src}")

print("Done!")
