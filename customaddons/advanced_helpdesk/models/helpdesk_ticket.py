from odoo import api, fields, models
from datetime import datetime


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    times_followup = fields.Integer(string="Number times follow up", default=0)

    def cron_job_followup_ticket(self):
        print("zoo")
        helpdesk_followup_stage_ids = self.env['helpdesk.stage'].sudo().search([('apply_followup', '=', True)])
        if helpdesk_followup_stage_ids:
            for stage in helpdesk_followup_stage_ids:
                ticket_ids = self.env['helpdesk.ticket'].sudo().search([('stage_id', '=', stage.id)])
                if ticket_ids:
                    for ticket in ticket_ids:
                        print("zoo11")
                        last_message = self.env['mail.message'].sudo().search([('model', '=', 'helpdesk.ticket'), ('res_id', '=', ticket.id), ('subject', '!=', 'Follow up')], order='create_date desc', limit=1)
                        if last_message:
                            if datetime.now().day - last_message.create_date.day >= 2:
                                if ticket.times_followup >= 2:
                                    ticket.sudo().write({
                                        'stage_id': stage.destination_stage_id.id,
                                        'times_followup': 0,
                                    })
                                else:
                                    ticket.sudo().write({
                                        'times_followup': ticket.times_followup + 1,
                                    })
                                    mail_template = stage.email_template
                                    mail_values = mail_template.generate_email(ticket.id)
                                    message = self.env['mail.message'].sudo().create({
                                        'subject': 'Follow up',
                                        'body': mail_values['body'],
                                        'model': 'helpdesk.ticket',
                                        'res_id': ticket.id,
                                        'message_type': 'comment'
                                    })
                                    # mail_template.send_mail(ticket.id, force_send=True)
