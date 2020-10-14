from odoo import api, fields, models


class ConfigFollowUpTicket(models.Model):
    _name = "config.followup.ticket"
    _rec_name = "name"

    name = fields.Char(string="Name")
    times = fields.Integer(string="Number times follow up")
    execute_every = fields.Integer(string="Execute every (day)")
    email_template = fields.Many2one(string='Mail template', comodel_name="mail.template")

