# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    project_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Proyecto",
        check_company=True,
        copy=True,
        help="Cuenta analítica (proyecto) a aplicar en todas las líneas de la orden de compra.",
    )

    @api.onchange("project_id")
    def _onchange_project_id(self):
        distribution = (
            {str(self.project_id.id): 100}
            if self.project_id
            else {}
        )
        for line in self.order_line:
            line.analytic_distribution = distribution

    @api.onchange('analytic_distribution')
    def inverse_analytic_distribution(self):
        if self.analytic_distribution:
            distribution = self.analytic_distribution
            if len(distribution) > 1:
                self.project_id = False
            else:
                project_id = list(distribution.keys())[0]
                self.project_id = int(project_id)
        else:
            self.project_id = False