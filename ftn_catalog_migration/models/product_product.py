from odoo import models, fields,api
from odoo import _
import requests
import base64
from io import BytesIO
from odoo.exceptions import  ValidationError
from . helpers import fetch_image
class ImportImage(models.Model):
    _inherit = "product.product"
    image_url = fields.Char(string="Product Image URL",help="Stores the image URL or local file path. The system fetches the image from this path and updates the product image.")
    @api.onchange('image_url')
    def image_import(self):
        image = self.image_url
        if image:
            try:
                # Fetch the image (URL or file)
                image_data = fetch_image(image)
                self.image_variant_1920 = image_data  # Attach image to the product
            except ValidationError as e:
                raise ValidationError(_("Error with import image %s") % str(e))
        else:
            self.image_variant_1920 = False