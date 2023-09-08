import pytz
import logging
import base64
import re
import json
from base64 import b64encode
from datetime import datetime, timedelta

from odoo import http
from odoo.http import request
from odoo.addons.website_form.controllers.main import WebsiteForm
_logger = logging.getLogger(__name__)

class Base64Encoder(json.JSONEncoder):
    # pylint: disable=method-hidden
    def default(self, o):
        if isinstance(o, bytes):
            return b64encode(o).decode()
        return json.JSONEncoder.default(self, o)

class Voip(http.Controller):

    @http.route(['/call_recording'], type='http', auth="public", methods=['GET'], website=True, csrf=False)
    def callRecording(self, **post):
        ext_to      = post.get('to', False)
        ext_from    = post.get('from', False)
        start_time  = post.get('starttime', False)
        file_path   = post.get('filepath', False)
        file_name   = post.get('filename', False)
        duration    = post.get('duration',False)
        uniqueid    = post.get('uniqueid',False)
        disposition = post.get('disposition',False)
        calldate    = post.get('calldate',False)
        
        description = "Call From : %s | Call To : %s | Start Time : %s | Path : %s | Name : %s | Duration : %s | CallID: %s | Disposition: %s | Call Date: %s" % (ext_to, ext_from, start_time, file_path, file_name, duration, uniqueid, disposition, calldate)
        name        = "%s-%s-%s"%(ext_from,ext_to,start_time)
        vals = {
            'name':             name,
            'user_id':          2,
            'partner_id':       2,
            'description':      description,
            'duration':         duration,
            'callid':           uniqueid,
            'disposition':      disposition,
            'calldate':         calldate,
            'recording_path':   file_path,
            'recording_name':   file_name,
            'state':            'open',
            'direction':        'in',

        }
        call = request.env['helpdesk.phonecall'].sudo().create(vals)

        res = {
            'status': True,
            'data': "Call data saved succesfully with ID %s" % call.id 
        }
        return json.dumps(res, cls=Base64Encoder)

    @http.route(['/update_recording'], type='http', auth="public", methods=['GET'], website=True, csrf=False)
    def updateRecording(self, **post):
        duration    = post.get('duration',False)
        uniqueid    = post.get('uniqueid',False)
        phonecall_record = request.env['helpdesk.phonecall'].sudo().search([('callid','=',uniqueid)],limit=1)
        
        description = "Call Spec : %s | Duration : %s | CallID: %s | Disposition: %s | Call Date: %s" % (
            phonecall_record.name, duration, uniqueid, phonecall_record.disposition, phonecall_record.calldate)
        vals = {
            'description':      description,
            'duration':         duration,
            'callid':           uniqueid,
            'state':            'open',
            'direction':        'in',
        }
        if phonecall_record:
            call = phonecall_record.update(vals)
            res = {
                'status': True,
                'data': "Call data updated succesfully with ID %s" % phonecall_record.id 
            }
        else:
            call = request.env['helpdesk.phonecall'].sudo().create(vals)
            res = {
                'status': True,
                'data': "Call data saved succesfully with ID %s" % call.id 
            }
        return json.dumps(res, cls=Base64Encoder)
    