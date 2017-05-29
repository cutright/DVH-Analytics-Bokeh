"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var load_google_api, bind = function (fn, me) { return function () { return fn.apply(me, arguments); }; }, extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var proj4_1 = require("core/util/proj4");
var plot_canvas_1 = require("./plot_canvas");
load_google_api = function (callback, api_key) {
    var ref, script;
    if (((ref = window.google) != null ? ref.maps : void 0) == null) {
        window._bokeh_gmap_callback = function () {
            return callback();
        };
        script = document.createElement('script');
        script.type = 'text/javascript';
        script.src = "https://maps.googleapis.com/maps/api/js?key=" + api_key + "&callback=_bokeh_gmap_callback";
        return document.body.appendChild(script);
    }
};
exports.GMapPlotCanvasView = (function (superClass) {
    extend(GMapPlotCanvasView, superClass);
    function GMapPlotCanvasView() {
        this._set_bokeh_ranges = bind(this._set_bokeh_ranges, this);
        this._get_projected_bounds = bind(this._get_projected_bounds, this);
        this._get_latlon_bounds = bind(this._get_latlon_bounds, this);
        return GMapPlotCanvasView.__super__.constructor.apply(this, arguments);
    }
    GMapPlotCanvasView.prototype.initialize = function (options) {
        var mo;
        GMapPlotCanvasView.__super__.initialize.call(this, options);
        this.zoom_count = 0;
        mo = this.model.plot.map_options;
        this.initial_zoom = mo.zoom;
        this.initial_lat = mo.lat;
        this.initial_lng = mo.lng;
        this.canvas_view.map_div.style.position = "absolute";
        return load_google_api(this.request_render, this.model.plot.api_key);
    };
    GMapPlotCanvasView.prototype.update_range = function (range_info) {
        var mo, new_map_zoom, old_map_zoom, proj_xend, proj_xstart, proj_yend, proj_ystart, ref, zoom_change;
        if (range_info == null) {
            mo = this.model.plot.map_options;
            this.map.setCenter({
                lat: this.initial_lat,
                lng: this.initial_lng
            });
            this.map.setOptions({
                zoom: this.initial_zoom
            });
            GMapPlotCanvasView.__super__.update_range.call(this, null);
        }
        else if ((range_info.sdx != null) || (range_info.sdy != null)) {
            this.map.panBy(range_info.sdx, range_info.sdy);
            GMapPlotCanvasView.__super__.update_range.call(this, range_info);
        }
        else if (range_info.factor != null) {
            this.pause();
            if (this.zoom_count !== 10) {
                this.zoom_count += 1;
                return;
            }
            this.zoom_count = 0;
            GMapPlotCanvasView.__super__.update_range.call(this, range_info);
            if (range_info.factor < 0) {
                zoom_change = -1;
            }
            else {
                zoom_change = 1;
            }
            old_map_zoom = this.map.getZoom();
            new_map_zoom = old_map_zoom + zoom_change;
            if (new_map_zoom >= 2) {
                this.map.setZoom(new_map_zoom);
                ref = this._get_projected_bounds(), proj_xstart = ref[0], proj_xend = ref[1], proj_ystart = ref[2], proj_yend = ref[3];
                if ((proj_xend - proj_xstart) < 0) {
                    this.map.setZoom(old_map_zoom);
                }
            }
            this.unpause();
        }
        return this._set_bokeh_ranges();
    };
    GMapPlotCanvasView.prototype._build_map = function () {
        var map_options, maps, mo;
        maps = window.google.maps;
        this.map_types = {
            satellite: maps.MapTypeId.SATELLITE,
            terrain: maps.MapTypeId.TERRAIN,
            roadmap: maps.MapTypeId.ROADMAP,
            hybrid: maps.MapTypeId.HYBRID
        };
        mo = this.model.plot.map_options;
        map_options = {
            center: new maps.LatLng(mo.lat, mo.lng),
            zoom: mo.zoom,
            disableDefaultUI: true,
            mapTypeId: this.map_types[mo.map_type],
            scaleControl: mo.scale_control
        };
        if (mo.styles != null) {
            map_options.styles = JSON.parse(mo.styles);
        }
        this.map = new maps.Map(this.canvas_view.map_div, map_options);
        maps.event.addListenerOnce(this.map, 'idle', this._set_bokeh_ranges);
        this.listenTo(this.model.plot, 'change:map_options', (function (_this) {
            return function () {
                return _this._update_options();
            };
        })(this));
        this.listenTo(this.model.plot.map_options, 'change:styles', (function (_this) {
            return function () {
                return _this._update_styles();
            };
        })(this));
        this.listenTo(this.model.plot.map_options, 'change:lat', (function (_this) {
            return function () {
                return _this._update_center('lat');
            };
        })(this));
        this.listenTo(this.model.plot.map_options, 'change:lng', (function (_this) {
            return function () {
                return _this._update_center('lng');
            };
        })(this));
        this.listenTo(this.model.plot.map_options, 'change:zoom', (function (_this) {
            return function () {
                return _this._update_zoom();
            };
        })(this));
        this.listenTo(this.model.plot.map_options, 'change:map_type', (function (_this) {
            return function () {
                return _this._update_map_type();
            };
        })(this));
        return this.listenTo(this.model.plot.map_options, 'change:scale_control', (function (_this) {
            return function () {
                return _this._update_scale_control();
            };
        })(this));
    };
    GMapPlotCanvasView.prototype._get_latlon_bounds = function () {
        var bottom_left, bounds, top_right, xend, xstart, yend, ystart;
        bounds = this.map.getBounds();
        top_right = bounds.getNorthEast();
        bottom_left = bounds.getSouthWest();
        xstart = bottom_left.lng();
        xend = top_right.lng();
        ystart = bottom_left.lat();
        yend = top_right.lat();
        return [xstart, xend, ystart, yend];
    };
    GMapPlotCanvasView.prototype._get_projected_bounds = function () {
        var proj_xend, proj_xstart, proj_yend, proj_ystart, ref, ref1, ref2, xend, xstart, yend, ystart;
        ref = this._get_latlon_bounds(), xstart = ref[0], xend = ref[1], ystart = ref[2], yend = ref[3];
        ref1 = proj4_1.proj4(proj4_1.mercator, [xstart, ystart]), proj_xstart = ref1[0], proj_ystart = ref1[1];
        ref2 = proj4_1.proj4(proj4_1.mercator, [xend, yend]), proj_xend = ref2[0], proj_yend = ref2[1];
        return [proj_xstart, proj_xend, proj_ystart, proj_yend];
    };
    GMapPlotCanvasView.prototype._set_bokeh_ranges = function () {
        var proj_xend, proj_xstart, proj_yend, proj_ystart, ref;
        ref = this._get_projected_bounds(), proj_xstart = ref[0], proj_xend = ref[1], proj_ystart = ref[2], proj_yend = ref[3];
        this.x_range.setv({
            start: proj_xstart,
            end: proj_xend
        });
        return this.y_range.setv({
            start: proj_ystart,
            end: proj_yend
        });
    };
    GMapPlotCanvasView.prototype._update_center = function (fld) {
        var c;
        c = this.map.getCenter().toJSON();
        c[fld] = this.model.plot.map_options[fld];
        this.map.setCenter(c);
        return this._set_bokeh_ranges();
    };
    GMapPlotCanvasView.prototype._update_map_type = function () {
        var maps;
        maps = window.google.maps;
        return this.map.setOptions({
            mapTypeId: this.map_types[this.model.plot.map_options.map_type]
        });
    };
    GMapPlotCanvasView.prototype._update_scale_control = function () {
        var maps;
        maps = window.google.maps;
        return this.map.setOptions({
            scaleControl: this.model.plot.map_options.scale_control
        });
    };
    GMapPlotCanvasView.prototype._update_options = function () {
        this._update_styles();
        this._update_center('lat');
        this._update_center('lng');
        this._update_zoom();
        return this._update_map_type();
    };
    GMapPlotCanvasView.prototype._update_styles = function () {
        return this.map.setOptions({
            styles: JSON.parse(this.model.plot.map_options.styles)
        });
    };
    GMapPlotCanvasView.prototype._update_zoom = function () {
        this.map.setOptions({
            zoom: this.model.plot.map_options.zoom
        });
        return this._set_bokeh_ranges();
    };
    GMapPlotCanvasView.prototype._map_hook = function (ctx, frame_box) {
        var height, left, top, width;
        left = frame_box[0], top = frame_box[1], width = frame_box[2], height = frame_box[3];
        this.canvas_view.map_div.style.top = top + "px";
        this.canvas_view.map_div.style.left = left + "px";
        this.canvas_view.map_div.style.width = width + "px";
        this.canvas_view.map_div.style.height = height + "px";
        if (this.map == null) {
            return this._build_map();
        }
    };
    GMapPlotCanvasView.prototype._paint_empty = function (ctx, frame_box) {
        var ih, iw, left, oh, ow, top;
        ow = this.canvas.width;
        oh = this.canvas.height;
        left = frame_box[0], top = frame_box[1], iw = frame_box[2], ih = frame_box[3];
        ctx.clearRect(0, 0, ow, oh);
        ctx.beginPath();
        ctx.moveTo(0, 0);
        ctx.lineTo(0, oh);
        ctx.lineTo(ow, oh);
        ctx.lineTo(ow, 0);
        ctx.lineTo(0, 0);
        ctx.moveTo(left, top);
        ctx.lineTo(left + iw, top);
        ctx.lineTo(left + iw, top + ih);
        ctx.lineTo(left, top + ih);
        ctx.lineTo(left, top);
        ctx.closePath();
        ctx.fillStyle = this.model.plot.border_fill_color;
        return ctx.fill();
    };
    return GMapPlotCanvasView;
})(plot_canvas_1.PlotCanvasView);
exports.GMapPlotCanvas = (function (superClass) {
    extend(GMapPlotCanvas, superClass);
    function GMapPlotCanvas() {
        return GMapPlotCanvas.__super__.constructor.apply(this, arguments);
    }
    GMapPlotCanvas.prototype.type = 'GMapPlotCanvas';
    GMapPlotCanvas.prototype.default_view = exports.GMapPlotCanvasView;
    GMapPlotCanvas.prototype.initialize = function (attrs, options) {
        this.use_map = true;
        return GMapPlotCanvas.__super__.initialize.call(this, attrs, options);
    };
    return GMapPlotCanvas;
})(plot_canvas_1.PlotCanvas);
