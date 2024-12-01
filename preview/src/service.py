from PIL import Image
from connectors.s3 import s3
import tempfile

MAX_SIZE = (150, 150)


def reduce_image_size(input_path,
                      output_path,
                      max_width=None,
                      max_height=None,
                      quality=20):
    try:
        # Open the image
        with Image.open(input_path) as img:
            # Get original dimensions
            original_width, original_height = img.size
            aspect_ratio = original_width / original_height

            # Determine new dimensions
            if max_width and max_height:
                # Calculate the maximum possible size within the given width and height
                new_width = max_width
                new_height = max_height
                # Adjust to maintain aspect ratio
                if (new_width / new_height) > aspect_ratio:
                    new_width = int(new_height * aspect_ratio)
                else:
                    new_height = int(new_width / aspect_ratio)
            elif max_width:
                new_width = max_width
                new_height = int(new_width / aspect_ratio)
            elif max_height:
                new_height = max_height
                new_width = int(new_height * aspect_ratio)
            else:
                raise ValueError("Either max_width or max_height must be provided.")

            # Ensure new dimensions are not larger than original
            new_width = min(new_width, original_width)
            new_height = min(new_height, original_height)

            # Resize the image
            img = img.resize((new_width, new_height), Image.ANTIALIAS)

            # Save the image
            img.save(output_path, quality=quality)

            return new_width, new_height

    except Exception as e:
        print(f"An error occurred: {e}")


def create_preview_image(s3_path: str) -> None:
    with tempfile.TemporaryDirectory(prefix="resize") as tmp:
        # Read file
        input_file = tempfile.NamedTemporaryFile(mode="wb+", suffix=f"_{s3_path}", dir=tmp)
        s3.download_file(input_file, s3_path)

        # Create preview image
        preview_s3_path = f"preview/{s3_path}"
        img = Image.open(input_file)
        img.thumbnail(MAX_SIZE, Image.LANCZOS)
        img.save(input_file.name)

        # Upload preview image to s3
        s3.upload_file(input_file, preview_s3_path)
        input_file.close()
