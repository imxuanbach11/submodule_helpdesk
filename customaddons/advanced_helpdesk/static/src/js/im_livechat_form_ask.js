odoo.define('advanced_helpdesk.im_livechat', function (require) {
    "use strict";
    var ImLivechatLib = require('im_livechat.im_livechat');
    var ImLivechatFormAsk = ImLivechatLib.LivechatButton;
    var concurrency = require('web.concurrency');
    var config = require('web.config');
    var core = require('web.core');
    var session = require('web.session');
    var time = require('web.time');
    var utils = require('web.utils');
    var Widget = require('web.Widget');

    var WebsiteLivechat = require('im_livechat.model.WebsiteLivechat');
    var WebsiteLivechatMessage = require('im_livechat.model.WebsiteLivechatMessage');
    var WebsiteLivechatWindow = require('im_livechat.WebsiteLivechatWindow');

    var _t = core._t;
    var QWeb = core.qweb;

    var PreQuestion = Widget.extend({
        template: 'advanced_helpdesk.PreQuestion',
        events: {
            'click .o_email_chat_button': '_onFinishPreQuestion',
        },
        init: function (parent, livechat) {
            this._super(parent);
            this._livechat = livechat;
            this.server_origin = session.origin;
            this.dp = new concurrency.DropPrevious();
        },
        _onFinishPreQuestion: function () {
            var self = this;
            var error = false;
            var $email = this.$('#o_pre_email');
            var $phone = this.$('#o_pre_phone');
            var $department = this.$('#o_pre_department');
            var $order_id = this.$('#o_pre_order_id');
            var $message = this.$('#o_pre_message');

            if (!utils.is_email($email.val())) {
                error = true;
                $email.addClass('is-invalid').prop('title', _t('Invalid email address'));
            }
            if ($message.val() && $message.val().length == 0) {
                error = true;
                $message.addClass('is-invalid').prop('title', _t('Invalid message'));
            }
            if (error == false) {
                // disable field
                $email.removeAttr('title').removeClass('is-invalid').prop('disabled', true);
                $phone.removeAttr('title').removeClass('is-invalid').prop('disabled', true);
                $department.removeAttr('title').removeClass('is-invalid').prop('disabled', true);
                $order_id.removeAttr('title').removeClass('is-invalid').prop('disabled', true);
                $message.removeAttr('title').removeClass('is-invalid').prop('disabled', true);
                // disable button
                this.$('.o_email_chat_button').prop('disabled', true);
                // trigger send message
                var first_message = ''
                first_message += '╠╦═ '
                first_message += 'Email: ' + $email.val() + '\n';
                first_message += 'Phone: ' + $phone.val() + '\n';
                first_message += 'Department: ' + $department.val() + '\n';
                first_message += 'Order ID: ' + $order_id.val() + '\n';
                first_message += 'Message: ' + $message.val() + '\n';
                self.trigger('send_first_message', {origin_message: first_message, content: $message.val()});
            }
        }
    });


    ImLivechatFormAsk.include({
        _openChat: _.debounce(function () {
            if (this._openingChat) {
                return;
            }
            var self = this;
            var cookie = utils.get_cookie('im_livechat_session');
            var def;
            this._openingChat = true;
            clearTimeout(this._autoPopupTimeout);
            if (cookie) {
                def = Promise.resolve(JSON.parse(cookie));
            } else {
                this._messages = []; // re-initialize messages cache
                def = session.rpc('/im_livechat/get_session', {
                    channel_id: this.options.channel_id,
                    anonymous_name: this.options.default_username,
                    previous_operator_id: this._get_previous_operator_id(),
                }, {shadow: true});
            }
            def.then(function (livechatData) {
                // if (!livechatData || !livechatData.operator_pid) {
                //     alert(_t("None of our collaborators seem to be available, please try again later."));
                // } else {
                    self._livechat = new WebsiteLivechat({
                        parent: self,
                        data: livechatData
                    });
                    return self._openChatWindow().then(function () {
                        if (!self._history) {
                            self._askPreQuestion();
                            self._sendWelcomeMessage();
                        } else {
                            if (self._history.length > 0) {
                                self._sendMessage({content: '╠╦═ ' + window.location.href})
                            } else {
                                self._askPreQuestion()
                            }
                        }
                        self._renderMessages();
                        self.call('bus_service', 'addChannel', self._livechat.getUUID());
                        self.call('bus_service', 'startPolling');

                        utils.set_cookie('im_livechat_session', JSON.stringify(self._livechat.toData()), 60 * 60);
                        utils.set_cookie('im_livechat_auto_popup', JSON.stringify(false), 60 * 60);
                        if (livechatData.operator_pid[0]) {
                            // livechatData.operator_pid contains a tuple (id, name)
                            // we are only interested in the id
                            var operatorPidId = livechatData.operator_pid[0];
                            var oneWeek = 7 * 24 * 60 * 60;
                            utils.set_cookie('im_livechat_previous_operator_pid', operatorPidId, oneWeek);
                        }
                    });
                // }
            }).then(function () {
                self._openingChat = false;
            }).guardedCatch(function () {
                self._openingChat = false;
            });
        }, 200, true),
        _askPreQuestion: function () {
            this._chatWindow.$('.o_thread_composer input').prop('disabled', true);

            var pre_question = new PreQuestion(this, this._livechat);
            this._chatWindow.replaceContentWith(pre_question);

            pre_question.on('send_first_message', this, this._sendFirstMessage);
        },
        _buttonSubmit: function ani() {
            document.getElementById('plane').className = 'animation';
        },
        // function anitwo(){
        //     document.getElementById('bg').className ='animation2';
        // }
        _sendFirstMessage: function (message) {
            var self = this
            // enable send message
            this._chatWindow.$('.o_thread_composer input').prop('disabled', false);
            // destroy chat window
            this._chatWindow.destroy();
            // re init chat window
            self._openChatWindow();
            session
                .rpc('/mail/chat_post', {uuid: this._livechat.getUUID(), message_content: message.origin_message});
            return session
                .rpc('/mail/chat_post', {uuid: this._livechat.getUUID(), message_content: message.content})
                .then(function () {
                    self._chatWindow.scrollToBottom();
                });
        }
    });
});
odoo.define('advanced_helpdesk.im_livechat.model.WebsiteLivechat', function (require) {
    "use strict";
    var ImLivechatLib = require('im_livechat.model.WebsiteLivechat')
    ImLivechatLib.include({
        setMessages: function (messages) {
            var new_message = [];
            for (var i in messages) {
                var mess = messages[i]['_body'];
                if (mess.includes('<p>╠╦═ ')) {
                    continue
                }
                new_message.push(messages[i])
            }
            messages = new_message
            this._messages = messages
        }
    })
});
