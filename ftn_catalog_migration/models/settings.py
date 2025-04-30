from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    odoo_14_url = fields.Char(string="Odoo 14 URL", config_parameter="migration.odoo_14_url")
    odoo_14_db = fields.Char(string="Odoo 14 Database", config_parameter="migration.odoo_14_db")
    odoo_14_username = fields.Char(string="Odoo 14 Username", config_parameter="migration.odoo_14_username")
    odoo_14_password = fields.Char(string="Odoo 14 Password", config_parameter="migration.odoo_14_password")

    wc_url = fields.Char(string="URL WooCommerce", config_parameter="migration.wc_url")
    wc_consumer_key = fields.Char(string="Consumer Key", config_parameter="migration.wc_consumer_key")
    wc_consumer_secret = fields.Char(string="Consumer Secret", config_parameter="migration.wc_consumer_secret")
