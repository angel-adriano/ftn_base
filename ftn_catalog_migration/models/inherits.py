from odoo import models, fields, api
import logging
import xmlrpc.client

_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def import_price_from_odoo14(self):
        # Remote Odoo 14 server credentials
        Param = self.env['ir.config_parameter'].sudo()
        url = Param.get_param("migration.odoo_14_url")
        db = Param.get_param("migration.odoo_14_db")
        username = Param.get_param("migration.odoo_14_username")
        password = Param.get_param("migration.odoo_14_password")

        try:
            # Setup XML-RPC connection
            common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
            uid = common.authenticate(db, username, password, {})
            models14 = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        except Exception as e:
            _logger.error(f"Connection error to Odoo 14: {e}")
            return

        for product in self:
            domain = []
            matched_field = ''

            if product.barcode:
                domain = [('barcode', '=', product.barcode)]
                matched_field = 'barcode'
            elif product.default_code:
                domain = [('default_code', '=', product.default_code)]
                matched_field = 'default_code'
            elif product.name:
                domain = [('name', '=', product.name)]
                matched_field = 'name'
            else:
                _logger.warning(f"Skipping product {product.id} — no identifier (barcode, default_code, name)")
                continue

            try:
                result = models14.execute_kw(
                    db, uid, password,
                    'product.template', 'search_read',
                    [domain],
                    {'fields': ['list_price', 'standard_price'], 'limit': 1}
                )
                if result:
                    data = result[0]
                    product.list_price = data.get('list_price', 0.0)
                    product.standard_price = data.get('standard_price', 0.0)
                    _logger.info(
                        f"Updated price for product {product.id} using {matched_field}: {result[0]['list_price']}"
                    )
                else:
                    _logger.warning(f"No match found for product {product.id} using {matched_field}: {domain}")
            except Exception as e:
                _logger.error(f"Error fetching product {product.id} from Odoo 14: {e}")
