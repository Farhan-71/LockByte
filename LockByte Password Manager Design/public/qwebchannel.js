// Standalone QWebChannel implementation for Qt WebEngine with Promise support
(function() {
    "use strict";

    var QWebChannel = function(transport, initCallback) {
        if (typeof transport !== "object" || typeof transport.send !== "function") {
            console.error("The QWebChannel expects a transport object with a send function and onmessage callback property." +
                          " Given transport is " + typeof(transport));
            return;
        }

        var channel = this;
        this.transport = transport;
        this.send = function(data) {
            this.transport.send(JSON.stringify(data));
        };
        this.transport.onmessage = function(message) {
            var data = message.data;
            if (typeof data === "string") {
                data = JSON.parse(data);
            }
            switch (data.type) {
                case 1: // signal
                    channel.handleSignal(data);
                    break;
                case 2: // response
                    channel.handleResponse(data);
                    break;
                case 3: // init
                    channel.handleInit(data);
                    break;
                case 4: // idle
                    break;
            }
        };

        this.execCallbacks = {};
        this.execId = 0;
        this.objects = {};

        this.send({type: 3, id: this.execId++}); // QWebChannelMessageTypes.init

        this.handleInit = function(data) {
            for (var objectName in data.objects) {
                new QObject(objectName, data.objects[objectName], channel);
            }
            for (var objectName in data.objects) {
                channel.objects[objectName].__setupSignals__();
            }
            if (initCallback) {
                initCallback(channel);
            }
        };

        this.handleSignal = function(data) {
            var object = channel.objects[data.object];
            if (object) {
                object.__signal__(data.signal, data.args);
            }
        };

        this.handleResponse = function(data) {
            if (data.id !== undefined) {
                var callback = channel.execCallbacks[data.id];
                delete channel.execCallbacks[data.id];
                if (callback) {
                    callback(data.response);
                }
            }
        };
    };

    function QObject(name, data, channel) {
        this.__id__ = name;
        var self = this;

        data.methods.forEach(function(method) {
            var methodName = method[0];
            var methodId = method[1];
            self[methodName] = function() {
                var args = Array.prototype.slice.call(arguments);
                var callback;
                if (typeof args[args.length - 1] === "function") {
                    callback = args.pop();
                    var id = channel.execId++;
                    channel.execCallbacks[id] = callback;
                    channel.send({
                        type: 2, // exec
                        object: self.__id__,
                        method: methodId,
                        args: args,
                        id: id
                    });
                } else {
                    // Promise wrapper for modern async/await in JS
                    return new Promise(function(resolve) {
                        var id = channel.execId++;
                        channel.execCallbacks[id] = resolve;
                        channel.send({
                            type: 2, // exec
                            object: self.__id__,
                            method: methodId,
                            args: args,
                            id: id
                        });
                    });
                }
            };
        });

        data.signals.forEach(function(signal) {
            var signalName = signal[0];
            var signalIndex = signal[1];
            self[signalName] = {
                connect: function(callback) {
                    if (typeof callback !== "function") {
                        console.error("Signal handler must be a function.");
                        return;
                    }
                    if (!self.__signals__[signalIndex]) {
                        self.__signals__[signalIndex] = [];
                    }
                    self.__signals__[signalIndex].push(callback);
                }
            };
        });

        this.__signals__ = {};
        this.__signal__ = function(signalIndex, args) {
            var handlers = self.__signals__[signalIndex];
            if (handlers) {
                handlers.forEach(function(handler) {
                    handler.apply(handler, args);
                });
            }
        };

        this.__setupSignals__ = function() {};
        channel.objects[name] = this;
    }

    window.QWebChannel = QWebChannel;
})();
