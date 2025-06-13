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
                    {'fields': [
                        'list_price', 'standard_price', 'taxes_id', 'supplier_taxes_id'], 'limit': 1}
                )
                if result:
                    data = result[0]
                    product.list_price = data.get('list_price', 0.0)
                    product.standard_price = data.get('standard_price', 0.0)

                    # Handle taxes
                    odoo14_tax_ids = data.get('taxes_id', [])
                    if odoo14_tax_ids:
                        # Get tax names from Odoo 14
                        tax_names = models14.execute_kw(
                            db, uid, password,
                            'account.tax', 'read',
                            [odoo14_tax_ids], {'fields': ['name']}
                        )

                        # Search matching tax names in Odoo 18
                        matched_tax_ids = []
                        for tax in tax_names:
                            tax_name = tax['name']
                            local_tax = self.env['account.tax'].search([('name', '=', tax_name)], limit=1)
                            if local_tax:
                                matched_tax_ids.append(local_tax.id)
                            else:
                                _logger.warning(f"Tax '{tax_name}' not found in Odoo 18")

                        if matched_tax_ids:
                            product.taxes_id = [(6, 0, matched_tax_ids)]
                            _logger.info(f"Updated taxes for {product.name} to {matched_tax_ids}")
                        else:
                            _logger.warning(f"No matching taxes found for {product.name}, taxes not updated")

                    odoo14_supplier_tax_ids = data.get('supplier_taxes_id', [])
                    if odoo14_supplier_tax_ids:
                        matched_supplier_tax_ids = []
                        if odoo14_supplier_tax_ids:
                            supplier_tax_names = models14.execute_kw(
                                db, uid, password,
                                'account.tax', 'read',
                                [odoo14_supplier_tax_ids], {'fields': ['name']}
                            )
                            for tax in supplier_tax_names:
                                local_tax = self.env['account.tax'].search([('name', '=', tax['name'])], limit=1)
                                if local_tax:
                                    matched_supplier_tax_ids.append(local_tax.id)
                                else:
                                    _logger.warning(f"[Supplier Tax] '{tax['name']}' not found in Odoo 18")

                        if matched_supplier_tax_ids:
                            product.supplier_taxes_id = [(6, 0, matched_supplier_tax_ids)]
                            _logger.info(f"Updated supplier taxes for {product.name} to {matched_supplier_tax_ids}")
                        else:
                            _logger.warning(f"No matching supplier taxes found for {product.name}")
                else:
                    _logger.warning(f"No match found for product {product.id} using {matched_field}: {domain}")
            except Exception as e:
                _logger.error(f"Error fetching product {product.id} from Odoo 14: {e}")

    def import_book_metadata_from_odoo14(self):
        # Remote Odoo 14 server credentials
        Param = self.env['ir.config_parameter'].sudo()
        url = Param.get_param("migration.odoo_14_url")
        db = Param.get_param("migration.odoo_14_db")
        username = Param.get_param("migration.odoo_14_username")
        password = Param.get_param("migration.odoo_14_password")

        try:
            common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
            uid = common.authenticate(db, username, password, {})
            models14 = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        except Exception as e:
            _logger.error(f"Connection to Odoo 14 failed: {e}")
            return

        for product in self:
            # Match priority: barcode > default_code > name
            domain = []
            if product.barcode:
                domain = [('barcode', '=', product.barcode)]
            elif product.default_code:
                domain = [('default_code', '=', product.default_code)]
            elif product.name:
                domain = [('name', '=', product.name)]
            else:
                _logger.warning(f"No identifier to match product {product.id}")
                continue

            try:
                result = models14.execute_kw(
                    db, uid, password,
                    'product.template', 'search_read',
                    [domain],
                    {'fields': [
                        'autor', 'editorial', 'sello_editorial', 'sinopsis', 'tematica',
                        'titulo', 'publish_year', 'edicion', 'paginas', 'colleccion',
                        'idioma', 'categoria', 'ubicacion'
                    ], 'limit': 1}
                )

                if result:
                    data = result[0]
                    product.write({
                        'autor': data.get('autor'),
                        'editorial': data.get('editorial'),
                        'sello_editorial': data.get('sello_editorial'),
                        'sinopsis': data.get('sinopsis'),
                        'tematica': data.get('tematica'),
                        'titulo': data.get('titulo'),
                        'publish_year': data.get('publish_year'),
                        'edicion': data.get('edicion'),
                        'paginas': data.get('paginas'),
                        'colleccion': data.get('colleccion'),
                        'idioma': data.get('idioma'),
                        'categoria': data.get('categoria'),
                        'ubicacion': data.get('ubicacion'),
                    })
                    _logger.info(f"Metadata updated for product {product.id}")
                else:
                    _logger.warning(f"No match found for {product.name} in Odoo 14")

            except Exception as e:
                _logger.error(f"Failed to fetch metadata for {product.id}: {e}")

    def import_book_metadata_from_odoo14(self):
        # Remote Odoo 14 server credentials
        Param = self.env['ir.config_parameter'].sudo()
        url = Param.get_param("migration.odoo_14_url")
        db = Param.get_param("migration.odoo_14_db")
        username = Param.get_param("migration.odoo_14_username")
        password = Param.get_param("migration.odoo_14_password")

        try:
            common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
            uid = common.authenticate(db, username, password, {})
            models14 = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        except Exception as e:
            _logger.error(f"Connection to Odoo 14 failed: {e}")
            return

        for product in self:
            # Match priority: barcode > default_code > name
            domain = []
            if product.barcode:
                domain = [('barcode', '=', product.barcode)]
            elif product.default_code:
                domain = [('default_code', '=', product.default_code)]
            elif product.name:
                domain = [('name', '=', product.name)]
            else:
                _logger.warning(f"No identifier to match product {product.id}")
                continue

            try:
                result = models14.execute_kw(
                    db, uid, password,
                    'product.template', 'search_read',
                    [domain],
                    {'fields': [
                        'autor', 'editorial', 'sello_editorial', 'sinopsis', 'tematica',
                        'titulo', 'publish_year', 'edicion', 'paginas', 'colleccion',
                        'idioma', 'categoria', 'ubicacion'
                    ], 'limit': 1}
                )

                if result:
                    data = result[0]
                    product.write({
                        'autor': data.get('autor'),
                        'editorial': data.get('editorial'),
                        'sello_editorial': data.get('sello_editorial'),
                        'sinopsis': data.get('sinopsis'),
                        'tematica': data.get('tematica'),
                        'titulo': data.get('titulo'),
                        'publish_year': data.get('publish_year'),
                        'edicion': data.get('edicion'),
                        'paginas': data.get('paginas'),
                        'colleccion': data.get('colleccion'),
                        'idioma': data.get('idioma'),
                        'categoria': data.get('categoria'),
                        'ubicacion': data.get('ubicacion'),
                    })
                    _logger.info(f"Metadata updated for product {product.id}")
                else:
                    _logger.warning(f"No match found for {product.name} in Odoo 14")

            except Exception as e:
                _logger.error(f"Failed to fetch metadata for {product.id}: {e}")
