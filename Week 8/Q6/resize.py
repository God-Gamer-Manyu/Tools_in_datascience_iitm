from PIL import Image, ImageOps

# Choose high-quality resampling in a Pillow-version-safe way
try:
    RESAMPLE = Image.Resampling.LANCZOS
except AttributeError:
    RESAMPLE = Image.LANCZOS

def resize_exact(input_path, output_path, width, height, resample=RESAMPLE):
    """Resize (stretch) to exactly width x height — aspect ratio NOT preserved."""
    img = Image.open(input_path)
    out = img.resize((width, height), resample=resample)
    out.save(output_path)

def resize_fit(input_path, output_path, width, height, bg_color=(255,255,255), resample=RESAMPLE):
    """
    Resize to fit inside (width, height), preserving aspect ratio.
    The result is centered on a background of `bg_color` and has exact dimensions.
    """
    img = Image.open(input_path)
    # Convert to RGBA if image has transparency, else RGB
    mode = 'RGBA' if img.mode in ('RGBA', 'LA') else 'RGB'
    img = img.convert(mode)

    # Create background of exact size
    background = Image.new(mode, (width, height), color=bg_color + (0,) if mode=='RGBA' and len(bg_color)==3 else bg_color)

    # Resize preserving aspect ratio (thumbnail modifies in place)
    img.thumbnail((width, height), resample=resample)

    # Paste centered
    x = (width - img.width) // 2
    y = (height - img.height) // 2
    if mode == 'RGBA':
        background.paste(img, (x, y), img)
    else:
        background.paste(img, (x, y))
    # convert back to RGB if you prefer non-alpha PNG/JPEG
    if background.mode == 'RGBA' and output_path.lower().endswith(('.jpg', '.jpeg')):
        background = background.convert('RGB')
    background.save(output_path)

def resize_fill(input_path, output_path, width, height, resample=RESAMPLE):
    """
    Resize to exactly (width, height) by preserving aspect ratio and cropping
    any overflow. Equivalent to CSS `object-fit: cover`.
    """
    img = Image.open(input_path)
    # ImageOps.fit resizes and crops to the requested size
    fitted = ImageOps.fit(img, (width, height), method=resample, centering=(0.5, 0.5))
    # Save (Pillow will keep mode appropriate for format)
    fitted.save(output_path)

# Example usage:
if __name__ == '__main__':
    input_file = 'Week 8/Q6/chart.png'   # change as needed
    # resize_exact(input_file, 'out_exact.png', 512, 512)
    resize_fit(input_file,   './Week 8/Q6/out_fit.png',   512, 512, bg_color=(255,255,255))
    # resize_fill(input_file,  'out_fill.png',  512, 512)
    print('Saved out_exact.png, out_fit.png, out_fill.png')