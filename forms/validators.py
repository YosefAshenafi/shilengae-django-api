from rest_framework.exceptions import ValidationError

MEGABYTE_LIMIT = 2

def image_validator(image):
    filesize = image.size

    if filesize > MEGABYTE_LIMIT * 1024 * 1024:
        raise ValidationError(f"Please keep image size under {MEGABYTE_LIMIT}MB")