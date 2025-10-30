from PIL import Image
import sys

# --- Configuration ---

# The scrambled image file provided by the case
SCRAMBLED_IMAGE_FILE = "Week 6\\jigsaw.webp"

# The final reconstructed image we will save
RECONSTRUCTED_IMAGE_FILE = "reconstructed_image.png"

# The size of the full image (500x500)
IMAGE_WIDTH = 500
IMAGE_HEIGHT = 500

# The size of each individual piece (500 / 5 = 100)
PIECE_SIZE = 100

# The grid size
GRID_SIZE = 5

# --- CRITICAL STEP: MAPPING ---
# This mapping has been pre-filled based on the image you uploaded.
#
# Format:
# (current_row, current_col): (original_row, original_col)
#

MAPPING = {
    # Data transcribed from image_aef377.png
    (0, 0): (2, 1),
    (0, 1): (1, 1),
    (0, 2): (4, 1),
    (0, 3): (0, 3),
    (0, 4): (0, 1),
    (1, 0): (1, 4),
    (1, 1): (2, 0),
    (1, 2): (2, 4),
    (1, 3): (4, 2),
    (1, 4): (2, 2),
    (2, 0): (0, 0),
    (2, 1): (3, 2),
    (2, 2): (4, 3),
    (2, 3): (3, 0),
    (2, 4): (3, 4),
    (3, 0): (1, 0),
    (3, 1): (2, 3),
    (3, 2): (3, 3),
    (3, 3): (4, 4),
    (3, 4): (0, 2),
    (4, 0): (3, 1),
    (4, 1): (1, 2),
    (4, 2): (1, 3),
    (4, 3): (0, 4),
    (4, 4): (4, 0),
}


def reconstruct_image():
    """
    Reassembles the scrambled image based on the MAPPING.
    """
    print(f"Loading scrambled image: {SCRAMBLED_IMAGE_FILE}")
    try:
        # Open the scrambled image
        scrambled_img = Image.open(SCRAMBLED_IMAGE_FILE)
    except FileNotFoundError:
        print(f"ERROR: File not found: {SCRAMBLED_IMAGE_FILE}", file=sys.stderr)
        print("Please make sure the image is in the same directory as the script.", file=sys.stderr)
        return
    except Exception as e:
        print(f"ERROR: Could not open image. Is it a valid .webp file? {e}", file=sys.stderr)
        return

    # Create a new, blank canvas for the reconstructed image
    # We use 'RGBA' to ensure transparency is handled correctly if present
    reconstructed_img = Image.new('RGBA', (IMAGE_WIDTH, IMAGE_HEIGHT))
    print(f"Created new {IMAGE_WIDTH}x{IMAGE_HEIGHT} canvas for reconstruction.")

    if len(MAPPING) != 25:
        print(f"WARNING: Your MAPPING has {len(MAPPING)} entries. It should have 25.")
        print("This may result in an incomplete image.")
        if len(MAPPING) < 1:
            return

    print("Reconstructing image piece by piece...")

    # Loop through all 25 pieces in the MAPPING
    for (current_row, current_col), (original_row, original_col) in MAPPING.items():
        
        # 1. Calculate the coordinates of the piece in the SCRAMBLED image
        current_x0 = current_col * PIECE_SIZE
        current_y0 = current_row * PIECE_SIZE
        current_x1 = current_x0 + PIECE_SIZE
        current_y1 = current_y0 + PIECE_SIZE
        
        # Define the crop box for the scrambled piece
        box_to_crop = (current_x0, current_y0, current_x1, current_y1)

        # 2. Crop the piece out
        try:
            piece = scrambled_img.crop(box_to_crop)
        except Exception as e:
            print(f"ERROR cropping piece at ({current_row}, {current_col}): {e}")
            continue

        # 3. Calculate the coordinates where the piece BELONGS in the ORIGINAL image
        original_x0 = original_col * PIECE_SIZE
        original_y0 = original_row * PIECE_SIZE
        
        # Define the paste box for the reconstructed image
        box_to_paste = (original_x0, original_y0)

        # 4. Paste the piece into its correct new location
        reconstructed_img.paste(piece, box_to_paste)

        # print(f"Moved piece from ({current_row}, {current_col}) -> ({original_row}, {original_col})")

    # 5. Save the final, reconstructed image
    try:
        reconstructed_img.save(RECONSTRUCTED_IMAGE_FILE, format="PNG")
        print("\n--- Reconstruction Complete! ---")
        print(f"Reconstructed image saved as: {RECONSTRUCTED_IMAGE_FILE}")
        print("This file can now be uploaded to the case management system.")
    except Exception as e:
        print(f"\nERROR: Could not save the final image: {e}", file=sys.stderr)

if __name__ == "__main__":
    try:
        from PIL import Image
    except ImportError:
        print("ERROR: The 'Pillow' library is not installed.", file=sys.stderr)
        print("Please install it by running: pip install Pillow", file=sys.stderr)
        sys.exit(1)
        
    reconstruct_image()

