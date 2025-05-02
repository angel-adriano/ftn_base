import base64
import requests
from odoo import _
from odoo.exceptions import ValidationError

def fetch_image(image_source):
    """Fetch image from URL or local file path and return as base64."""
    
    if isinstance(image_source, str) and image_source.startswith(('http://', 'https://')):
        # Fetch image from URL
        try:
            response = requests.get(image_source)
            if response.status_code == 200:
                # Return the image as base64 encoded string
                return base64.b64encode(response.content)
            else:
                raise ValidationError(_("Failed to fetch image from URL: %s. Please check the URL and try again.") % image_source)
        except requests.exceptions.RequestException as e:
            raise ValidationError(_("An error occurred while fetching the image from the URL: %s. Please ensure the URL is correct.") % str(e))
    elif isinstance(image_source,str):
        # Fetch image from local file path
        try:
            with open(image_source, "rb") as file:
                return base64.b64encode(file.read())
        except FileNotFoundError:
            raise ValidationError(_("File not found at path: %s. Please verify the file path and try again.") % image_source)
        except Exception as e:
            raise ValidationError(_("An unexpected error occurred while processing the file: %s. Please try again.") % str(e))
    else:
        raise ValidationError(_("Invalid image source. Please provide a valid URL or local file path."))