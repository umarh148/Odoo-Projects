from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = "sale.order"

    subject = fields.Char(String="Subject")
#
#     def action_confirm(self):
#         super(SaleOrder, self).action_confirm()
#         self.confirm_user_id = self.env.user.id
