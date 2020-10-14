from odoo import api, fields, models


class HelpdeskStageInherit(models.Model):
    _inherit = "helpdesk.stage"

    apply_followup = fields.Boolean(string="Apply Follow Up", default=False)
    email_template = fields.Many2one(string='Mail template', comodel_name="mail.template")
    destination_stage_id = fields.Many2one(string="Destination Stage", comodel_name="helpdesk.stage")

    is_stage_progress_for_followup = fields.Boolean(string="Is in progress stage")
