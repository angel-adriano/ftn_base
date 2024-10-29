from odoo import models, fields, api
import base64
from io import BytesIO
import zipfile


class AccountMove(models.Model):
    _inherit = 'account.move'

    def download_attachments(self):
        # Create a byte stream to hold the zip file
        zip_stream = BytesIO()
        with zipfile.ZipFile(zip_stream, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Iterate through all selected account.move records
            for record in self:
                # Get all attachments related to the account.move
                attachments = record.message_main_attachment_id | record.attachment_ids
                for attachment in attachments:
                                                                                
                                                                
                    # Add each attachment to the zip file
                    zip_file.writestr(attachment.name, base64.b64decode(attachment.datas))

        # Reset the byte stream position
        zip_stream.seek(0)

        # Create a new attachment to hold the zip file
        zip_attachment = self.env['ir.attachment'].create({
            'name': 'account_move_attachments.zip',
            'type': 'binary',
            'datas': base64.b64encode(zip_stream.read()),
            'store_fname': 'account_move_attachments.zip',
            'res_model': 'account.move',
            'res_id': self[0].id,  # Use the first record to attach the zip file
            'mimetype': 'application/zip'
        })

        # Return an action to download the zip file
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % zip_attachment.id,
            'target': 'self',
        }
