# -*- coding: utf-8 -*-
from odoo import models, fields, _, api

class SolicitudWS(models.Model):
    _name = 'solicitud.ws'
    _description = 'SolicitudWS'

    id_solicitud = fields.Char("ID Solicitud")
    cod_estatus = fields.Char("Codigo Estatus Solicitud")
    mensaje = fields.Char("Mensaje de solicitud")
    rfc_receptor = fields.Boolean('Solicitud de recibidos')
    rfc_emisor = fields.Boolean('Solicitud de emitidos')
    fecha = fields.Date('Fecha de solicitud')
    fecha_inicio = fields.Date('Fecha inicio')
    fecha_fin = fields.Date('Fecha fin')
    state = fields.Selection([('draft', 'En espera'), ('done', 'Hecho'), ('cancel', 'Error')], string='Estado', default='draft')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.company)

    cod_verifica = fields.Char("Codigo Verificacion")
    estado_solicitud = fields.Char("Estado Verificacion")
    mensaje_ver = fields.Char("Mensaje de verificacion")
