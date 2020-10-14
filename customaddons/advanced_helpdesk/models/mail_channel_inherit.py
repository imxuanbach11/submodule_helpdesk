from odoo import fields, models, api


class MailChannelInherit(models.Model):
    _inherit = 'mail.channel'

    visitor_info = fields.Char(string='Visitor Information', compute="_compute_visitor_info")
    livechat_stage = fields.Selection([
        ('waiting', 'Waiting'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
    ], string='Livechat Stage', default='waiting')

    # fill info prequestion
    def _compute_visitor_info(self):
        for rec in self:
            if rec.channel_type == 'livechat':
                rec.visitor_info = None
                if len(rec.message_ids) > 0:
                    for mess in rec.message_ids:
                        if mess:
                            if '╠╦═ Email' in mess.body:
                                str_info = mess.body.replace('<p>╠╦═ ', '').replace('<br>', ', ').replace(
                                    '</p>', '')
                                mess_index = str_info.find(', Message:')
                                rec.visitor_info = str_info[0:mess_index]

    # mark done sau khi suport hoan thanh
    # def action_done(self):
    #     for rec in self:
    #         rec.is_done = False
    #         if rec.channel_type == 'livechat':
    #             rec.is_done = True
    #             rec.livechat_stage = 'done'
