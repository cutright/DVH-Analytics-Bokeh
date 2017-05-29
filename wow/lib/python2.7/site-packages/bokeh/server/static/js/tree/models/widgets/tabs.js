"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var extend = function (child, parent) { for (var key in parent) {
    if (hasProp.call(parent, key))
        child[key] = parent[key];
} function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; }, hasProp = {}.hasOwnProperty;
var $ = require("jquery");
require("bootstrap/tab");
var p = require("core/properties");
var array_1 = require("core/util/array");
var tabs_template_1 = require("./tabs_template");
var widget_1 = require("./widget");
exports.TabsView = (function (superClass) {
    extend(TabsView, superClass);
    function TabsView() {
        return TabsView.__super__.constructor.apply(this, arguments);
    }
    TabsView.prototype.render = function () {
        var $panels, _key, active, child, children, html, i, len, panel, ref, ref1, ref2, ref3, tabs, that;
        TabsView.__super__.render.call(this);
        ref = this.child_views;
        for (_key in ref) {
            if (!hasProp.call(ref, _key))
                continue;
            child = ref[_key];
            if ((ref1 = child.el.parentNode) != null) {
                ref1.removeChild(child.el);
            }
        }
        this.$el.empty();
        tabs = this.model.tabs;
        active = this.model.active;
        children = this.model.children;
        html = $(tabs_template_1.default({
            tabs: tabs,
            active_tab_id: tabs[active].id
        }));
        that = this;
        html.find(".bk-bs-nav a").click(function (event) {
            var panelId, panelIdx, ref2;
            event.preventDefault();
            $(this).tab('show');
            panelId = $(this).attr('href').replace('#tab-', '');
            tabs = that.model.tabs;
            panelIdx = array_1.findIndex(tabs, function (panel) {
                return panel.id === panelId;
            });
            that.model.active = panelIdx;
            return (ref2 = that.model.callback) != null ? ref2.execute(that.model) : void 0;
        });
        $panels = html.find(".bk-bs-tab-pane");
        ref2 = array_1.zip(children, $panels);
        for (i = 0, len = ref2.length; i < len; i++) {
            ref3 = ref2[i], child = ref3[0], panel = ref3[1];
            $(panel).html(this.child_views[child.id].el);
        }
        this.$el.append(html);
        return this;
    };
    return TabsView;
})(widget_1.WidgetView);
exports.Tabs = (function (superClass) {
    extend(Tabs, superClass);
    function Tabs() {
        return Tabs.__super__.constructor.apply(this, arguments);
    }
    Tabs.prototype.type = "Tabs";
    Tabs.prototype.default_view = exports.TabsView;
    Tabs.define({
        tabs: [p.Array, []],
        active: [p.Number, 0],
        callback: [p.Instance]
    });
    Tabs.getters({
        children: function () {
            var i, len, ref, results, tab;
            ref = this.tabs;
            results = [];
            for (i = 0, len = ref.length; i < len; i++) {
                tab = ref[i];
                results.push(tab.child);
            }
            return results;
        }
    });
    Tabs.prototype.get_layoutable_children = function () {
        return this.children;
    };
    Tabs.prototype.get_edit_variables = function () {
        var child, edit_variables, i, len, ref;
        edit_variables = Tabs.__super__.get_edit_variables.call(this);
        ref = this.get_layoutable_children();
        for (i = 0, len = ref.length; i < len; i++) {
            child = ref[i];
            edit_variables = edit_variables.concat(child.get_edit_variables());
        }
        return edit_variables;
    };
    Tabs.prototype.get_constraints = function () {
        var child, constraints, i, len, ref;
        constraints = Tabs.__super__.get_constraints.call(this);
        ref = this.get_layoutable_children();
        for (i = 0, len = ref.length; i < len; i++) {
            child = ref[i];
            constraints = constraints.concat(child.get_constraints());
        }
        return constraints;
    };
    return Tabs;
})(widget_1.Widget);
