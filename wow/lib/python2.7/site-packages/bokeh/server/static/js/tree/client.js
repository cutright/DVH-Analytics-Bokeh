"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var ClientConnection, ClientSession, Message, message_handlers;
var es6_promise_1 = require("es6-promise");
var logging_1 = require("./core/logging");
var string_1 = require("./core/util/string");
var object_1 = require("./core/util/object");
var document_1 = require("./document");
exports.DEFAULT_SERVER_WEBSOCKET_URL = "ws://localhost:5006/ws";
exports.DEFAULT_SESSION_ID = "default";
Message = (function () {
    function Message(header1, metadata1, content1) {
        this.header = header1;
        this.metadata = metadata1;
        this.content = content1;
        this.buffers = [];
    }
    Message.assemble = function (header_json, metadata_json, content_json) {
        var content, e, header, metadata;
        try {
            header = JSON.parse(header_json);
            metadata = JSON.parse(metadata_json);
            content = JSON.parse(content_json);
            return new Message(header, metadata, content);
        }
        catch (error1) {
            e = error1;
            logging_1.logger.error("Failure parsing json " + e + " " + header_json + " " + metadata_json + " " + content_json, e);
            throw e;
        }
    };
    Message.create_header = function (msgtype, options) {
        var header;
        header = {
            'msgid': string_1.uniqueId(),
            'msgtype': msgtype
        };
        return object_1.extend(header, options);
    };
    Message.create = function (msgtype, header_options, content) {
        var header;
        if (content == null) {
            content = {};
        }
        header = Message.create_header(msgtype, header_options);
        return new Message(header, {}, content);
    };
    Message.prototype.send = function (socket) {
        var content_json, e, header_json, metadata_json;
        try {
            header_json = JSON.stringify(this.header);
            metadata_json = JSON.stringify(this.metadata);
            content_json = JSON.stringify(this.content);
            socket.send(header_json);
            socket.send(metadata_json);
            return socket.send(content_json);
        }
        catch (error1) {
            e = error1;
            logging_1.logger.error("Error sending ", this, e);
            throw e;
        }
    };
    Message.prototype.complete = function () {
        if ((this.header != null) && (this.metadata != null) && (this.content != null)) {
            if ('num_buffers' in this.header) {
                return this.buffers.length === this.header['num_buffers'];
            }
            else {
                return true;
            }
        }
        else {
            return false;
        }
    };
    Message.prototype.add_buffer = function (buffer) {
        return this.buffers.push(buffer);
    };
    Message.prototype._header_field = function (field) {
        if (field in this.header) {
            return this.header[field];
        }
        else {
            return null;
        }
    };
    Message.prototype.msgid = function () {
        return this._header_field('msgid');
    };
    Message.prototype.msgtype = function () {
        return this._header_field('msgtype');
    };
    Message.prototype.sessid = function () {
        return this._header_field('sessid');
    };
    Message.prototype.reqid = function () {
        return this._header_field('reqid');
    };
    Message.prototype.problem = function () {
        if (!('msgid' in this.header)) {
            return "No msgid in header";
        }
        else if (!('msgtype' in this.header)) {
            return "No msgtype in header";
        }
        else {
            return null;
        }
    };
    return Message;
})();
message_handlers = {
    'PATCH-DOC': function (connection, message) {
        return connection._for_session(function (session) {
            return session._handle_patch(message);
        });
    },
    'OK': function (connection, message) {
        return logging_1.logger.debug("Unhandled OK reply to " + (message.reqid()));
    },
    'ERROR': function (connection, message) {
        return logging_1.logger.error("Unhandled ERROR reply to " + (message.reqid()) + ": " + message.content['text']);
    }
};
ClientConnection = (function () {
    ClientConnection._connection_count = 0;
    function ClientConnection(url1, id, args_string1, _on_have_session_hook, _on_closed_permanently_hook) {
        this.url = url1;
        this.id = id;
        this.args_string = args_string1;
        this._on_have_session_hook = _on_have_session_hook;
        this._on_closed_permanently_hook = _on_closed_permanently_hook;
        this._number = ClientConnection._connection_count;
        ClientConnection._connection_count = this._number + 1;
        if (this.url == null) {
            this.url = exports.DEFAULT_SERVER_WEBSOCKET_URL;
        }
        if (this.id == null) {
            this.id = exports.DEFAULT_SESSION_ID;
        }
        logging_1.logger.debug("Creating websocket " + this._number + " to '" + this.url + "' session '" + this.id + "'");
        this.socket = null;
        this.closed_permanently = false;
        this._fragments = [];
        this._partial = null;
        this._current_handler = null;
        this._pending_ack = null;
        this._pending_replies = {};
        this.session = null;
    }
    ClientConnection.prototype._for_session = function (f) {
        if (this.session !== null) {
            return f(this.session);
        }
    };
    ClientConnection.prototype.connect = function () {
        var error, ref, versioned_url;
        if (this.closed_permanently) {
            return es6_promise_1.Promise.reject(new Error("Cannot connect() a closed ClientConnection"));
        }
        if (this.socket != null) {
            return es6_promise_1.Promise.reject(new Error("Already connected"));
        }
        this._fragments = [];
        this._partial = null;
        this._pending_replies = {};
        this._current_handler = null;
        try {
            versioned_url = this.url + "?bokeh-protocol-version=1.0&bokeh-session-id=" + this.id;
            if (((ref = this.args_string) != null ? ref.length : void 0) > 0) {
                versioned_url += "&" + this.args_string;
            }
            if (window.MozWebSocket != null) {
                this.socket = new MozWebSocket(versioned_url);
            }
            else {
                this.socket = new WebSocket(versioned_url);
            }
            return new es6_promise_1.Promise((function (_this) {
                return function (resolve, reject) {
                    _this.socket.binarytype = "arraybuffer";
                    _this.socket.onopen = function () {
                        return _this._on_open(resolve, reject);
                    };
                    _this.socket.onmessage = function (event) {
                        return _this._on_message(event);
                    };
                    _this.socket.onclose = function (event) {
                        return _this._on_close(event);
                    };
                    return _this.socket.onerror = function () {
                        return _this._on_error(reject);
                    };
                };
            })(this));
        }
        catch (error1) {
            error = error1;
            logging_1.logger.error("websocket creation failed to url: " + this.url);
            logging_1.logger.error(" - " + error);
            return es6_promise_1.Promise.reject(error);
        }
    };
    ClientConnection.prototype.close = function () {
        if (!this.closed_permanently) {
            logging_1.logger.debug("Permanently closing websocket connection " + this._number);
            this.closed_permanently = true;
            if (this.socket != null) {
                this.socket.close(1000, "close method called on ClientConnection " + this._number);
            }
            this._for_session(function (session) {
                return session._connection_closed();
            });
            if (this._on_closed_permanently_hook != null) {
                this._on_closed_permanently_hook();
                return this._on_closed_permanently_hook = null;
            }
        }
    };
    ClientConnection.prototype._schedule_reconnect = function (milliseconds) {
        var retry;
        retry = (function (_this) {
            return function () {
                if (true || _this.closed_permanently) {
                    if (!_this.closed_permanently) {
                        logging_1.logger.info("Websocket connection " + _this._number + " disconnected, will not attempt to reconnect");
                    }
                }
                else {
                    logging_1.logger.debug("Attempting to reconnect websocket " + _this._number);
                    return _this.connect();
                }
            };
        })(this);
        return setTimeout(retry, milliseconds);
    };
    ClientConnection.prototype.send = function (message) {
        var e;
        try {
            if (this.socket === null) {
                throw new Error("not connected so cannot send " + message);
            }
            return message.send(this.socket);
        }
        catch (error1) {
            e = error1;
            return logging_1.logger.error("Error sending message ", e, message);
        }
    };
    ClientConnection.prototype.send_event = function (event) {
        var message;
        message = Message.create('EVENT', {}, JSON.stringify(event));
        return this.send(message);
    };
    ClientConnection.prototype.send_with_reply = function (message) {
        var promise;
        promise = new es6_promise_1.Promise((function (_this) {
            return function (resolve, reject) {
                _this._pending_replies[message.msgid()] = [resolve, reject];
                return _this.send(message);
            };
        })(this));
        return promise.then(function (message) {
            if (message.msgtype() === 'ERROR') {
                throw new Error("Error reply " + message.content['text']);
            }
            else {
                return message;
            }
        }, function (error) {
            throw error;
        });
    };
    ClientConnection.prototype._pull_doc_json = function () {
        var message, promise;
        message = Message.create('PULL-DOC-REQ', {});
        promise = this.send_with_reply(message);
        return promise.then(function (reply) {
            if (!('doc' in reply.content)) {
                throw new Error("No 'doc' field in PULL-DOC-REPLY");
            }
            return reply.content['doc'];
        }, function (error) {
            throw error;
        });
    };
    ClientConnection.prototype._repull_session_doc = function () {
        if (this.session === null) {
            logging_1.logger.debug("Pulling session for first time");
        }
        else {
            logging_1.logger.debug("Repulling session");
        }
        return this._pull_doc_json().then((function (_this) {
            return function (doc_json) {
                var document, patch, patch_message;
                if (_this.session === null) {
                    if (_this.closed_permanently) {
                        return logging_1.logger.debug("Got new document after connection was already closed");
                    }
                    else {
                        document = document_1.Document.from_json(doc_json);
                        patch = document_1.Document._compute_patch_since_json(doc_json, document);
                        if (patch.events.length > 0) {
                            logging_1.logger.debug("Sending " + patch.events.length + " changes from model construction back to server");
                            patch_message = Message.create('PATCH-DOC', {}, patch);
                            _this.send(patch_message);
                        }
                        _this.session = new ClientSession(_this, document, _this.id);
                        logging_1.logger.debug("Created a new session from new pulled doc");
                        if (_this._on_have_session_hook != null) {
                            _this._on_have_session_hook(_this.session);
                            return _this._on_have_session_hook = null;
                        }
                    }
                }
                else {
                    _this.session.document.replace_with_json(doc_json);
                    return logging_1.logger.debug("Updated existing session with new pulled doc");
                }
            };
        })(this), function (error) {
            throw error;
        })["catch"](function (error) {
            if (console.trace != null) {
                console.trace(error);
            }
            return logging_1.logger.error("Failed to repull session " + error);
        });
    };
    ClientConnection.prototype._on_open = function (resolve, reject) {
        logging_1.logger.info("Websocket connection " + this._number + " is now open");
        this._pending_ack = [resolve, reject];
        return this._current_handler = (function (_this) {
            return function (message) {
                return _this._awaiting_ack_handler(message);
            };
        })(this);
    };
    ClientConnection.prototype._on_message = function (event) {
        var e;
        try {
            return this._on_message_unchecked(event);
        }
        catch (error1) {
            e = error1;
            return logging_1.logger.error("Error handling message: " + e + ", " + event);
        }
    };
    ClientConnection.prototype._on_message_unchecked = function (event) {
        var msg, problem;
        if (this._current_handler == null) {
            logging_1.logger.error("got a message but haven't set _current_handler");
        }
        if (event.data instanceof ArrayBuffer) {
            if ((this._partial != null) && !this._partial.complete()) {
                this._partial.add_buffer(event.data);
            }
            else {
                this._close_bad_protocol("Got binary from websocket but we were expecting text");
            }
        }
        else if (this._partial != null) {
            this._close_bad_protocol("Got text from websocket but we were expecting binary");
        }
        else {
            this._fragments.push(event.data);
            if (this._fragments.length === 3) {
                this._partial = Message.assemble(this._fragments[0], this._fragments[1], this._fragments[2]);
                this._fragments = [];
                problem = this._partial.problem();
                if (problem !== null) {
                    this._close_bad_protocol(problem);
                }
            }
        }
        if ((this._partial != null) && this._partial.complete()) {
            msg = this._partial;
            this._partial = null;
            return this._current_handler(msg);
        }
    };
    ClientConnection.prototype._on_close = function (event) {
        var pop_pending, promise_funcs;
        logging_1.logger.info("Lost websocket " + this._number + " connection, " + event.code + " (" + event.reason + ")");
        this.socket = null;
        if (this._pending_ack != null) {
            this._pending_ack[1](new Error("Lost websocket connection, " + event.code + " (" + event.reason + ")"));
            this._pending_ack = null;
        }
        pop_pending = (function (_this) {
            return function () {
                var promise_funcs, ref, reqid;
                ref = _this._pending_replies;
                for (reqid in ref) {
                    promise_funcs = ref[reqid];
                    delete _this._pending_replies[reqid];
                    return promise_funcs;
                }
                return null;
            };
        })(this);
        promise_funcs = pop_pending();
        while (promise_funcs !== null) {
            promise_funcs[1]("Disconnected");
            promise_funcs = pop_pending();
        }
        if (!this.closed_permanently) {
            return this._schedule_reconnect(2000);
        }
    };
    ClientConnection.prototype._on_error = function (reject) {
        logging_1.logger.debug("Websocket error on socket  " + this._number);
        return reject(new Error("Could not open websocket"));
    };
    ClientConnection.prototype._close_bad_protocol = function (detail) {
        logging_1.logger.error("Closing connection: " + detail);
        if (this.socket != null) {
            return this.socket.close(1002, detail);
        }
    };
    ClientConnection.prototype._awaiting_ack_handler = function (message) {
        if (message.msgtype() === "ACK") {
            this._current_handler = (function (_this) {
                return function (message) {
                    return _this._steady_state_handler(message);
                };
            })(this);
            this._repull_session_doc();
            if (this._pending_ack != null) {
                this._pending_ack[0](this);
                return this._pending_ack = null;
            }
        }
        else {
            return this._close_bad_protocol("First message was not an ACK");
        }
    };
    ClientConnection.prototype._steady_state_handler = function (message) {
        var promise_funcs;
        if (message.reqid() in this._pending_replies) {
            promise_funcs = this._pending_replies[message.reqid()];
            delete this._pending_replies[message.reqid()];
            return promise_funcs[0](message);
        }
        else if (message.msgtype() in message_handlers) {
            return message_handlers[message.msgtype()](this, message);
        }
        else {
            return logging_1.logger.debug("Doing nothing with message " + (message.msgtype()));
        }
    };
    return ClientConnection;
})();
ClientSession = (function () {
    function ClientSession(_connection, document1, id) {
        this._connection = _connection;
        this.document = document1;
        this.id = id;
        this.document_listener = (function (_this) {
            return function (event) {
                return _this._document_changed(event);
            };
        })(this);
        this.document.on_change(this.document_listener);
        this.event_manager = this.document.event_manager;
        this.event_manager.session = this;
    }
    ClientSession.prototype.close = function () {
        return this._connection.close();
    };
    ClientSession.prototype.send_event = function (type) {
        return this._connection.send_event(type);
    };
    ClientSession.prototype._connection_closed = function () {
        return this.document.remove_on_change(this.document_listener);
    };
    ClientSession.prototype.request_server_info = function () {
        var message, promise;
        message = Message.create('SERVER-INFO-REQ', {});
        promise = this._connection.send_with_reply(message);
        return promise.then(function (reply) {
            return reply.content;
        });
    };
    ClientSession.prototype.force_roundtrip = function () {
        return this.request_server_info().then(function (ignored) {
            return void 0;
        });
    };
    ClientSession.prototype._document_changed = function (event) {
        var patch;
        if (event.setter_id === this.id) {
            return;
        }
        if (event instanceof document_1.ModelChangedEvent && !(event.attr in event.model.serializable_attributes())) {
            return;
        }
        patch = Message.create('PATCH-DOC', {}, this.document.create_json_patch([event]));
        return this._connection.send(patch);
    };
    ClientSession.prototype._handle_patch = function (message) {
        return this.document.apply_json_patch(message.content, this.id);
    };
    return ClientSession;
})();
exports.pull_session = function (url, session_id, args_string) {
    var connection, promise, rejecter;
    rejecter = null;
    connection = null;
    promise = new es6_promise_1.Promise(function (resolve, reject) {
        connection = new ClientConnection(url, session_id, args_string, function (session) {
            var e;
            try {
                return resolve(session);
            }
            catch (error1) {
                e = error1;
                logging_1.logger.error("Promise handler threw an error, closing session " + error);
                session.close();
                throw e;
            }
        }, function () {
            return reject(new Error("Connection was closed before we successfully pulled a session"));
        });
        return connection.connect().then(function (whatever) { }, function (error) {
            logging_1.logger.error("Failed to connect to Bokeh server " + error);
            throw error;
        });
    });
    promise.close = function () {
        return connection.close();
    };
    return promise;
};
