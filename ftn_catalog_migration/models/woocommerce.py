from odoo import models, fields, api
from woocommerce import API
import logging

_logger = logging.getLogger(__name__)

class ImportProductsWizard(models.TransientModel):
    _name = 'import.products.wizard'
    _description = 'Import WooCommerce Products'

    # Add WooCommerce connection fields if needed (optional)
    wc_url = fields.Char(string="WooCommerce URL")
    wc_consumer_key = fields.Char(string="Consumer Key")
    wc_consumer_secret = fields.Char(string="Consumer Secret")

    def import_woocommerce_products(self):
        Param = self.env['ir.config_parameter'].sudo()
        wc_url = Param.get_param("migration.wc_url")
        wc_consumer_key = Param.get_param("migration.wc_consumer_key")
        wc_consumer_secret = Param.get_param("migration.wc_consumer_secret")


        wcapi = API(
            url=wc_url,
            consumer_key=wc_consumer_key,
            consumer_secret=wc_consumer_secret,
            version="wc/v3"
        )

        def get_all_products(per_page=100):
            page = 1
            all_products = []

            while True:
                response = wcapi.get("products", params={"per_page": per_page, "page": page})
                data = response.json()
                if not data:
                    break
                all_products.extend(data)
                page += 1
            return all_products

        products = get_all_products()
        _logger.info(f"Retrieved {len(products)} products from WooCommerce")

        for product in products:
            # Skip if already imported by SKU
            if self.env['product.template'].search([('default_code', '=', product['sku'])]):
                continue

            # Create product template
            tmpl_vals = {
                'name': product['name'],
                'default_code': product['sku'],
                'type': 'consu',
                'is_storable': True,
                'sale_ok': True,
                'purchase_ok': True,
                'description': product.get('description'),
                'list_price': float(product['price']) if product.get('price') else 0.0,
                'description_sale': product.get('short_description')
            }
            product_tmpl = self.env['product.template'].create(tmpl_vals)

            # Attributes and values
            attribute_lines = []
            for attr in product.get('attributes', []):
                attr_name = attr['name']
                attr_values = attr['options']

                product_attribute = self.env['product.attribute'].search([('name', '=', attr_name)], limit=1)
                if not product_attribute:
                    continue  # Skip unknown attributes

                values = self.env['product.attribute.value'].search([
                    ('attribute_id', '=', product_attribute.id),
                    ('name', 'in', attr_values)
                ])

                if values:
                    attribute_lines.append((0, 0, {
                        'attribute_id': product_attribute.id,
                        'value_ids': [(6, 0, values.ids)]
                    }))

            if attribute_lines:
                product_tmpl.write({'attribute_line_ids': attribute_lines})
                product_tmpl._create_variant_ids()  # Generate variants

            # Update variant details if needed
            if product['type'] == 'variable':
                variations = wcapi.get(f"products/{product['id']}/variations").json()
                for variant in variations:
                    woo_values = set(attr['option'] for attr in variant['attributes'])

                    for v in product_tmpl.product_variant_ids:
                        odoo_values = set(
                            v.product_template_attribute_value_ids.mapped('product_attribute_value_id.name'))
                        if woo_values == odoo_values:
                            v.write({
                                'default_code': variant['sku'],
                                'lst_price': float(variant['regular_price']) if variant.get('regular_price') else 0.0
                            })
                            break
                        else:
                            _logger.warning(
                            f"No matching variant found for combination {woo_values} in product {product['name']}")

        return {'type': 'ir.actions.act_window_close'}
