import base64

from odoo.addons.im_livechat.controllers.main import LivechatController

from odoo import http,tools
from odoo.addons.base.models.assetsbundle import AssetsBundle
from odoo.http import request


# from odoo.addons.im_livechat.controllers.main import LivechatController


class ImLivechatController(LivechatController):

    @http.route()
    def livechat_lib(self, ext, **kwargs):
        # _get_asset return the bundle html code (script and link list) but we want to use the attachment content
        xmlid = 'advanced_helpdesk.im_livechat_custom_pre_question_form_tracking'
        files, remains = request.env["ir.qweb"]._get_asset_content(xmlid, options=request.context)
        asset = AssetsBundle(xmlid, files)

        mock_attachment = getattr(asset, ext)()
        if isinstance(mock_attachment, list):  # suppose that CSS asset will not required to be split in pages
            mock_attachment = mock_attachment[0]
        # can't use /web/content directly because we don't have attachment ids (attachments must be created)
        status, headers, content = request.env['ir.http'].binary_content(id=mock_attachment.id, unique=asset.checksum)
        content_base64 = base64.b64decode(content) if content else ''
        headers.append(('Content-Length', len(content_base64)))
        return request.make_response(content_base64, headers)

    @http.route()
    def load_templates(self, **kwargs):
        base_url = request.httprequest.base_url
        templates = [
            'mail/static/src/xml/abstract_thread_window.xml',
            'mail/static/src/xml/discuss.xml',
            'mail/static/src/xml/thread.xml',
            'im_livechat/static/src/xml/im_livechat.xml',
            'advanced_helpdesk/static/src/xml/im_livechat_pre_question_form.xml',
        ]
        return [tools.file_open(tmpl, 'rb').read() for tmpl in templates]