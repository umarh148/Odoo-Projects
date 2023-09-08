# -*- coding: utf-8 -*-

import requests
import logging
import json

from odoo.modules.module import get_module_resource

from odoo import api, fields, models, exceptions, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from ast import literal_eval
_logger = logging.getLogger(__name__)
import pytz

class ResUsers(models.Model):
    _inherit = "res.users"

    web_hook = fields.Char(string="Webhook Url")
    ticket_role = fields.Selection([('user', 'User'), ('manager', 'Manager')], default='user', string="Ticket Role")

class HelpdeskTickets(models.Model):
    _inherit = 'helpdesk.ticket'

    user_ticket_role = fields.Char(string="Ticket Role", compute='_compute_user_ticket_role')
    time_completion = fields.Datetime(string='Planned Completion', default=False)

    def _compute_user_ticket_role(self):
        self.user_ticket_role = self.user_id.ticket_role

    def action_get_my_helpdesk_tickets(self):
        user = self.env['res.users'].sudo().search([('id', '=', self.env.uid)])
        action = {
            'domain': "[('user_id', '=', " + str(self.env.uid) + " )]",
            'name': 'My Tickets',
            'view_mode': 'kanban,tree,form',
            'res_model': 'helpdesk.ticket',
            'type': 'ir.actions.act_window',
        }
        return action

    def action_get_all_helpdesk_tickets(self):
        action = {
            'domain': "[]",
            'name': 'My Tickets',
            'view_mode': 'kanban,tree,form',
            'res_model': 'helpdesk.ticket',
            'type': 'ir.actions.act_window',
        }
        return action

    @api.model
    def create(self, vals):
        res1 = super(HelpdeskTickets, self).create(vals)
        _logger.exception("--------- Tickets Creation ----- %s", vals)
        sw_file = get_module_resource('knk_portal_tasks_customization', 'static/jsonbody.json')
        with open(sw_file, 'r') as fp:
            json_body = fp.read()
            json_body_index = json_body.index("%%TICKET_TYPE%%")
            json_body = json_body.replace( "%%TICKET_NUM%%", vals["sequence_name"])
            json_body = json_body.replace("%%CUSTOMER_NAME%%", str(vals["partner_name"]))
            if "assign_date" in vals:
                create_date = vals["assign_date"].strftime("%b %d %Y - %I:%M %p")
                json_body = json_body.replace("%%CREATION_DATE%%", str(create_date))
            json_body = json_body.replace("%%TASK_NAME%%", vals["name"])
            json_body = json_body.replace("%%TICKET_NUM%%", vals["sequence_name"])
            json_body = json_body.replace("%%TICKET_TYPE%%", str(vals["ticket_type_id"]))
            json_body = json_body.replace("%%TICKET_URL%%", "https://dis2.staging.knkit.com/my/ticket/" + str(res1.id) +"/access_token="+ res1.access_token)

            # _logger.exception("--------- Tickets Creation ----- %s", {'body':json_body, 'index':json_body_index})
            fp.close()
            # data = json.load(fp)
            # data['attachments'][0]['body'][0]['text'] = vals["sequence_name"]
            # data['attachments'][0]['body'][1]['columns'][1]['items'][0][
            #     'text'] = vals["partner_id"]
            # create_date = vals["assign_date"].strftime("%b %d %Y - %I:%M %p")
            # data['attachments'][0]['body'][1]['columns'][1]['items'][1]['text'] = "Created " + str(create_date)
            # data['attachments'][0]['body'][2]['text'] = vals["sequence_name"]
            # data['attachments'][0]['body'][3]['facts'][0]['value'] = vals["name"]
            # _logger.exception("--------- Tickets Creation ----- %s", json.dumps(data, indent=2))

        url_root                = "https://hooks.ringcentral.com"
        webhook_from_setting    = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJvdCI6ImMiLCJvaSI6IjI0ODkxODgzNTMiLCJpZCI6IjE4ODIxODU3NTUifQ.htZpWKlyEOe1M1TzPDLox4qq2OmWxoJWonyDmuVZhm4"
        webhook_url             ="/webhook/v2/%s" % webhook_from_setting
        post_url                = url_root + webhook_url

        _logger.exception("--------- Tickets Creation ----- %s", {'post_url': post_url})
        headers = {'Content-type': 'application/json'}
        data = json_body
        res = requests.post(post_url, data=data, headers=headers)
        return res1

class HelpdeskTicketsTeam(models.Model):
    _inherit = 'helpdesk.team'

    user_ticket_role = fields.Char(string="Ticket Role", compute='_compute_user_ticket_role')


    def _compute_user_ticket_role(self):
        user_id = self.env['res.users'].sudo().search([('id', '=', self.env.uid)])
        self.user_ticket_role = user_id.ticket_role

    def action_get_my_helpdesk_tickets(self):
        action = {
            'domain': "[('user_id', '=', " + str(self.env.uid) + " )]",
            'name': 'My Tickets',
            'view_mode': 'kanban,tree,form',
            'res_model': 'helpdesk.ticket',
            'type': 'ir.actions.act_window',
        }
        return action
