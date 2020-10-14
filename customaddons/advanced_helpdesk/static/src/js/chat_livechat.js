odoo.define('advanced_helpdesk.chat_livechat', function (require) {
'use strict';

    var FormController = require('web.FormController');
    var FormView = require('web.FormView');
    var FormRenderer = require('web.FormRenderer');
    var viewRegistry = require('web.view_registry');

    var EmployeeFormRenderer = FormRenderer.extend({

        /**
         * @override
         */
        _render: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                var $chat_button = self.$el.find('.o_advanced_helpdesk_visitor_chat_btn');
                $chat_button.off('click').on('click', self._onOpenChat.bind(self));
            });
        },

        destroy: function () {
            this.$el.find('.o_advanced_helpdesk_visitor_chat_btn').off('click');
            return this._super();
        },

        _onOpenChat: function(ev) {
            ev.preventDefault();
            ev.stopImmediatePropagation();
            this.trigger_up('open_chat', {
                channel_id: this.state.data.id
            });
            return true;
        },
    });

    var EmployeeFormController = FormController.extend({
        custom_events: _.extend({}, FormController.prototype.custom_events, {
            open_chat: '_onOpenChat'
        }),

        _onOpenChat: function(ev) {
            var self = this;
            var dmChat = this.call('mail_service', 'getChannel', ev.data.channel_id);
            if (dmChat) {
                dmChat.detach();
            }
        },
    });

    var EmployeeFormView = FormView.extend({
        config: _.extend({}, FormView.prototype.config, {
            Controller: EmployeeFormController,
            Renderer: EmployeeFormRenderer
        }),
    });

    viewRegistry.add('advanced_helpdesk_mail_channel_form', EmployeeFormView);
    return EmployeeFormView;
});