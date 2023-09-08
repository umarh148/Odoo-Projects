import pytz

from datetime import datetime, timedelta
from odoo.tools.safe_eval import safe_eval
from odoo import api, models, fields, _


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    capture_attachment_ids = fields.Many2many(
        'ir.attachment',
        string='Capture Photos',
        copy=False,
    )

    phonecall_ids = fields.One2many(
        comodel_name="helpdesk.phonecall", inverse_name="ticket_id", string="Phonecalls"
    )
    phonecall_count = fields.Integer(compute="_compute_phonecall_count")
    description = fields.Html(string="Description")

    sequence_name = fields.Char("Sequence",readonly=True)

    def _compute_phonecall_count(self):
        """Calculate number of phonecalls."""
        for ticket in self:
            ticket.phonecall_count = self.env["helpdesk.phonecall"].search_count(
                [("ticket_id", "=", ticket.id)]
            )

    def button_open_phonecall(self):
        self.ensure_one()
        action = self.env.ref("knk_portal_tasks.helpdesk_case_categ_phone_incoming0")
        action_dict = action.read()[0] if action else {}
        action_dict["context"] = safe_eval(action_dict.get("context", "{}"))
        action_dict["context"].update(
            {
                "default_ticket_id": self.id,
                "search_default_ticket_id": self.id,
                "default_partner_id": self.partner_id.id,
                "default_duration": 1.0,
            }
        )
        return action_dict

    @api.model
    def create(self,vals):
        if vals.get('sequence_name', _('New')) == _('New'):
            vals['sequence_name'] = self.env['ir.sequence'].next_by_code('helpdesk.ticket') or _('New')
        res = super(HelpdeskTicket, self).create(vals)
        return res