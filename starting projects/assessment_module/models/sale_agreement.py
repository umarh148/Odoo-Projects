from odoo import models, fields, api


class SaleAgreement(models.Model):
    _name = 'sale.agreement'
    _description = 'Sale Agreement'

    seq_sa = fields.Char(string='SA', readonly=True)
    name = fields.Char(string="Name")
    subject = fields.Text(string='Subject')
    date = fields.Date(string='Date')
    item_ids = fields.One2many('sale.agreement.item', 'item_id', string='Items')

    @api.model
    def create(self, vals):
        vals['seq_sa'] = self.env['ir.sequence'].next_by_code('sale.agreement')
        return super(SaleAgreement, self).create(vals)

