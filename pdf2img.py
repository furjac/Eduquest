from pdf2image import convert_from_path

# Convert PDF to images
images = convert_from_path("sample.pdf", dpi=300)

# Save each page as an image
for i, image in enumerate(images):
    image.save(f"page_{i+1}.png", "PNG")
