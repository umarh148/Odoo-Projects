# Copyright 2004-2010 Tiny SPRL (<http://tiny.be>)
# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import time

from odoo import api, fields, models


class HelpdeskPhonecall2phonecall(models.TransientModel):
    """Added the details of the helpdesk phonecall2phonecall."""

    _name = "helpdesk.phonecall2phonecall"
    _description = "Phonecall To Phonecall"

    name = fields.Char(string="Call summary", required=True, index=True)
    user_id = fields.Many2one(comodel_name="res.users", string="Assign To")
    contact_name = fields.Char(string="Contact")
    phone = fields.Char()
    date = fields.Datetime()
    action = fields.Selection(
        selection=[("schedule", "Schedule a call"), ("log", "Log a call")],
        string="Action",
        required=True,
    )
    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner")
    note = fields.Text()

    def get_vals_action_schedule(self):
        vals = {
            "schedule_time": self.date,
            "name": self.name,
            "user_id": self.user_id.id,
            "action": self.action,
        }
        return vals

    def action_schedule(self):
        """Schedule a phonecall."""
        phonecall_obj = self.env["helpdesk.phonecall"]
        phonecalls = phonecall_obj.browse(self._context.get("active_ids", []))
        vals = self.get_vals_action_schedule()
        new_phonecalls = phonecalls.schedule_another_phonecall(
            vals, return_recordset=True
        )
        return new_phonecalls.redirect_phonecall_view()

    @api.model
    def default_get(self, fields):
        """Function gets default values."""
        res = super().default_get(fields)
        res.update({"action": "schedule", "date": time.strftime("%Y-%m-%d %H:%M:%S")})
        for phonecall in self.env["helpdesk.phonecall"].browse(
            self.env.context.get("active_id")
        ):
            if "user_id" in fields:
                res.update({"user_id": phonecall.user_id.id})
            if "partner_id" in fields:
                res.update({"partner_id": phonecall.partner_id.id})
            for field in ("name", "date"):
                if field in fields:
                    res[field] = getattr(phonecall, field)
        return res
