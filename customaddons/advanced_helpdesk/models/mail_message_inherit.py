from odoo import api, fields, models


class MailMessageInherit(models.Model):
    _inherit = "mail.message"

    @api.model
    def create(self, vals):
        res = super(MailMessageInherit, self).create(vals)
        if res.model == "helpdesk.ticket":
            ticket = self.env['helpdesk.ticket'].sudo().browse(res.res_id)
            if not res.subject or res.subject != 'Follow up':
                if ticket:
                    ticket.sudo().write({
                        'times_followup': 0,
                    })
            message_related = self.env['mail.message'].sudo().search([('id', '!=', res.id), ('create_date', '!=', ticket.create_date), ('subject', '!=', 'Follow up'), ('model', '=', 'helpdesk.ticket'), ('res_id', '=', res.res_id)])
            if len(message_related) == 0:
                if ticket.team_id:
                    inprogress_stage = self.env['helpdesk.stage'].sudo().search([('is_stage_progress_for_followup', '=', True)])
                    if inprogress_stage:
                        for element in inprogress_stage:
                            if ticket.team_id.id in element.team_ids.ids:
                                ticket.sudo().write({
                                    'stage_id': element.id
                                })
                                break
        return res
