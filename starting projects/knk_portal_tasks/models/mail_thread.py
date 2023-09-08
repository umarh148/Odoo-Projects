import pytz

from datetime import datetime, timedelta

from odoo import api, models, fields, _


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _notify_classify_recipients(self, recipient_data, model_name, msg_vals=None):
        """ Classify recipients to be notified of a message in groups to have
        specific rendering depending on their group. For example users could
        have access to buttons customers should not have in their emails.
        Module-specific grouping should be done by overriding ``_notify_get_groups_custom``
        method defined here-under.
        :param recipient_data:todo xdo UPDATE ME
        return example:
        [{
            'actions': [],
            'button_access': {'title': 'View Simple Chatter Model',
                                'url': '/mail/view?model=mail.test.simple&res_id=1497'},
            'has_button_access': False,
            'recipients': [11]
        },
        {
            'actions': [],
            'button_access': {'title': 'View Simple Chatter Model',
                            'url': '/mail/view?model=mail.test.simple&res_id=1497'},
            'has_button_access': False,
            'recipients': [4, 5, 6] 
        },
        {
            'actions': [],
            'button_access': {'title': 'View Simple Chatter Model',
                                'url': '/mail/view?model=mail.test.simple&res_id=1497'},
            'has_button_access': True,
            'recipients': [10, 11, 12]
        }]
        only return groups with recipients
        """
        # keep a local copy of msg_vals as it may be modified to include more information about groups or links
        local_msg_vals = dict(msg_vals) if msg_vals else {}
        groups = self._notify_get_groups_custom(msg_vals=local_msg_vals)
        access_link = self._notify_get_action_link('view', **local_msg_vals)

        if model_name:
            view_title = _('View %s', model_name)
        else:
            view_title = _('View')

        # fill group_data with default_values if they are not complete
        for group_name, group_func, group_data in groups:
            group_data.setdefault('notification_group_name', group_name)
            group_data.setdefault('notification_is_customer', False)
            is_thread_notification = self._notify_get_recipients_thread_info(msg_vals=msg_vals)['is_thread_notification']
            group_data.setdefault('has_button_access', is_thread_notification)
            group_button_access = group_data.setdefault('button_access', {})
            group_button_access.setdefault('url', access_link)
            group_button_access.setdefault('title', view_title)
            group_data.setdefault('actions', list())
            group_data.setdefault('recipients', list())

        # classify recipients in each group
        for recipient in recipient_data:
            for group_name, group_func, group_data in groups:
                if group_func(recipient):
                    group_data['recipients'].append(recipient['id'])
                    break

        result = []
        for group_name, group_method, group_data in groups:
            if group_data['recipients']:
                result.append(group_data)

        return result

    def _notify_get_groups_custom(self, msg_vals=None):
        """ Return groups used to classify recipients of a notification email.
        Groups is a list of tuple containing of form (group_name, group_func,
        group_data) where
         * group_name is an identifier used only to be able to override and manipulate
           groups. Default groups are user (recipients linked to an employee user),
           portal (recipients linked to a portal user) and customer (recipients not
           linked to any user). An example of override use would be to add a group
           linked to a res.groups like Hr Officers to set specific action buttons to
           them.
         * group_func is a function pointer taking a partner record as parameter. This
           method will be applied on recipients to know whether they belong to a given
           group or not. Only first matching group is kept. Evaluation order is the
           list order.
         * group_data is a dict containing parameters for the notification email
          * has_button_access: whether to display Access <Document> in email. True
            by default for new groups, False for portal / customer.
          * button_access: dict with url and title of the button
          * actions: list of action buttons to display in the notification email.
            Each action is a dict containing url and title of the button.
        Groups has a default value that you can find in mail_thread
        ``_notify_classify_recipients`` method.
        """
        return [
            (
                'user',
                lambda pdata: pdata['type'] == 'user',
                {}
            ), (
                'portal',
                lambda pdata: pdata['type'] == 'portal',
                {'has_button_access': False}
            ), (
                'customer',
                lambda pdata: True,
                {'has_button_access': False}
            )
        ]