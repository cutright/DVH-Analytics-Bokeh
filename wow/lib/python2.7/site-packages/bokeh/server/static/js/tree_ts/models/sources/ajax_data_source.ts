var bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; },
  extend = function(child, parent) { for (var key in parent) { if (hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor(); child.__super__ = parent.prototype; return child; },
  hasProp = {}.hasOwnProperty;

import {
  RemoteDataSource
} from "./remote_data_source";

import {
  logger
} from "core/logging";

import * as p from "core/properties";

export var AjaxDataSource = (function(superClass) {
  extend(AjaxDataSource, superClass);

  function AjaxDataSource() {
    this.get_data = bind(this.get_data, this);
    this.setup = bind(this.setup, this);
    this.destroy = bind(this.destroy, this);
    return AjaxDataSource.__super__.constructor.apply(this, arguments);
  }

  AjaxDataSource.prototype.type = 'AjaxDataSource';

  AjaxDataSource.define({
    mode: [p.String, 'replace'],
    content_type: [p.String, 'application/json'],
    http_headers: [p.Any, {}],
    max_size: [p.Number],
    method: [p.String, 'POST'],
    if_modified: [p.Bool, false]
  });

  AjaxDataSource.prototype.destroy = function() {
    if (this.interval != null) {
      return clearInterval(this.interval);
    }
  };

  AjaxDataSource.prototype.setup = function(plot_view, glyph) {
    this.pv = plot_view;
    this.get_data(this.mode);
    if (this.polling_interval) {
      return this.interval = setInterval(this.get_data, this.polling_interval, this.mode, this.max_size, this.if_modified);
    }
  };

  AjaxDataSource.prototype.get_data = function(mode, max_size, if_modified) {
    var name, ref, value, xhr;
    if (max_size == null) {
      max_size = 0;
    }
    if (if_modified == null) {
      if_modified = false;
    }
    xhr = new XMLHttpRequest();
    xhr.open(this.method, this.data_url, true);
    xhr.withCredentials = false;
    xhr.setRequestHeader("Content-Type", this.content_type);
    ref = this.http_headers;
    for (name in ref) {
      value = ref[name];
      xhr.setRequestHeader(name, value);
    }
    xhr.addEventListener("load", (function(_this) {
      return function() {
        var column, data, i, len, original_data, ref1;
        if (xhr.status === 200) {
          data = JSON.parse(xhr.responseText);
          switch (mode) {
            case 'replace':
              return _this.data = data;
            case 'append':
              original_data = _this.data;
              ref1 = _this.columns();
              for (i = 0, len = ref1.length; i < len; i++) {
                column = ref1[i];
                data[column] = original_data[column].concat(data[column]).slice(-max_size);
              }
              return _this.data = data;
          }
        }
      };
    })(this));
    xhr.addEventListener("error", (function(_this) {
      return function() {
        return logger.error("Failed to fetch JSON from " + _this.data_url + " with code " + xhr.status);
      };
    })(this));
    xhr.send();
    return null;
  };

  return AjaxDataSource;

})(RemoteDataSource);
