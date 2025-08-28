from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError
import io
import xlsxwriter
import base64
from datetime import timedelta, datetime


class AccountRemittance(models.Model):
    _name = "account.remittance"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"
    _description = "Account remittance"

    def action_execute_individual_payments(self):
        for line in self.line_ids.filtered(lambda l: l.ready_to_pay and l.invoice_id):
            invoice = line.invoice_id

            if line.amount_to_pay <= 0:
                continue

            register_payment = self.env['account.payment.register'].with_context(
                active_model='account.move',
                active_ids=[invoice.id],
                remittance_id=self.id
            ).create({
                'amount': line.amount_to_pay,
                'currency_id': invoice.currency_id.id,
                'payment_date': fields.Date.today(),
                'journal_id': self.journal_id.id,
                'payment_type': 'outbound' if invoice.is_outbound() else 'inbound',
                'partner_id': invoice.partner_id.id,
                'communication': invoice.name,
                'l10n_mx_edi_payment_method_id': 3,
            })

            action = register_payment.action_create_payments()
            payment_ids = action.get('res_ids') or []

            if payment_ids:
                self.env['account.payment'].browse(payment_ids).write({'remittance_id': self.id})

            # Mark the remittance line as paid
            line.line_stage = 'done'
            line.amount_paid = line.amount_to_pay

        # Move remittance to the next stage
        stage_id = self.env.ref("ftn_remittance.stage_4")
        self.write({"stage_id": stage_id.id})

    @api.returns("self")
    def _default_stage(self):
        return self.env.ref("ftn_remittance.stage_0")

    name = fields.Char('Name', tracking=True, default='/')
    journal_id = fields.Many2one('account.journal', string="Diario de Pago")

    def _compute_payment_count(self):
        for rem in self:
            rem.payment_count = self.env['account.payment'].search_count([('remittance_id', '=', rem.id)])

    def action_open_payments(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Payments',
            'view_mode': 'list,form',
            'res_model': 'account.payment',
            'domain': [('remittance_id', '=', self.id)],
            'context': {'default_remittance_id': self.id},
        }

    period = fields.Char(string="Period")
    project_id = fields.Many2one(
        comodel_name="account.analytic.account", string="Project"
    )
    payment_count = fields.Integer(string='Payment Count', compute='_compute_payment_count')

    responsible_id = fields.Many2one(comodel_name="res.users", string="Responsible")
    approver_id = fields.Many2one(comodel_name="res.users", string="Approver", tracking=True)
    approved_done = fields.Boolean(string="Approved", tracking=True)
    payer_id = fields.Many2one(
        comodel_name="res.users", string="Payer", tracking=True
    )
    initial_date = fields.Datetime(string="Initial date")
    final_date = fields.Datetime(string="Final date")
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Currency",
        default=lambda self: self.env.ref("base.MXN"),
    )
    currency_usd = fields.Many2one(
        comodel_name="res.currency",
        string="Currency USD",
        default=lambda self: self.env.ref("base.USD"),
    )
    total_mxn = fields.Monetary(
        string="Total MXN",
        currency_field="currency_id",
        compute="_compute_total",
        store=True,
    )
    total_usd = fields.Monetary(
        string="Total USD",
        currency_field="currency_usd",
        compute="_compute_total",
        store=True,
    )
    remittance_total = fields.Monetary(
        string="Remittance total",
        currency_field="currency_id",
        compute="_compute_total",
        store=True,
    )
    line_ids = fields.One2many('account.remittance.line', 'remittance_id', string='Lines')
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("posted", "Posted"),
            ("cancel", "Cancelled"),
        ],
        string="Status",
        readonly=True,
        copy=False,
        default="draft",
        tracking=True,
    )
    tag_ids = fields.Many2many(
        comodel_name="remittance.tag",
        relation="remittance_rag_remittance_rel",
        string="Remittance tag",
    )
    pay_account = fields.Many2one('res.partner.bank',string="Charge account", domain="[('partner_id', '=', 1)]")
    user_id = fields.Many2one(
        "res.users", string="User", default=lambda self: self.env.user.id
    )

    # invoice_ids = fields.One2many("account.move", "remittance_id", string="Invoices")
    stage_id = fields.Many2one(
        comodel_name="remittance.stage",
        string="Stage",
        tracking=True,
        group_expand="_read_group_stage_ids",
        default=_default_stage,
        copy=False,
    )
    current_approver = fields.Many2one('res.users', string="Aprobador actual")
    allow_approve = fields.Boolean(string='Puede aprobar', compute='allow_user_to_approve')

    def allow_user_to_approve(self):
        if self.current_approver == self.env.user:
            self.allow_approve = True
        else:
            self.allow_approve = False

    # Compute methods
    @api.depends("line_ids.currency_id", "line_ids.amount_total")
    def _compute_total(self):
        for remittance in self:
            total_usd = 0.0
            total_mxn = 0.0
            remittance_total = 0.0
            amount_total = 0.0
            if remittance.line_ids:
                for line_ids in remittance.line_ids:
                    usd_currency = self.env.ref("base.USD")
                    mxn_currency = self.env.ref("base.MXN")
                    if line_ids.currency_id.id == usd_currency.id:
                        total_usd += line_ids.amount_to_pay
                    elif line_ids.currency_id.id == mxn_currency.id:
                        total_mxn += line_ids.amount_to_pay
                    if total_usd > 0:
                        amount_total += remittance.currency_usd._convert(
                            total_usd,
                            remittance.currency_id,
                            line_ids.invoice_id.company_id,
                            line_ids.invoice_id.date,
                        )
                remittance_total = total_mxn + amount_total
                remittance.total_usd = total_usd
                remittance.total_mxn = total_mxn
                remittance.remittance_total = remittance_total

    # Action's button
    def action_register_payment(self):
        move_ids = [
            line.invoice_id.id
            for line in self.line_ids.filtered(lambda line: line.ready_to_pay)
        ]
        return {
            "name": _("Register Payment"),
            "res_model": "account.payment.register",
            "view_mode": "form",
            "context": {
                "active_model": "account.move",
                "active_ids": move_ids,
                'default_remittance_payment': True,
                'default_l10n_mx_edi_payment_method_id': 3,
                'default_analytic_account_id': self.project_id.id,
                "remittance_lines": self.line_ids.filtered(
                    lambda line: line.ready_to_pay
                ).ids,
                "default_amount": sum(
                    self.line_ids.filtered(lambda line: line.ready_to_pay).mapped(
                        "amount_to_pay"
                    )
                ),
                "remittance_id": self.id,
                "type": 'supplier',
            },
            "target": "new",
            "type": "ir.actions.act_window",
        }

    def action_generate_txt(self):
        records = self.line_ids.filtered(lambda line: line.ready_to_pay)
        filename = "REMESA %s.xlsx" % self.project_id.name
        xlsx_data = io.BytesIO()
        workbook = xlsxwriter.Workbook(xlsx_data)
        sheet = workbook.add_worksheet()
        header_format = workbook.add_format({"bold": True, "border": 1})
        header_row = [
            "CUENTA DE CARGO",
            "CUENTA DE ABONO",
            "DIVISA DE LA OPERACIÓN (MXN,USD,EUR)",
            "IMPORTE DE LA OPERACIÓN",
            "MOTIVO DE PAGO",
            "TITULAR DE LA CUENTA BANCARIA",
            "TIPO DE CUENTA (CLABE INTERBANCARIA)",
            "REFERENCIA NUMERICA",
            "DISPONIBILIDAD (H = hoy, M = Día siguiente)",
            "RFC",
            "IVA",
        ]
        for col, header in enumerate(header_row):
            sheet.write(0, col, header, header_format)

        for row_num, record in enumerate(records, start=1):
            row = [
                self.pay_account.acc_number,
                record.partner_bank_id.l10n_mx_edi_clabe,
                record.invoice_id.currency_id.name,
                record.amount_paid,
                record.description,
                record.invoice_id.partner_id.name,
                "",
                "",
                "",
                "",
                "",
            ]
            for col, value in enumerate(row):
                sheet.write(row_num, col, value)
        for col, header in enumerate(header_row):
            sheet.set_column(col, col, len(header) + 2)
        workbook.close()
        xlsx_data.seek(0)
        xlsx_binary = xlsx_data.getvalue()
        xlsx_base64 = base64.b64encode(xlsx_binary).decode()
        record = self.env["account.remittance.export.wizard"].create(
            {"excel_file": xlsx_base64, "filename": filename, "name": filename}
        )
        wizard = self.env.ref(
            "ftn_remittance.account_remittance_export_wizard_view_form"
        ).id
        ctx = dict()
        return {
            "name": _("Generate TXT file"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_id": record.id,
            "res_model": "account.remittance.export.wizard",
            "views": [(wizard, "form")],
            "view_id": wizard,
            "target": "new",
            "context": ctx,
        }

    def action_export_remittance_invoice_lines(self):
        self.ensure_one()
        filename = f"Reporte_fact_{self.name or 'Unnamed'}.xlsx"
        xlsx_data = io.BytesIO()
        workbook = xlsxwriter.Workbook(xlsx_data)
        sheet = workbook.add_worksheet("Lineas de fact")

        header_format = workbook.add_format({"bold": True, "border": 1})
        headers = [
            "Número", "Fecha de factura", "Partner", "Cuenta", "Cuenta analítica",
            "Producto", "Etiqueta", "Referencia", "Subtotal", "Importe adeudado", "Divisa"
        ]

        for col, header in enumerate(headers):
            sheet.write(0, col, header, header_format)

        row_num = 1
        for line in self.line_ids.mapped("invoice_id.invoice_line_ids"):
            sheet.write(row_num, 0, line.move_id.name or '')
            sheet.write(row_num, 1, str(line.move_id.invoice_date or ''))
            sheet.write(row_num, 2, line.partner_id.name or '')
            sheet.write(row_num, 3, line.account_id.name or '')
            sheet.write(row_num, 4, line.analytic_line_ids.account_id.name or '')
            sheet.write(row_num, 5, line.product_id.name or '')
            sheet.write(row_num, 6, line.name or '')
            sheet.write(row_num, 7, line.move_id.ref or '')
            sheet.write(row_num, 8, line.price_total or 0.0)
            sheet.write(row_num, 9, line.move_id.amount_residual or 0.0)
            sheet.write(row_num, 10, line.currency_id.name or '')
            row_num += 1

        for col in range(len(headers)):
            sheet.set_column(col, col, 20)

        workbook.close()
        xlsx_data.seek(0)
        xlsx_binary = xlsx_data.getvalue()
        xlsx_base64 = base64.b64encode(xlsx_binary).decode()

        wizard = self.env["account.remittance.export.wizard"].create({
            "excel_file": xlsx_base64,
            "filename": filename,
            "name": filename
        })

        return {
            "name": _("Invoice Line Report"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "account.remittance.export.wizard",
            "res_id": wizard.id,
            "target": "new",
        }

    def action_generate_txt_banregio(self):
        records = self.line_ids.filtered(lambda line: line.ready_to_pay)
        filename = "BRGIO %s.xlsx" % self.name
        xlsx_data = io.BytesIO()
        workbook = xlsxwriter.Workbook(xlsx_data)
        sheet = workbook.add_worksheet()
        header_format = workbook.add_format({"bold": True, "border": 1})
        header_row = [
            "OPERACION",
            "NOMBRE BENEFICIARIO",
            "CUENTA ORIGEN",
            "CUENTA DESTINO",
            "IMPORTE",
            "REFERENCIA",
            "CONCEPTO",
            "IVA",
            "DISPONIBILIDAD (H = hoy, M = Día siguiente)",
            "RFC",
            "IVA",
        ]
        for col, header in enumerate(header_row):
            sheet.write(0, col, header, header_format)

        for row_num, record in enumerate(records, start=1):
            row = [
                self.pay_account.acc_number,
                record.partner_bank_id.l10n_mx_edi_clabe,
                record.invoice_id.currency_id.name,
                record.amount_paid,
                record.description,
                record.invoice_id.partner_id.name,
                "",
                "",
                "",
                "",
                "",
            ]
            for col, value in enumerate(row):
                sheet.write(row_num, col, value)
        for col, header in enumerate(header_row):
            sheet.set_column(col, col, len(header) + 2)
        workbook.close()
        xlsx_data.seek(0)
        xlsx_binary = xlsx_data.getvalue()
        xlsx_base64 = base64.b64encode(xlsx_binary).decode()
        record = self.env["account.remittance.export.wizard"].create(
            {"excel_file": xlsx_base64, "filename": filename, "name": filename}
        )
        wizard = self.env.ref(
            "ftn_remittance.account_remittance_export_wizard_view_form"
        ).id
        ctx = dict()
        return {
            "name": _("Generate TXT file"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_id": record.id,
            "res_model": "account.remittance.export.wizard",
            "views": [(wizard, "form")],
            "view_id": wizard,
            "target": "new",
            "context": ctx,
        }

    def action_confirm(self):
        approver = self.env['res.partner'].search([('id', '=', self.approver_id.partner_id.id)])
        treasurer = self.env['res.partner'].search([('id', '=', self.payer_id.partner_id.id)])
        followers = approver+treasurer

        self.ensure_one()
        self.write({"stage_id": self.env.ref("ftn_remittance.stage_1").id})

        if self.name == '/':
            self.name = self.env['ir.sequence'].next_by_code('remittance_seq') or _('New')

        activity_vals = {
            'activity_type_id': 4,  # Reference to your activity type
            'summary': "Aprobar remesa",
            'res_id': self.id,
            'res_model_id': self.env['ir.model']._get(self._name).id,
            'date_deadline': fields.Date.today() + timedelta(days=1),  # Set your desired deadline
            'user_id': self.approver_id.id,  # Assign the activity to the follower's user
        }
        activity = self.env['mail.activity'].create(activity_vals)

        self.message_subscribe(followers.ids)
        self.current_approver = self.approver_id.id

        # Return the activity
        return activity

    def action_cancel(self):
        """Cancels the remittance."""
        self.ensure_one()
        self.write({"stage_id": self.env.ref("ftn_remittance.stage_5").id, "approved_done": False})

    def action_approve(self):
        """Approves the remittance if the current user is the approver."""
        self.ensure_one()
        if self.state != "draft":
            raise UserError("Only drafts can be approved.")
        # if self.stage_id != "to_approve":
        #     raise UserError(
        #         _(
        #             "To validate the approval flow it is necessary to confirm the remittance"
        #         )
        #     )
        # self.ensure_one()
        self._validate_approval()
        return True

    def _validate_approval(self):
        approver_user = self.env.user

        activities = self.env['mail.activity'].search([("res_id", "=", self.id), ('res_model', '=', self._name)])

        if self.approved_done:
            raise UserError(_("This remittance is already approved"))
        elif not self.approved_done and approver_user.id == self.approver_id.id:
            self.write(
                {
                    "approved_done": True,
                    "stage_id": self.env.ref("ftn_remittance.stage_3").id,
                }
            )
            for activity in activities:
                activity.unlink()
            display_msg = "Aprobado por " + str(approver_user.name)
            self.message_post(body=display_msg, partner_ids=[approver_user.partner_id.id])

            if self.payer_id.id != self.approver_id.id:
                activity_vals = {
                    'activity_type_id': 4,  # Reference to your activity type
                    'summary': "Ejecutar pago",
                    'res_id': self.id,
                    'res_model_id': self.env['ir.model']._get(self._name).id,
                    'date_deadline': fields.Date.today() + timedelta(days=1),  # Set your desired deadline
                    'user_id': self.payer_id.id,
                }
                activity = self.env['mail.activity'].create(activity_vals)
        else:
            raise UserError(_("Your user is not authorized to approve this remittance"))

    @api.model
    def _read_group_stage_ids(self, stages, domain, order=None):
        """Read group customization in order to display all the stages in the
        kanban view, even if they are empty
        """
        # Odoo 18 may call this without the 'order' argument; provide a safe default
        order = order or getattr(stages, "_order", "sequence, id")
        # Use sudo().search instead of deprecated _search/access_rights_uid
        all_stages = stages.sudo().search([], order=order)
        return all_stages

    def update_sat_status(self):
        for record in self.line_ids:
            record.update_sat_status()


class AccountRemittanceLine(models.Model):
    _name = "account.remittance.line"
    _description = "Account remittance line"

    name = fields.Char(string="Name")
    line_stage = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),], string="Line stage", default="draft",
    )
    payment_terms = fields.Many2one('account.payment.term', related="invoice_id.invoice_payment_term_id")
    invoice_id = fields.Many2one(
        comodel_name="account.move",
        string="Invoice",
        domain="[('journal_id', '=', 2), ('state', '=', 'posted')]",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner"
    )
    comment = fields.Char(string='Comentario')

    @api.onchange('invoice_id')
    def update_partner(self):
        for record in self:
            record.partner_id = record.invoice_id.partner_id.id

    payment_type = fields.Selection(
        [
            ("credit", "Credit"),
            ("cash", "Cash"),
        ],
        default="credit",
        string="Payment type",
    )
    description = fields.Text(string="Description")
    currency_id = fields.Many2one(
        comodel_name="res.currency", related="remittance_id.currency_id", store=True
    )
    amount_total = fields.Monetary(
        string="Amount total",
        currency_field="currency_id",
        compute="_compute_amount",
        store=True,
    )
    amount_residual = fields.Monetary(
        string="Amount residual",
        currency_field="currency_id",
        compute="_compute_amount",
        store=True,
    )
    amount_to_pay = fields.Monetary(
        string="Amount to pay",
        currency_field="currency_id",
        store=True,
    )
    amount_paid = fields.Monetary(
        string="Amount paid",
        currency_field="currency_id",
        store=True,
    )
    purchase_id = fields.Many2one(
        comodel_name="purchase.order",
        string="Purchase",
        compute="_compute_purchase_id",
        store=True,
    )
    ready_to_pay = fields.Boolean(string="Ready for payment", default=True)
    denied_reason = fields.Selection(
        [
            ("LS", "Lack of support"),
            ("CF", "Cash flow"),
            ("OM", "Cancellation by operations management"),
            ("BM", "Cancellation by administrative management"),
            ("BD", "Missing or incorrect bank details"),
        ],
        string="Rejection reason",
    )
    partner_bank_id = fields.Many2one(
        comodel_name="res.partner.bank",
        string="Account bank",
        compute="_compute_partner_bank",
        store=True,
    )

    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic account', related='remittance_id.project_id')
    remittance_id = fields.Many2one('account.remittance', string='Remesa')
    estado = fields.Char("Estado")

    def update_sat_status(self):
        for record in self:
            attachment_id = self.env['ir.attachment'].search([('id', '=', record.invoice_id.xml_id.id)])
            if attachment_id:
                attachment_id.action_download_state()
                record.estado = attachment_id.estado

    # Actions
    def action_assign_amount(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "ftn_remittance.action_register_payment"
        )
        ctx = dict(self.env.context)
        ctx.pop("active_id", None)
        ctx["active_ids"] = self.ids
        ctx["active_model"] = "account.remittance.line"
        action["context"] = ctx
        return action

    # Onchange methods
    @api.onchange("amount_residual")
    def _onchange_amount_to_pay(self):
        for line in self:
            if line.line_stage == 'draft':
                line.amount_to_pay = line.amount_residual


    # compute methods
    @api.depends("invoice_id.partner_id")
    def _compute_partner_bank(self):
        for line in self:
            partner_bank_id = (
                line.invoice_id.partner_id.bank_ids[0]
                if len(line.invoice_id.partner_id.bank_ids) > 0
                else None
            )
            line.partner_bank_id = partner_bank_id

    @api.depends(
        "invoice_id.amount_total",
        "invoice_id.amount_residual",
    )
    def _compute_amount(self):
        for line in self:
            if line.line_stage == 'draft':
                invoice_id = line.invoice_id
                line.amount_total = invoice_id.amount_total
                line.amount_residual = invoice_id.amount_residual
                line.amount_to_pay = invoice_id.next_due_amount


    @api.depends("invoice_id", "invoice_id.invoice_origin")
    def _compute_purchase_id(self):
        for line in self:
            origin = (
                line.invoice_id.invoice_origin.strip()
                if line.invoice_id.invoice_origin
                else None
            )
            if origin and origin.startswith("P"):
                purchase_id = self.env["purchase.order"].search([("name", "=", origin)])
                line.purchase_id = purchase_id
                line.description = purchase_id.name


    def write(self, vals):
        res = super(AccountRemittanceLine, self).write(vals)
        if "amount_paid" in vals:
            if vals.get("amount_paid") > self.amount_to_pay:
                raise UserError(
                    _(
                        "Amount paid must be less than amount to pay ($%s)"
                        % self.amount_to_pay
                    )
                )
        return res


class RemittanceTag(models.Model):
    _name = "remittance.tag"
    _description = "Tags for remittance"

    name = fields.Char(string="Tag", required=True)
