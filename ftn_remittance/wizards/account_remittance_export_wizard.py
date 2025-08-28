from odoo import models, fields, _
from odoo.exceptions import UserError
import io
import xlsxwriter


class AccountRemittanceExportWizard(models.TransientModel):
    _name = "account.remittance.export.wizard"
    _description = "Export remittance"

    export_type = fields.Selection(
        [
            ("xlsx", "Xlsx"), 
        ],
        default="xlsx",
    )
    name = fields.Char(string="Name")
    filename = fields.Char(string="Filename")
    excel_file = fields.Binary(string="Excel file", attachment=True)
