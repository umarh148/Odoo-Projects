import pytz
import logging
import base64
import re
import json
from base64 import b64encode
from datetime import datetime, timedelta
from operator import itemgetter

from odoo import http, _
from odoo.http import request
from odoo.addons.website_form.controllers.main import WebsiteForm
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.tools import groupby as groupbyelem

from odoo.osv.expression import OR, AND
_logger = logging.getLogger(__name__)

class Base64Encoder(json.JSONEncoder):
    # pylint: disable=method-hidden
    def default(self, o):
        if isinstance(o, bytes):
            return b64encode(o).decode()
        return json.JSONEncoder.default(self, o)

class WebsiteMeeting(http.Controller):

    @http.route(['/schedule'], type='http', auth="user", methods=['GET'], website=True)
    def schedule(self, **kw):
        ticket_types_ob = request.env['helpdesk.ticket.type'].sudo().search([])
        ticket_types = []
        for ttp in ticket_types_ob:
            ticket_types.append([ttp.id,ttp.name])
        values = {
            'website': request.website,
            'members': [],
            'ticket_types': ticket_types,
        }
        return request.render('knk_portal_tasks.create_ticket', values)

    @http.route(['/ticket_public'], type='http', auth="user", methods=['POST'], website=True, csrf=False)
    def ticketPublic(self, **post):
        
        total_images_count  = post.get('total_images', False)
        
        Attachment          = request.env['ir.attachment']
        partner             = request.env.user.partner_id
        vals = {
            'team_id':          1,
            'name':             post.get('subject',False),
            'ticket_type_id':   post.get('issue_type',False),
            'description':      post.get('description',False),
            'partner_id':       partner.id,
            'partner_name':     partner.name
        }
        error = ""
        if (not vals['name']):
            error += "Subject is required<br/>"
        if (not vals['ticket_type_id']):
            error += "Issue Type is required<br/>"
        if (not vals['description']):
            error += "Description is required<br/>"
        if error != "":
            res = {
                'status': False,
                'data': error
            }
            return json.dumps(res, cls=Base64Encoder)
        ticket = request.env['helpdesk.ticket'].sudo().create(vals)
        file_base64 = False
        ticket_attachments = []
        all_array = list(range(0, int(total_images_count)))
        if total_images_count:
            for index in all_array:
                posted_file        = post.get(('file[%s]' % index), False)
                if posted_file:
                    filename    = posted_file.filename
                    file        = posted_file
                    attachment  = file.read()
                    attachment = request.env['ir.attachment'].sudo().create({
                    'name':           filename,
                    'type':           'binary',
                    'datas':          base64.encodebytes(attachment),
                    'store_fname':    filename,
                    'res_model':      'helpdesk.ticket',
                    'res_id':         ticket.id,
                    'mimetype':       posted_file.content_type,
                    'public':         True
                    })
                    ticket_attachments += [(4, attachment.id)]
        
        ticket.sudo().update({'capture_attachment_ids':ticket_attachments})
        res = {
            'status': True,
            'data': "Ticket # %s generated successfully" % ticket.sequence_name
        }
        return json.dumps(res, cls=Base64Encoder)
                
class CustomerPortal(CustomerPortal):

    @http.route(['/my/tickets', '/my/tickets/page/<int:page>'], type='http', auth="user", website=True)
    def my_helpdesk_tickets(self, page=1, date_begin=None, date_end=None, sortby=None, search=None, search_in='content', groupby='none', **kw):
        values = self._prepare_portal_layout_values()
        domain = []

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Subject'), 'order': 'name'},
            'stage': {'label': _('Stage'), 'order': 'stage_id'},
        }
        searchbar_inputs = {
            'content': {'input': 'content', 'label': _('Search <span class="nolabel"> (in Content)</span>')},
            'message': {'input': 'message', 'label': _('Search in Messages')},
            'customer': {'input': 'customer', 'label': _('Search in Customer')},
            'id': {'input': 'id', 'label': _('Search ID')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        searchbar_groupby = {
            'none': {'input': 'none', 'label': _('None')},
            'stage': {'input': 'stage', 'label': _('Stage')},
        }

        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # archive groups - Default Group By 'create_date'
        archive_groups = self._get_archive_groups('helpdesk.ticket', domain) if values.get('my_details') else []
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # search
        search_domain = []
        partner_id = request.env.user.partner_id
        search_domain = OR([search_domain, [('partner_id.id', '=', partner_id.id)]])
        if partner_id.parent_id:
            search_domain = OR([search_domain, [('partner_id.id', '=', partner_id.parent_id.id)]])
        domain += search_domain
        if search and search_in:
            search_domain = []
            if search_in in ('id', 'all'):
                search_domain = OR([search_domain, [('id', 'ilike', search)]])
            if search_in in ('content', 'all'):
                search_domain = OR([search_domain, ['|', ('name', 'ilike', search), ('description', 'ilike', search)]])
            if search_in in ('customer', 'all'):
                search_domain = OR([search_domain, [('partner_id', 'ilike', search)]])
            if search_in in ('message', 'all'):
                search_domain = OR([search_domain, [('message_ids.body', 'ilike', search)]])
            domain += search_domain

        # pager
        tickets_count = request.env['helpdesk.ticket'].search_count(domain)
        pager = portal_pager(
            url="/my/tickets",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby, 'groupby': groupby},
            total=tickets_count,
            page=page,
            step=self._items_per_page
        )
        _logger.exception("--------- KNKDIS res----- %s", domain)
        tickets = request.env['helpdesk.ticket'].search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_tickets_history'] = tickets.ids[:100]

        if groupby == 'stage':
            order = "stage_id, %s" % order  # force sort on project first to group by project in view
        tickets = request.env['helpdesk.ticket'].search(domain, order=order, limit=self._items_per_page, offset=(page - 1) * self._items_per_page)
        request.session['my_tickets_history'] = tickets.ids[:100]
        if groupby == 'stage':
            grouped_tickets = [request.env['helpdesk.ticket'].concat(*g) for k, g in groupbyelem(tickets, itemgetter('stage_id'))]
        else:
            grouped_tickets = [tickets]

        values.update({
            'date': date_begin,
            'grouped_tickets': grouped_tickets,
            'page_name': 'ticket',
            'default_url': '/my/tickets',
            'pager': pager,
            'archive_groups': archive_groups,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_inputs': searchbar_inputs,
            'searchbar_groupby': searchbar_groupby,
            'sortby': sortby,
            'groupby': groupby,
            'search_in': search_in,
            'search': search,
        })
        return request.render("helpdesk.portal_helpdesk_ticket", values)

class WebsiteForm(WebsiteForm):

    def _handle_website_form(self, model_name, **kwargs):
        # if model_name == 'helpdesk.ticket':
        #     attendees = request.env['res.users'].sudo().browse(int(kwargs['user_id'])).partner_id + request.env.user.partner_id
        #     kwargs['partner_ids'] = [(6, 0, attendees.ids)]
        #     time_from = kwargs['timeslot'].split(' - ')[0]
        #     hour_from = int(time_from.split(':')[0])
        #     minute_from = int(time_from.split(':')[1])
        #     meeting_date = pytz.timezone(kwargs['timezone']).localize(datetime.strptime(kwargs['meeting_date'], '%Y-%m-%d') + timedelta(hours=hour_from, minutes=minute_from))
        #     request.params.update({
        #         'partner_ids': ','.join([str(partner_id) for partner_id in attendees.ids]),
        #         'start': meeting_date.astimezone(pytz.timezone('UTC')).replace(tzinfo=None),
        #         'stop': meeting_date.astimezone(pytz.timezone('UTC')).replace(tzinfo=None) + timedelta(minutes=int(kwargs['duration'])),
        #         'duration': (int(kwargs['duration']) / 60),
        #     })
        return super(WebsiteForm, self)._handle_website_form(model_name, **kwargs)
