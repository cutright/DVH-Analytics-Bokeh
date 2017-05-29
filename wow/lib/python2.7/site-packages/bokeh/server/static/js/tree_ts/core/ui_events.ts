var extend1 = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

import * as Hammer from "hammerjs";

import {
  Events
} from "./events";

import {
  logger
} from "./logging";

import {
  offset
} from "./dom";

import {
  getDeltaY
} from "./util/wheel";

import {
  extend
} from "./util/object";

import {
  BokehEvent
} from "./bokeh_events";

import {
  any
} from "./util/array";

export var UIEvents = (function() {
  extend1(UIEvents.prototype, Events);

  function UIEvents(plot_view, toolbar, hit_area, plot) {
    this.plot_view = plot_view;
    this.toolbar = toolbar;
    this.hit_area = hit_area;
    this.plot = plot;
    this._configure_hammerjs();
  }

  UIEvents.prototype._configure_hammerjs = function() {
    this.hammer = new Hammer(this.hit_area);
    this.hammer.get('doubletap').recognizeWith('tap');
    this.hammer.get('tap').requireFailure('doubletap');
    this.hammer.get('doubletap').dropRequireFailure('tap');
    this.hammer.on('doubletap', (function(_this) {
      return function(e) {
        return _this._doubletap(e);
      };
    })(this));
    this.hammer.on('tap', (function(_this) {
      return function(e) {
        return _this._tap(e);
      };
    })(this));
    this.hammer.on('press', (function(_this) {
      return function(e) {
        return _this._press(e);
      };
    })(this));
    this.hammer.get('pan').set({
      direction: Hammer.DIRECTION_ALL
    });
    this.hammer.on('panstart', (function(_this) {
      return function(e) {
        return _this._pan_start(e);
      };
    })(this));
    this.hammer.on('pan', (function(_this) {
      return function(e) {
        return _this._pan(e);
      };
    })(this));
    this.hammer.on('panend', (function(_this) {
      return function(e) {
        return _this._pan_end(e);
      };
    })(this));
    this.hammer.get('pinch').set({
      enable: true
    });
    this.hammer.on('pinchstart', (function(_this) {
      return function(e) {
        return _this._pinch_start(e);
      };
    })(this));
    this.hammer.on('pinch', (function(_this) {
      return function(e) {
        return _this._pinch(e);
      };
    })(this));
    this.hammer.on('pinchend', (function(_this) {
      return function(e) {
        return _this._pinch_end(e);
      };
    })(this));
    this.hammer.get('rotate').set({
      enable: true
    });
    this.hammer.on('rotatestart', (function(_this) {
      return function(e) {
        return _this._rotate_start(e);
      };
    })(this));
    this.hammer.on('rotate', (function(_this) {
      return function(e) {
        return _this._rotate(e);
      };
    })(this));
    this.hammer.on('rotateend', (function(_this) {
      return function(e) {
        return _this._rotate_end(e);
      };
    })(this));
    this.hit_area.addEventListener("mousemove", (function(_this) {
      return function(e) {
        return _this._mouse_move(e);
      };
    })(this));
    this.hit_area.addEventListener("mouseenter", (function(_this) {
      return function(e) {
        return _this._mouse_enter(e);
      };
    })(this));
    this.hit_area.addEventListener("mouseleave", (function(_this) {
      return function(e) {
        return _this._mouse_exit(e);
      };
    })(this));
    this.hit_area.addEventListener("wheel", (function(_this) {
      return function(e) {
        return _this._mouse_wheel(e);
      };
    })(this));
    document.addEventListener("keydown", (function(_this) {
      return function(e) {
        return _this._key_down(e);
      };
    })(this));
    return document.addEventListener("keyup", (function(_this) {
      return function(e) {
        return _this._key_up(e);
      };
    })(this));
  };

  UIEvents.prototype.register_tool = function(tool_view) {
    var et, id, type;
    et = tool_view.model.event_type;
    id = tool_view.model.id;
    type = tool_view.model.type;
    if (et == null) {
      logger.debug("Button tool: " + type);
      return;
    }
    if (et === 'pan' || et === 'pinch' || et === 'rotate') {
      logger.debug("Registering tool: " + type + " for event '" + et + "'");
      if (tool_view["_" + et + "_start"] != null) {
        tool_view.listenTo(this, et + ":start:" + id, tool_view["_" + et + "_start"]);
      }
      if (tool_view["_" + et] != null) {
        tool_view.listenTo(this, et + ":" + id, tool_view["_" + et]);
      }
      if (tool_view["_" + et + "_end"] != null) {
        tool_view.listenTo(this, et + ":end:" + id, tool_view["_" + et + "_end"]);
      }
    } else if (et === "move") {
      logger.debug("Registering tool: " + type + " for event '" + et + "'");
      if (tool_view._move_enter != null) {
        tool_view.listenTo(this, "move:enter", tool_view._move_enter);
      }
      tool_view.listenTo(this, "move", tool_view["_move"]);
      if (tool_view._move_exit != null) {
        tool_view.listenTo(this, "move:exit", tool_view._move_exit);
      }
    } else {
      logger.debug("Registering tool: " + type + " for event '" + et + "'");
      tool_view.listenTo(this, et + ":" + id, tool_view["_" + et]);
    }
    if (tool_view._keydown != null) {
      logger.debug("Registering tool: " + type + " for event 'keydown'");
      tool_view.listenTo(this, "keydown", tool_view._keydown);
    }
    if (tool_view._keyup != null) {
      logger.debug("Registering tool: " + type + " for event 'keyup'");
      tool_view.listenTo(this, "keyup", tool_view._keyup);
    }
    if (tool_view._doubletap != null) {
      logger.debug("Registering tool: " + type + " for event 'doubletap'");
      tool_view.listenTo(this, "doubletap", tool_view._doubletap);
    }
    if ('ontouchstart' in window || navigator.maxTouchPoints > 0) {
      if (et === 'pinch') {
        logger.debug("Registering scroll on touch screen");
        return tool_view.listenTo(this, "scroll:" + id, tool_view["_scroll"]);
      }
    }
  };

  UIEvents.prototype._hit_test_renderers = function(sx, sy) {
    var i, ref, ref1, view;
    ref = this.plot_view.get_renderer_views();
    for (i = ref.length - 1; i >= 0; i += -1) {
      view = ref[i];
      if (((ref1 = view.model.level) === 'annotation' || ref1 === 'overlay') && (view.bbox != null)) {
        if (view.bbox().contains(sx, sy)) {
          return view;
        }
      }
    }
    return null;
  };

  UIEvents.prototype._hit_test_frame = function(sx, sy) {
    var canvas, vx, vy;
    canvas = this.plot_view.canvas;
    vx = canvas.sx_to_vx(sx);
    vy = canvas.sy_to_vy(sy);
    return this.plot_view.frame.contains(vx, vy);
  };

  UIEvents.prototype._trigger = function(event_type, e) {
    var active_gesture, base, base_type, cursor, has_active_inspectors, view;
    base_type = event_type.split(":")[0];
    view = this._hit_test_renderers(e.bokeh.sx, e.bokeh.sy);
    switch (base_type) {
      case "move":
        has_active_inspectors = any(this.toolbar.inspectors, function(t) {
          return t.active;
        });
        cursor = "default";
        if (view != null) {
          if (view.model.cursor != null) {
            cursor = view.model.cursor();
          }
          if (has_active_inspectors) {
            event_type = "move:exit";
          }
        } else if (this._hit_test_frame(e.bokeh.sx, e.bokeh.sy)) {
          if (has_active_inspectors) {
            cursor = "crosshair";
          }
        }
        this.plot_view.set_cursor(cursor);
        return this.trigger(event_type, e);
      case "tap":
        if (view != null) {
          if (typeof view.on_hit === "function") {
            view.on_hit(e.bokeh.sx, e.bokeh.sy);
          }
        }
        active_gesture = this.toolbar.gestures[base_type].active;
        if (active_gesture != null) {
          return this.trigger(event_type + ":" + active_gesture.id, e);
        }
        break;
      case "scroll":
        base = 'ontouchstart' in window || navigator.maxTouchPoints > 0 ? "pinch" : "scroll";
        active_gesture = this.toolbar.gestures[base].active;
        if (active_gesture != null) {
          e.preventDefault();
          e.stopPropagation();
          return this.trigger(event_type + ":" + active_gesture.id, e);
        }
        break;
      default:
        active_gesture = this.toolbar.gestures[base_type].active;
        if (active_gesture != null) {
          return this.trigger(event_type + ":" + active_gesture.id, e);
        }
    }
  };

  UIEvents.prototype._bokify_hammer = function(e, extras) {
    var event_cls, left, ref, top, x, y;
    if (extras == null) {
      extras = {};
    }
    if (e.pointerType === 'mouse') {
      x = e.srcEvent.pageX;
      y = e.srcEvent.pageY;
    } else {
      x = e.pointers[0].pageX;
      y = e.pointers[0].pageY;
    }
    ref = offset(e.target), left = ref.left, top = ref.top;
    e.bokeh = {
      sx: x - left,
      sy: y - top
    };
    e.bokeh = extend(e.bokeh, extras);
    event_cls = BokehEvent.event_class(e);
    if (event_cls != null) {
      return this.plot.trigger_event(event_cls.from_event(e));
    } else {
      return logger.debug('Unhandled event of type ' + e.type);
    }
  };

  UIEvents.prototype._bokify_point_event = function(e, extras) {
    var event_cls, left, ref, top;
    if (extras == null) {
      extras = {};
    }
    ref = offset(e.currentTarget), left = ref.left, top = ref.top;
    e.bokeh = {
      sx: e.pageX - left,
      sy: e.pageY - top
    };
    e.bokeh = extend(e.bokeh, extras);
    event_cls = BokehEvent.event_class(e);
    if (event_cls != null) {
      return this.plot.trigger_event(event_cls.from_event(e));
    } else {
      return logger.debug('Unhandled event of type ' + e.type);
    }
  };

  UIEvents.prototype._tap = function(e) {
    this._bokify_hammer(e);
    return this._trigger('tap', e);
  };

  UIEvents.prototype._doubletap = function(e) {
    this._bokify_hammer(e);
    return this.trigger('doubletap', e);
  };

  UIEvents.prototype._press = function(e) {
    this._bokify_hammer(e);
    return this._trigger('press', e);
  };

  UIEvents.prototype._pan_start = function(e) {
    this._bokify_hammer(e);
    e.bokeh.sx -= e.deltaX;
    e.bokeh.sy -= e.deltaY;
    return this._trigger('pan:start', e);
  };

  UIEvents.prototype._pan = function(e) {
    this._bokify_hammer(e);
    return this._trigger('pan', e);
  };

  UIEvents.prototype._pan_end = function(e) {
    this._bokify_hammer(e);
    return this._trigger('pan:end', e);
  };

  UIEvents.prototype._pinch_start = function(e) {
    this._bokify_hammer(e);
    return this._trigger('pinch:start', e);
  };

  UIEvents.prototype._pinch = function(e) {
    this._bokify_hammer(e);
    return this._trigger('pinch', e);
  };

  UIEvents.prototype._pinch_end = function(e) {
    this._bokify_hammer(e);
    return this._trigger('pinch:end', e);
  };

  UIEvents.prototype._rotate_start = function(e) {
    this._bokify_hammer(e);
    return this._trigger('rotate:start', e);
  };

  UIEvents.prototype._rotate = function(e) {
    this._bokify_hammer(e);
    return this._trigger('rotate', e);
  };

  UIEvents.prototype._rotate_end = function(e) {
    this._bokify_hammer(e);
    return this._trigger('rotate:end', e);
  };

  UIEvents.prototype._mouse_enter = function(e) {
    this._bokify_point_event(e);
    return this._trigger('move:enter', e);
  };

  UIEvents.prototype._mouse_move = function(e) {
    this._bokify_point_event(e);
    return this._trigger('move', e);
  };

  UIEvents.prototype._mouse_exit = function(e) {
    this._bokify_point_event(e);
    return this._trigger('move:exit', e);
  };

  UIEvents.prototype._mouse_wheel = function(e) {
    this._bokify_point_event(e, {
      delta: getDeltaY(e)
    });
    return this._trigger('scroll', e);
  };

  UIEvents.prototype._key_down = function(e) {
    return this.trigger('keydown', e);
  };

  UIEvents.prototype._key_up = function(e) {
    return this.trigger('keyup', e);
  };

  return UIEvents;

})();
