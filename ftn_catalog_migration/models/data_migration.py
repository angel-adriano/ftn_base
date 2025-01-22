import xmlrpc.client
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class MigrationCategory(models.TransientModel):
    _name = 'migration.category'
    _description = 'Migration Categories'

    name = fields.Char(string='Category Name', required=True)
    external_id = fields.Char(string='Odoo 14 ID', required=True)
    product_count = fields.Integer(string='Product Count', default=0)
    selected = fields.Boolean(string='Select for Import', default=False)


class RetrieveCategoriesWizard(models.TransientModel):
    _name = 'retrieve.categories.wizard'
    _description = 'Retrieve Categories from Odoo 14'

    def retrieve_categories(self):
        # Fetch credentials from res.config.settings
        Param = self.env['ir.config_parameter'].sudo()
        odoo_14_url = Param.get_param("migration.odoo_14_url")
        odoo_14_db = Param.get_param("migration.odoo_14_db")
        odoo_14_username = Param.get_param("migration.odoo_14_username")
        odoo_14_password = Param.get_param("migration.odoo_14_password")

        if not all([odoo_14_url, odoo_14_db, odoo_14_username, odoo_14_password]):
            raise UserError(_("Please configure Odoo 14 connection settings in General Settings."))

        # Connect to Odoo 14
        try:
            common = xmlrpc.client.ServerProxy(f"{odoo_14_url}/xmlrpc/2/common")
            uid = common.authenticate(odoo_14_db, odoo_14_username, odoo_14_password, {})
            models_14 = xmlrpc.client.ServerProxy(f"{odoo_14_url}/xmlrpc/2/object")
        except Exception as e:
            raise UserError(_("Failed to connect to Odoo 14: %s") % str(e))

        # Fetch categories
        categories = models_14.execute_kw(
            odoo_14_db, uid, odoo_14_password, 'product.category', 'search_read',
            [],
            {'fields': ['name']}
        )

        # Clear existing temporary data
        self.env['migration.category'].search([]).unlink()

        # Store categories and product counts in the temporary model
        for category in categories:
            # Fetch product count for the category
            product_count = models_14.execute_kw(
                odoo_14_db, uid, odoo_14_password, 'product.template', 'search_count',
                [[('categ_id.id', '=', category['id'])]]
            )

            # Create category record in the transient model
            self.env['migration.category'].create({
                'name': category['name'],
                'external_id': category['id'],
                'product_count': product_count,
            })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Migration Categories',
            'res_model': 'migration.category',
            'view_mode': 'list',
            'target': 'new',
        }


class ImportCategoriesWizard(models.TransientModel):
    _name = 'import.categories.wizard'
    _description = 'Import Selected Categories'

    batch_size = fields.Integer(string='Batch Size', default=500)

    def import_categories(self):
        # Fetch credentials from res.config.settings
        Param = self.env['ir.config_parameter'].sudo()
        odoo_14_url = Param.get_param("migration.odoo_14_url")
        odoo_14_db = Param.get_param("migration.odoo_14_db")
        odoo_14_username = Param.get_param("migration.odoo_14_username")
        odoo_14_password = Param.get_param("migration.odoo_14_password")

        if not all([odoo_14_url, odoo_14_db, odoo_14_username, odoo_14_password]):
            raise UserError(_("Please configure Odoo 14 connection settings in General Settings."))

        # Log the connection details for debugging
        _logger.info("Connecting to Odoo 14 instance at %s with database %s", odoo_14_url, odoo_14_db)

        try:
            common = xmlrpc.client.ServerProxy(f"{odoo_14_url}/xmlrpc/2/common")
            uid = common.authenticate(odoo_14_db, odoo_14_username, odoo_14_password, {})
            models_14 = xmlrpc.client.ServerProxy(f"{odoo_14_url}/xmlrpc/2/object")
        except Exception as e:
            _logger.error("Failed to connect to Odoo 14: %s", str(e))
            raise UserError(_("Failed to connect to Odoo 14: %s") % str(e))

        # Import the selected category
        selected_categories = self.env['migration.category'].search([('selected', '=', True)])
        if not selected_categories:
            raise UserError(_("No categories selected for import."))

        for category in selected_categories:
            # Fetch all products for the category from Odoo 14
            product_templates = models_14.execute_kw(
                odoo_14_db, uid, odoo_14_password, 'product.template', 'search_read',
                [[('categ_id.id', '=', category.external_id)]],
                {
                    'fields': ['name', 'default_code', 'type', 'categ_id', 'uom_id', 'uom_po_id', 'available_in_pos',
                               'clave_producto', 'list_price', 'standard_price', 'image_1920', 'product_variant_ids',
                               'attribute_line_ids']
                }
            )

            if not product_templates:
                _logger.info("No products found for category '%s'", category.name)
                continue

            # Import products into Odoo 18
            for template in product_templates:
                _logger.info("Processing product: %s (Code: %s)", template['name'], template.get('default_code', 'N/A'))

                # Map category
                categ_name = template.get('categ_id', [None, None])[1]
                categ_id = self.env['product.category'].search([('name', '=', categ_name)], limit=1).id or \
                           self.env['product.category'].create({'name': categ_name}).id

                # Map unit of measure
                uom_name = template.get('uom_id', [None, None])[1]
                uom_id = self.env['uom.uom'].search([('name', '=', uom_name)], limit=1).id

                uom_po_name = template.get('uom_po_id', [None, None])[1]
                uom_po_id = self.env['uom.uom'].search([('name', '=', uom_po_name)], limit=1).id

                # Create product template in Odoo 18
                product_template = self.env['product.template'].create({
                    'name': template['name'],
                    'default_code': template['default_code'],
                    'type': 'consu',
                    'is_storable': template['type'] == 'product',
                    'categ_id': categ_id,
                    'uom_id': uom_id,
                    'uom_po_id': uom_po_id,
                    'available_in_pos': template['available_in_pos'],
                    'clave_producto': template['clave_producto'],
                    'list_price': template['list_price'],
                    'standard_price': template['standard_price'],
                    'image_1920': template['image_1920'],
                })
                _logger.info("Created product template: %s", product_template.name)

                # Assign attributes to the product template
                attribute_lines = []
                for attr_line_id in template['attribute_line_ids']:
                    attr_line_data = models_14.execute_kw(
                        odoo_14_db, uid, odoo_14_password, 'product.template.attribute.line', 'read',
                        [attr_line_id],
                        {'fields': ['attribute_id', 'value_ids']}
                    )[0]
                    attr_name = attr_line_data['attribute_id'][1]

                    # Map attribute in Odoo 18
                    attribute = self.env['product.attribute'].search([('name', '=', attr_name)], limit=1)
                    if not attribute:
                        attribute = self.env['product.attribute'].create({'name': attr_name})

                    # Map attribute values
                    value_ids = []
                    for value_id in attr_line_data['value_ids']:
                        value_data = models_14.execute_kw(
                            odoo_14_db, uid, odoo_14_password, 'product.attribute.value', 'read',
                            [value_id],
                            {'fields': ['name']}
                        )[0]
                        value_name = value_data['name']

                        attribute_value = self.env['product.attribute.value'].search([
                            ('name', '=', value_name),
                            ('attribute_id', '=', attribute.id)
                        ], limit=1)
                        if not attribute_value:
                            attribute_value = self.env['product.attribute.value'].create({
                                'name': value_name,
                                'attribute_id': attribute.id,
                            })
                        value_ids.append(attribute_value.id)

                    # Add attribute line
                    attribute_lines.append((0, 0, {
                        'attribute_id': attribute.id,
                        'value_ids': [(6, 0, value_ids)],
                    }))

                if attribute_lines:
                    product_template.write({'attribute_line_ids': attribute_lines})

                _logger.info("Assigned attributes to product template: %s", product_template.name)

    def import_boms(self):
        # Fetch credentials from res.config.settings
        Param = self.env['ir.config_parameter'].sudo()
        odoo_14_url = Param.get_param("migration.odoo_14_url")
        odoo_14_db = Param.get_param("migration.odoo_14_db")
        odoo_14_username = Param.get_param("migration.odoo_14_username")
        odoo_14_password = Param.get_param("migration.odoo_14_password")

        if not all([odoo_14_url, odoo_14_db, odoo_14_username, odoo_14_password]):
            raise UserError(_("Please configure Odoo 14 connection settings in General Settings."))

        # Connect to Odoo 14
        try:
            common = xmlrpc.client.ServerProxy(f"{odoo_14_url}/xmlrpc/2/common")
            uid = common.authenticate(odoo_14_db, odoo_14_username, odoo_14_password, {})
            models_14 = xmlrpc.client.ServerProxy(f"{odoo_14_url}/xmlrpc/2/object")
        except Exception as e:
            raise UserError(_("Failed to connect to Odoo 14: %s") % str(e))

        # Fetch BOMs
        boms = models_14.execute_kw(
            odoo_14_db, uid, odoo_14_password, 'mrp.bom', 'search_read',
            [],
            {'fields': ['product_tmpl_id', 'product_id', 'bom_line_ids', 'product_qty', 'type']}
        )

        _logger.info("Retrieved %d BOMs from Odoo 14.", len(boms))

        for bom in boms:
            product = None
            if bom['product_id']:
                product_name = bom['product_id'][1]
                if ' (' in product_name:
                    template_name, variant = product_name.rsplit(' (', 1)
                    variant = variant.rstrip(')')
                else:
                    template_name, variant = product_name, ''
                product_template = self.env['product.template'].search([('name', '=', template_name)], limit=1)
                if product_template:
                    product = self.env['product.product'].search([
                        ('product_tmpl_id', '=', product_template.id),
                        ('product_template_variant_value_ids.name', 'in', variant.split(', '))
                    ], limit=1)
                if not product:
                    _logger.warning("Product '%s' not found in Odoo 18. Skipping BOM.", product_name)
                    continue
            else:
                product_tmpl_name = bom['product_tmpl_id'][1]
                product_template = self.env['product.template'].search([('name', '=', product_tmpl_name)], limit=1)
                if not product_template:
                    _logger.warning("Product template '%s' not found in Odoo 18. Skipping BOM.", product_tmpl_name)
                    continue
                product = product_template.product_variant_id

            new_bom = self.env['mrp.bom'].create({
                'product_tmpl_id': product.product_tmpl_id.id,
                'product_id': product.id,
                'product_qty': bom['product_qty'],
                'type': bom['type'],
            })

            bom_lines = models_14.execute_kw(
                odoo_14_db, uid, odoo_14_password, 'mrp.bom.line', 'search_read',
                [[('id', 'in', bom['bom_line_ids'])]],
                {'fields': ['product_id', 'product_qty', 'product_uom_id', 'bom_product_template_attribute_value_ids']}
            )

            for bom_line in bom_lines:
                line_product_name = bom_line['product_id'][1]
                if ' (' in line_product_name:
                    line_template_name, line_variant = line_product_name.rsplit(' (', 1)
                    line_variant = line_variant.rstrip(')')
                    line_template = self.env['product.template'].search([('name', '=', line_template_name)], limit=1)
                    line_product = self.env['product.product'].search([
                        ('product_tmpl_id', '=', line_template.id),
                        ('product_template_variant_value_ids.name', 'in', line_variant.split(', '))
                    ], limit=1)
                else:
                    line_template_name, line_variant = line_product_name, ''
                    line_template = self.env['product.template'].search([('name', '=', line_template_name)], limit=1)
                    line_product = self.env['product.product'].search([
                        ('product_tmpl_id', '=', line_template.id)
                    ], limit=1)

                if not line_product:
                    _logger.warning("BOM Line product '%s' not found in Odoo 18. Skipping line.", line_product_name)
                    continue

                uom_name = bom_line.get('product_uom_id', [None, None])[1]
                uom_id = self.env['uom.uom'].search([('name', '=', uom_name)], limit=1).id

                self.env['mrp.bom.line'].create({
                    'bom_id': new_bom.id,
                    'product_id': line_product.id,
                    'product_qty': bom_line['product_qty'],
                    'product_uom_id': uom_id,
                    # 'bom_product_template_attribute_value_ids': [
                    #     (6, 0, bom_line.get('bom_product_template_attribute_value_ids', []))],
                })

            _logger.info("Created BOM for product: %s.", product.name)



