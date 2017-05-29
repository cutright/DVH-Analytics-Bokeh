import {
  difference
} from "./util/array";

import {
  extend
} from "./util/object";

export var build_views = function(view_storage, view_models, options, view_types) {
  var cls, created_views, i, i_model, j, key, len, len1, model, newmodels, ref, to_remove, view, view_options;
  if (view_types == null) {
    view_types = [];
  }
  created_views = [];
  newmodels = view_models.filter(function(x) {
    return view_storage[x.id] == null;
  });
  for (i_model = i = 0, len = newmodels.length; i < len; i_model = ++i) {
    model = newmodels[i_model];
    cls = (ref = view_types[i_model]) != null ? ref : model.default_view;
    view_options = extend({
      model: model
    }, options);
    view_storage[model.id] = view = new cls(view_options);
    created_views.push(view);
  }
  to_remove = difference(Object.keys(view_storage), (function() {
    var j, len1, results;
    results = [];
    for (j = 0, len1 = view_models.length; j < len1; j++) {
      view = view_models[j];
      results.push(view.id);
    }
    return results;
  })());
  for (j = 0, len1 = to_remove.length; j < len1; j++) {
    key = to_remove[j];
    view_storage[key].remove();
    delete view_storage[key];
  }
  return created_views;
};
