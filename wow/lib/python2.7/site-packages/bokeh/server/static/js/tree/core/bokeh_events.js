"use strict";
var __extends = (this && this.__extends) || (function () {
    var extendStatics = Object.setPrototypeOf ||
        ({ __proto__: [] } instanceof Array && function (d, b) { d.__proto__ = b; }) ||
        function (d, b) { for (var p in b) if (b.hasOwnProperty(p)) d[p] = b[p]; };
    return function (d, b) {
        extendStatics(d, b);
        function __() { this.constructor = d; }
        d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
    };
})();
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
Object.defineProperty(exports, "__esModule", { value: true });
var logging_1 = require("./logging");
var object_1 = require("./util/object");
var event_classes = {};
function register_event_class(event_name) {
    return function (event_cls) {
        event_cls.prototype.event_name = event_name;
        event_classes[event_name] = event_cls;
    };
}
exports.register_event_class = register_event_class;
function register_with_event(event_cls) {
    var models = [];
    for (var _i = 1; _i < arguments.length; _i++) {
        models[_i - 1] = arguments[_i];
    }
    var applicable_models = event_cls.prototype.applicable_models.concat(models);
    event_cls.prototype.applicable_models = applicable_models;
}
exports.register_with_event = register_with_event;
var BokehEvent = (function () {
    function BokehEvent(options) {
        if (options === void 0) { options = {}; }
        this._options = options;
        if (options.model_id) {
            this.model_id = options.model_id;
        }
    }
    BokehEvent.prototype.set_model_id = function (id) {
        this._options.model_id = id;
        this.model_id = id;
        return this;
    };
    BokehEvent.prototype.is_applicable_to = function (obj) {
        return this.applicable_models.some(function (model) { return obj instanceof model; });
    };
    BokehEvent.event_class = function (e) {
        // Given an event with a type attribute matching the event_name,
        // return the appropriate BokehEvent class
        if (e.type) {
            return event_classes[e.type];
        }
        else {
            logging_1.logger.warn('BokehEvent.event_class required events with a string type attribute');
        }
    };
    BokehEvent.prototype.toJSON = function () {
        return {
            event_name: this.event_name,
            event_values: object_1.clone(this._options),
        };
    };
    BokehEvent.prototype._customize_event = function (model) {
        return this;
    };
    return BokehEvent;
}());
exports.BokehEvent = BokehEvent;
BokehEvent.prototype.applicable_models = [];
var ButtonClick = (function (_super) {
    __extends(ButtonClick, _super);
    function ButtonClick() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return ButtonClick;
}(BokehEvent));
ButtonClick = __decorate([
    register_event_class("button_click")
], ButtonClick);
exports.ButtonClick = ButtonClick;
// A UIEvent is an event originating on a PlotCanvas this includes
// DOM events such as keystrokes as well as hammer events and LOD events.
var UIEvent = (function (_super) {
    __extends(UIEvent, _super);
    function UIEvent() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return UIEvent;
}(BokehEvent));
exports.UIEvent = UIEvent;
var LODStart = (function (_super) {
    __extends(LODStart, _super);
    function LODStart() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return LODStart;
}(UIEvent));
LODStart = __decorate([
    register_event_class("lodstart")
], LODStart);
exports.LODStart = LODStart;
var LODEnd = (function (_super) {
    __extends(LODEnd, _super);
    function LODEnd() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return LODEnd;
}(UIEvent));
LODEnd = __decorate([
    register_event_class("lodend")
], LODEnd);
exports.LODEnd = LODEnd;
var PointEvent = (function (_super) {
    __extends(PointEvent, _super);
    function PointEvent(options) {
        var _this = _super.call(this, options) || this;
        _this.sx = options.sx;
        _this.sy = options.sy;
        _this.x = null;
        _this.y = null;
        return _this;
    }
    PointEvent.from_event = function (e, model_id) {
        if (model_id === void 0) { model_id = null; }
        return new this({ sx: e.bokeh['sx'], sy: e.bokeh['sy'], model_id: model_id });
    };
    PointEvent.prototype._customize_event = function (plot) {
        var xmapper = plot.plot_canvas.frame.x_mappers['default'];
        var ymapper = plot.plot_canvas.frame.y_mappers['default'];
        this.x = xmapper.map_from_target(plot.plot_canvas.canvas.sx_to_vx(this.sx));
        this.y = ymapper.map_from_target(plot.plot_canvas.canvas.sy_to_vy(this.sy));
        this._options['x'] = this.x;
        this._options['y'] = this.y;
        return this;
    };
    return PointEvent;
}(UIEvent));
exports.PointEvent = PointEvent;
var Pan = (function (_super) {
    __extends(Pan, _super);
    function Pan(options) {
        if (options === void 0) { options = {}; }
        var _this = _super.call(this, options) || this;
        _this.delta_x = options.delta_x;
        _this.delta_y = options.delta_y;
        return _this;
    }
    Pan.from_event = function (e, model_id) {
        if (model_id === void 0) { model_id = null; }
        return new this({
            sx: e.bokeh['sx'],
            sy: e.bokeh['sy'],
            delta_x: e.deltaX,
            delta_y: e.deltaY,
            direction: e.direction,
            model_id: model_id
        });
    };
    return Pan;
}(PointEvent));
Pan = __decorate([
    register_event_class("pan")
], Pan);
exports.Pan = Pan;
var Pinch = (function (_super) {
    __extends(Pinch, _super);
    function Pinch(options) {
        if (options === void 0) { options = {}; }
        var _this = _super.call(this, options) || this;
        _this.scale = options.scale;
        return _this;
    }
    Pinch.from_event = function (e, model_id) {
        if (model_id === void 0) { model_id = null; }
        return new this({
            sx: e.bokeh['sx'],
            sy: e.bokeh['sy'],
            scale: e.scale,
            model_id: model_id,
        });
    };
    return Pinch;
}(PointEvent));
Pinch = __decorate([
    register_event_class("pinch")
], Pinch);
exports.Pinch = Pinch;
var MouseWheel = (function (_super) {
    __extends(MouseWheel, _super);
    function MouseWheel(options) {
        if (options === void 0) { options = {}; }
        var _this = _super.call(this, options) || this;
        _this.delta = options.delta;
        return _this;
    }
    MouseWheel.from_event = function (e, model_id) {
        if (model_id === void 0) { model_id = null; }
        return new this({
            sx: e.bokeh['sx'],
            sy: e.bokeh['sy'],
            delta: e.delta,
            model_id: model_id,
        });
    };
    return MouseWheel;
}(PointEvent));
MouseWheel = __decorate([
    register_event_class("wheel")
], MouseWheel);
exports.MouseWheel = MouseWheel;
var MouseMove = (function (_super) {
    __extends(MouseMove, _super);
    function MouseMove() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return MouseMove;
}(PointEvent));
MouseMove = __decorate([
    register_event_class("mousemove")
], MouseMove);
exports.MouseMove = MouseMove;
var MouseEnter = (function (_super) {
    __extends(MouseEnter, _super);
    function MouseEnter() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return MouseEnter;
}(PointEvent));
MouseEnter = __decorate([
    register_event_class("mouseenter")
], MouseEnter);
exports.MouseEnter = MouseEnter;
var MouseLeave = (function (_super) {
    __extends(MouseLeave, _super);
    function MouseLeave() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return MouseLeave;
}(PointEvent));
MouseLeave = __decorate([
    register_event_class("mouseleave")
], MouseLeave);
exports.MouseLeave = MouseLeave;
var Tap = (function (_super) {
    __extends(Tap, _super);
    function Tap() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return Tap;
}(PointEvent));
Tap = __decorate([
    register_event_class("tap")
], Tap);
exports.Tap = Tap;
var DoubleTap = (function (_super) {
    __extends(DoubleTap, _super);
    function DoubleTap() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return DoubleTap;
}(PointEvent));
DoubleTap = __decorate([
    register_event_class("doubletap")
], DoubleTap);
exports.DoubleTap = DoubleTap;
var Press = (function (_super) {
    __extends(Press, _super);
    function Press() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return Press;
}(PointEvent));
Press = __decorate([
    register_event_class("press")
], Press);
exports.Press = Press;
var PanStart = (function (_super) {
    __extends(PanStart, _super);
    function PanStart() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return PanStart;
}(PointEvent));
PanStart = __decorate([
    register_event_class("panstart")
], PanStart);
exports.PanStart = PanStart;
var PanEnd = (function (_super) {
    __extends(PanEnd, _super);
    function PanEnd() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return PanEnd;
}(PointEvent));
PanEnd = __decorate([
    register_event_class("panend")
], PanEnd);
exports.PanEnd = PanEnd;
var PinchStart = (function (_super) {
    __extends(PinchStart, _super);
    function PinchStart() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return PinchStart;
}(PointEvent));
PinchStart = __decorate([
    register_event_class("pinchstart")
], PinchStart);
exports.PinchStart = PinchStart;
var PinchEnd = (function (_super) {
    __extends(PinchEnd, _super);
    function PinchEnd() {
        return _super !== null && _super.apply(this, arguments) || this;
    }
    return PinchEnd;
}(PointEvent));
PinchEnd = __decorate([
    register_event_class("pinchend")
], PinchEnd);
exports.PinchEnd = PinchEnd;
