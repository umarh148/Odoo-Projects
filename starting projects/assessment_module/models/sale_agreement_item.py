from odoo import models, fields, api


class SaleAgreementItem(models.Model):
    _name = "sale.agreement.item"
    _description = "Sale Agreement Item"

    product_id = fields.Many2one('product.product', string='Product', required=True)
    description = fields.Char(string='Description', default='Default Description')
    quantity = fields.Float(string='Quantity', default=1.00)
    unit_price = fields.Float(string='Unit Price', related='product_id.list_price')
    total_price = fields.Float(compute='total_amount', string='Total Price', store=True)
    item_id = fields.Many2one('sale.agreement', string='Item')

    @api.depends('quantity', 'unit_price')
    def total_amount(self):
        for record in self:
            record.total_price = record.quantity*record.unit_price



