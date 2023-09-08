# Copyright 2004-2016 Odoo SA (<http://www.odoo.com>)
# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from functools import reduce

from odoo import _, api, fields, models

class GeneralSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    recording_server_url = fields.Char(string='Recording Server URL',
                                       config_parameter='knk_portal_tasks.recording_server_url')

    def set_values(self):
        res = super(GeneralSettings, self).set_values()
        self.env['ir.config_parameter'].set_param('knk_portal_tasks.recording_server_url', self.recording_server_url)
        return res

    @api.model
    def get_values(self):
        res = super(GeneralSettings, self).get_values()
        icp_sudo = self.env['ir.config_parameter'].sudo()
        url = icp_sudo.get_param('knk_portal_tasks.recording_server_url')
        res.update(recording_server_url=url)
        return res



class HelpdeskCall(models.Model):
    """Model for Helpdesk phonecalls."""

    _name = "helpdesk.phonecall"
    _description = "Phonecall"
    _order = "id desc"
    _inherit = ["mail.thread", "utm.mixin"]

    date_action_last = fields.Datetime(string="Last Action", readonly=True)
    date_action_next = fields.Datetime(string="Next Action", readonly=True)
    create_date = fields.Datetime(string="Creation Date", readonly=True)
    recording_path = fields.Text(string='Recording Path')
    recording_name = fields.Text(string='Recording Name')
    audio_player = fields.Char(compute='_compute_audio', string='Audio Player', readonly=True)

    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Responsible",
        default=lambda self: self.env.user,
    )
    partner_id = fields.Many2one(comodel_name="res.partner", string="Contact")
    company_id = fields.Many2one(comodel_name="res.company", string="Company")
    description = fields.Text()
    state = fields.Selection(
        [
            ("open", "Confirmed"),
            ("cancel", "Cancelled"),
            ("pending", "Pending"),
            ("done", "Done"),
        ],
        string="Status",
        tracking=3,
        default="open",
        help="The status is set to Confirmed, when a case is created.\n"
        "When the call is over, the status is set to Held.\n"
        "If the callis not applicable anymore, the status can be set "
        "to Cancelled.",
    )

    email_from  = fields.Char(string="Email", help="These people will receive email.")
    duration    = fields.Char(string="Duration")
    callid      = fields.Char(string="Call ID")
    disposition = fields.Char(string="Disposition")
    calldate    = fields.Char(string="Call Date")

    date_open = fields.Datetime(string="Opened", readonly=True)
    name = fields.Char(string="Call Summary", required=True)
    active = fields.Boolean(required=False, default=True)
    duration = fields.Float(help="Duration in minutes and seconds.")

    partner_phone = fields.Char(string="Phone")
    partner_mobile = fields.Char("Mobile")
    priority = fields.Selection(
        selection=[("0", "Low"), ("1", "Normal"), ("2", "High")],
        string="Priority",
        default="1",
    )
    date_closed = fields.Datetime(string="Closed", readonly=True)
    date = fields.Datetime(default=lambda self: fields.Datetime.now())
    ticket_id = fields.Many2one(comodel_name="helpdesk.ticket", string="Ticket")
    direction = fields.Selection(
        [("in", "In"), ("out", "Out")], default="out", required=True
    )

    @api.depends('recording_path', 'recording_name')
    def _compute_audio(self):
        config_params = self.env['ir.config_parameter'].sudo().get_param('knk_portal_tasks.recording_server_url')
        for record in self:
            if record.recording_path and record.recording_name:
                record.audio_player = str(config_params) + str(record.recording_path) + str(record.recording_name)
            else:
                record.audio_player = False


    @api.onchange("partner_id")
    def on_change_partner_id(self):
        """Contact number details should be change based on partner."""
        if self.partner_id:
            self.partner_phone = self.partner_id.phone
            self.partner_mobile = self.partner_id.mobile

    @api.onchange("ticket_id")
    def on_change_ticket(self):
        """Based on Ticket, changed contact, tags, partner, team."""
        if self.ticket_id:
            self.partner_phone = self.ticket_id.partner_id.phone
            self.partner_mobile = self.ticket_id.partner_id.mobile
            self.partner_id = self.ticket_id.partner_id.id

    def write(self, values):
        """Override to add case management: open/close dates."""
        if values.get("state"):
            if values.get("state") == "done":
                values["date_closed"] = fields.Datetime.now()
                self.compute_duration()
            elif values.get("state") == "open":
                values["date_open"] = fields.Datetime.now()
                values["duration"] = 0.0
        return super().write(values)

    def compute_duration(self):
        """Calculate duration based on phonecall date."""
        phonecall_dates = self.filtered("date")
        phonecall_no_dates = self - phonecall_dates
        for phonecall in phonecall_dates:
            if phonecall.duration <= 0 and phonecall.date:
                duration = fields.Datetime.now() - phonecall.date
                values = {"duration": duration.seconds / 60.0}
                phonecall.write(values)
            else:
                phonecall.duration = 0.0
        phonecall_no_dates.write({"duration": 0.0})
        return True

    def get_values_schedule_another_phonecall(self, vals):
        res = {
            "name": vals.get("name"),
            "user_id": vals.get("user_id") or self.user_id.id,
            "description": self.description,
            "date": vals.get("schedule_time") or self.date,
            "partner_id": self.partner_id.id,
            "partner_phone": self.partner_phone,
            "partner_mobile": self.partner_mobile,
            "priority": self.priority,
            "ticket_id": self.ticket_id.id,
        }
        return res

    def schedule_another_phonecall(self, vals, return_recordset=False):
        """Action :('schedule','Schedule a call'), ('log','Log a call')."""
        phonecall_dict = {}
        for call in self:
            values = call.get_values_schedule_another_phonecall(vals)
            new_id = self.create(values)
            if vals.get("action") == "log":
                call.write({"state": "done"})
            phonecall_dict[call.id] = new_id
        if return_recordset:
            return reduce(lambda x, y: x + y, phonecall_dict.values())
        else:
            return phonecall_dict

    def redirect_phonecall_view(self):
        """Redirect on the phonecall related view."""
        model_data = self.env["ir.model.data"]
        # Select the view
        tree_view = model_data.get_object_reference(
            "helpdesk_phonecall", "helpdesk_case_phone_tree_view"
        )
        form_view = model_data.get_object_reference(
            "helpdesk_phonecall", "helpdesk_case_phone_form_view"
        )
        search_view = model_data.get_object_reference(
            "helpdesk_phonecall", "view_helpdesk_case_phonecalls_filter"
        )
        value = {}
        for call in self:
            value = {
                "name": _("Phone Call"),
                "view_type": "form",
                "view_mode": "tree,form",
                "res_model": "helpdesk.phonecall",
                "res_id": call.id,
                "views": [
                    (form_view and form_view[1] or False, "form"),
                    (tree_view and tree_view[1] or False, "tree"),
                    (False, "calendar"),
                ],
                "type": "ir.actions.act_window",
                "search_view_id": search_view and search_view[1] or False,
            }
        return value

    def action_make_meeting(self):
        """Open meeting's calendar view to schedule a meeting on phonecall."""
        partner_ids = [self.env["res.users"].browse(self.env.uid).partner_id.id]
        res = {}
        for phonecall in self:
            if phonecall.partner_id and phonecall.partner_id.email:
                partner_ids.append(phonecall.partner_id.id)
            res = self.env["ir.actions.act_window"]._for_xml_id(
                "calendar.action_calendar_event"
            )
            res["context"] = {
                "default_phonecall_id": phonecall.id,
                "default_partner_ids": partner_ids,
                "default_user_id": self.env.uid,
                "default_email_from": phonecall.email_from,
                "default_name": phonecall.name,
            }
        return res

    def get_values_convert2ticket(self):
        return {
            "name": self.name,
            "partner_id": self.partner_id.id,
            "partner_phone": self.partner_phone or self.partner_id.phone,
            "partner_mobile": self.partner_mobile or self.partner_id.mobile,
            "partner_email": self.partner_id.email,
            "description": self.description,
            "priority": self.priority,
            #"type": "opportunity",
        }

    def action_button_convert2ticket(self):
        """Convert a phonecall into an opp and redirect to the opp view."""
        self.ensure_one()
        ticket = self.env["helpdesk.ticket"]
        ticket_id = ticket.create(self.get_values_convert2ticket())
        self.write({"ticket_id": ticket_id.id, "state": "done"})
        return ticket_id.redirect_lead_opportunity_view()
