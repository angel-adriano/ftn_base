from odoo import models, fields, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger("-----------------------_" + __name__)


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    remittance_payment = fields.Boolean(string="Remesa")
    type = fields.Selection([
        ('supplier', 'Proveedores'),
        ('expense', 'Gastos y reembolsos'),
        ('bonos', 'Bonos')])

    def _init_payments(self, to_process, edit_mode=False):
        ctx = self.env.context
        remittance_id = ctx.get("remittance_id")

        # Check for remittance payment logic
        if self.remittance_payment:
            remittance_lines = ctx.get("remittance_lines", [])
            if remittance_lines:
                line_ids = self.env["account.remittance.line"].browse(remittance_lines)

                # Process each remittance line and update payment values
                for vals, remittance_line in zip(to_process, line_ids):
                    batch_vals = vals.get("batch", {}).get("key_values", {})
                    vals = vals.get("create_vals", {})
                    balance = remittance_line.amount_to_pay
                    vals["amount"] = balance
                    vals["remittance_id"] = remittance_id
                    remittance_line.line_stage = 'done'
                    remittance_line.amount_paid = balance


                # Call the super method to execute the payment creation
                payments = super(AccountPaymentRegister, self)._init_payments(to_process, edit_mode=False)

                # Update the remittance stage if context has remittance_id
                if remittance_id:
                    remittance = self.env["account.remittance"].browse(remittance_id)
                    if remittance:
                        stage_id = self.env.ref("ftn_remittance.stage_4")
                        remittance.write({"stage_id": stage_id.id})

                return payments

        # Include remittance_id in standard behavior if it exists
        if remittance_id:
            for vals in to_process:
                create_vals = vals.get('create_vals', {})
                create_vals['remittance_id'] = remittance_id
                vals['create_vals'] = create_vals

        # Fallback to the standard behavior for non-remittance payments
        payments = super(AccountPaymentRegister, self)._init_payments(to_process, edit_mode)

        # Add the additional remittance stage update in fallback scenario
        if remittance_id:
            remittance = self.env["account.remittance"].browse(remittance_id)
            if remittance:
                stage_id = self.env.ref("ftn_remittance.stage_4")
                remittance.write({"stage_id": stage_id.id})

        return payments

