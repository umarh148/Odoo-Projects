import pytz

from datetime import datetime, timedelta

from odoo import api, models, fields, _


class PortalMixin(models.AbstractModel):
    _inherit = 'portal.mixin'

    def _notify_get_groups(self, msg_vals=None):
        access_token = self._portal_ensure_token()
        groups = super(PortalMixin, self)._notify_get_groups(msg_vals=msg_vals)
        local_msg_vals = dict(msg_vals or {})

        if access_token and 'partner_id' in self._fields and self['partner_id']:
            customer = self['partner_id']
            local_msg_vals['access_token'] = self.access_token
            local_msg_vals.update(customer.signup_get_auth_param()[customer.id])
            access_link = self._notify_get_action_link('view', **local_msg_vals)

            new_group = [
                ('portal_customer', lambda pdata: pdata['id'] == customer.id, {
                    'has_button_access': False,
                    'button_access': {
                        'url': access_link,
                    },
                    'notification_is_customer': True,
                })
            ]
        else:
            new_group = []
        return new_group + groups