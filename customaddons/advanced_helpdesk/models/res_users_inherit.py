from odoo import fields, models, api
from odoo.addons.bus.models.bus_presence import AWAY_TIMER
from odoo.addons.bus.models.bus_presence import DISCONNECTION_TIMER

class ResUserInherit (models.Model):
    _inherit = 'res.users'
    is_online = fields.Boolean(string='Online',store=True, default=False, help="User online everyday")

    def _compute_im_status(self):
        res = super(ResUserInherit, self)._compute_im_status()
        for user in self:
            if user.is_online:
                user.im_status = 'online'
        return res


