from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import date


class AccountMove(models.Model):
    _inherit = "account.move"

    remittance_id = fields.Many2one("account.remittance", string="Remittance")
    ready_to_pay = fields.Boolean(string="Lista para pago")
    uuid_reconciled = fields.Boolean(string="XML Validado")
    supplier_uuid = fields.Char(string="UUID")
    xml_id = fields.Many2one('ir.attachment', string="Adjunto XML")
    analytic_account_id = fields.Many2one('account.analytic.account',string="Analytic Account", compute="_compute_analytic_account_id",store=True)
    analytic_distribution = fields.Json(compute="_compute_analytic_distribution",inverse="_inverse_analytic_distribution",store=True)
    next_due_date = fields.Date(string="Next Due Date", compute="_compute_next_due", store=True)
    next_due_amount = fields.Monetary(string="Next Due Amount", currency_field='currency_id',
                                      compute="_compute_next_due", store=True)

    @api.depends('state', 'line_ids', 'amount_residual')
    def _compute_next_due(self):
        today = date.today()
        for move in self:
            if move.move_type in ('out_invoice', 'out_refund'):
                due_lines = move.line_ids.filtered(lambda l: (
                        l.date_maturity and
                        l.date_maturity <= today and
                        l.amount_residual > 0 and
                        l.display_type == 'payment_term'
                ))
            elif move.move_type in ('in_invoice', 'in_refund'):
                due_lines = move.line_ids.filtered(lambda l: (
                        l.date_maturity and
                        l.date_maturity <= today and
                        l.amount_residual < 0 and
                        l.display_type == 'payment_term'
                ))
            else:
                move.next_due_date = False
                move.next_due_amount = 0.0
                continue

            if due_lines:
                earliest_date = min(due_lines.mapped('date_maturity'))
                relevant_lines = due_lines.filtered(lambda l: l.date_maturity == earliest_date)
                move.next_due_date = earliest_date
                move.next_due_amount = abs(sum(relevant_lines.mapped('amount_residual')))
            else:
                move.next_due_date = False
                move.next_due_amount = 0.0

    def validate_sat_sync(self):
        for record in self:
            if record.l10n_mx_edi_cfdi_uuid_cusom:
                record.uuid_reconciled = True
            else:
                record.uuid_reconciled = False

    def match_supplier_xml(self):
        for record in self:
            if record.supplier_uuid:
                last_12_chars = record.supplier_uuid[-12:]

                XML_true = self.env['ir.attachment'].search([
                    ('cfdi_uuid', 'like', record.supplier_uuid),
                    ('rfc_tercero', '=', record.partner_id.vat)])
                XML_partial = self.env['ir.attachment'].search([
                    ('cfdi_uuid', 'like', last_12_chars),
                    ('rfc_tercero', '=', record.partner_id.vat)])

                if XML_true:
                    XML_true['res_id'] = record.id
                    XML_true['res_model'] = "account.move"
                    XML_true['creado_en_odoo'] = True
                    record['l10n_mx_edi_cfdi_uuid'] = XML_true.cfdi_uuid
                    record['uuid_reconciled'] = True
                    record['xml_id'] = XML_true.id
                elif XML_partial:
                    XML_partial['res_id'] = record.id
                    XML_partial['res_model'] = "account.move"
                    XML_partial['creado_en_odoo'] = True
                    record['l10n_mx_edi_cfdi_uuid'] = XML_partial.cfdi_uuid
                    record['uuid_reconciled'] = True
                    record['xml_id'] = XML_partial.id
                else:
                    raise UserError(
                        "El UUID no existe en la lista de XMLs descagados, o el RFC no coincide favor de validar")

            else:
                raise UserError(
                    "Es necesario especificar el UUID de la factura del proveedor para poder conciliar")



    @api.depends("line_ids.analytic_distribution")
    def _compute_analytic_distribution(self):
        """Compute the analytic distribution at the move level based on its move lines."""
        for move in self:
            if move.line_ids:
                # Convert dictionaries to tuples to make them hashable
                distributions = {tuple(line.analytic_distribution.items()) for line in move.line_ids if
                                 line.analytic_distribution}
                if len(distributions) == 1:
                    move.analytic_distribution = dict(distributions.pop())
                elif len(distributions) > 1:
                    move.analytic_distribution = {}
                else:
                    move.analytic_distribution = move.line_ids[0].analytic_distribution if move.line_ids else {}

    def _inverse_analytic_distribution(self):
        """Apply the move-level analytic distribution to all move lines."""
        for move in self:
            if move.analytic_distribution:
                move.line_ids.write({"analytic_distribution": move.analytic_distribution})

    @api.depends("analytic_distribution")
    def _compute_analytic_account_id(self):
        """Infer the analytic_account_id from the analytic_distribution if only one is present."""
        for move in self:
            if move.analytic_distribution:
                analytic_ids = list(move.analytic_distribution.keys())
                move.analytic_account_id = int(analytic_ids[0]) if len(analytic_ids) == 1 else False

    @api.onchange("analytic_account_id")
    def _onchange_analytic_account_id(self):
        """Update analytic_distribution to reflect 100% allocation when analytic_account_id is changed."""
        if self.analytic_account_id:
            self.analytic_distribution = {str(self.analytic_account_id.id): 100.0}
            self.line_ids.write({"analytic_distribution": self.analytic_distribution})


