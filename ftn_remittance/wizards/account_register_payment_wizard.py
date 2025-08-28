from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountRegisterPaymentWizard(models.TransientModel):
    _name = "account.register.payment.wizard"
    _description = "Register payment"

    amount_to_pay = fields.Float(string="Amount to pay")

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if "amount_to_pay" in fields_list:
            if self._context.get("active_model") == "account.remittance.line":
                remittance_line = self.env["account.remittance.line"].browse(
                    self._context.get("active_ids")
                )
                res["amount_to_pay"] = remittance_line.amount_to_pay
        return res

    def do_assign_payment(self):
        if self.amount_to_pay <= 0:
            raise UserError(_("Your amount to pay must be greater than zero"))
        ctx = self.env.context
        model = ctx["active_model"]
        active_id = ctx["active_id"]
        remittance_line = self.env[model].browse(active_id)
        if self.amount_to_pay > remittance_line.amount_to_pay:
            raise UserError(
                _(
                    "Your amount to pay must be less than %s"
                    % remittance_line.amount_to_pay
                )
            )
        if remittance_line:
            remittance_line.write({"amount_paid": self.amount_to_pay})
