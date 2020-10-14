from odoo import fields, models, api
import random


class ImlivechatChannelInherit(models.Model):
    _inherit = 'im_livechat.channel'

    def _get_random_operator(self):
        """ Return a random operator from the available users of the channel that have the lowest number of active livechats.
        A livechat is considered 'active' if it has at least one message within the 30 minutes.

        (Some annoying conversions have to be made on the fly because this model holds 'res.users' as available operators
        and the mail_channel model stores the partner_id of the randomly selected operator)

        :return : user
        :rtype : res.users
        """
        operators = self._get_available_users()
        if len(operators) == 0:
            return False
        # lay ds operator onl kp bot
        list_operator_online = []
        if operators:
            for user in operators:
                if user.partner_id:
                    if user.im_status == 'online' and user.is_online == False:
                        list_operator_online.append(user.partner_id.id)
        # support onl
        if len(list_operator_online) > 0:
            self.env.cr.execute("""SELECT COUNT(DISTINCT c.id), c.livechat_operator_id
                FROM mail_channel c
                LEFT OUTER JOIN mail_message_mail_channel_rel r ON c.id = r.mail_channel_id
                LEFT OUTER JOIN mail_message m ON r.mail_message_id = m.id
                WHERE m.create_date > ((now() at time zone 'UTC') - interval '30 minutes')
                AND c.channel_type = 'livechat'
                AND c.livechat_operator_id in %s
                GROUP BY c.livechat_operator_id
                ORDER BY COUNT(DISTINCT c.id) asc""", (tuple(list_operator_online),))
            active_channels = self.env.cr.dictfetchall()
            # If inactive operator(s), return one of them
            active_channel_operator_ids = [active_channel['livechat_operator_id'] for active_channel in active_channels]
            # operator chua co channel iperator
            inactive_operators = [operator for operator in operators if
                                  operator.partner_id.id not in active_channel_operator_ids and operator.is_online == False]
            if inactive_operators:
                return random.choice(inactive_operators)
            # If no inactive operator, active_channels is not empty as len(operators) > 0 (see above).
            # Get the less active operator using the active_channels first element's count (since they are sorted 'ascending')
            lowest_number_of_conversations = active_channels[0]['count']
            less_active_operator = random.choice([
                active_channel['livechat_operator_id'] for active_channel in active_channels
                if active_channel['count'] == lowest_number_of_conversations])

            # convert the selected 'partner_id' to its corresponding res.users
            return next(operator for operator in operators if
                        operator.partner_id.id == less_active_operator and operator.is_online == False)
        # neu ko co support onl, chat voi bot
        else:
            return random.choice([operator for operator in operators if
                                  operator.partner_id.id])
