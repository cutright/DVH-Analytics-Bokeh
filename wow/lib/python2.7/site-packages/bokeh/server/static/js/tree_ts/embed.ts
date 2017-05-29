var _create_view, _get_session, _handle_notebook_comms, _init_comms, _render_document_to_element, _sessions, _update_comms_callback, add_document_from_session, add_model_from_session, add_model_static, fill_render_item_from_script_tag;

import {
  Promise
} from "es6-promise";

import * as base from "./base";

import {
  pull_session
} from "./client";

import {
  logger,
  set_log_level
} from "./core/logging";

import {
  Document,
  RootAddedEvent,
  RootRemovedEvent,
  TitleChangedEvent
} from "./document";

import {
  div,
  link,
  style,
  replaceWith
} from "./core/dom";

import {
  delay
} from "./core/util/callback";

export var BOKEH_ROOT = "bk-root";

_handle_notebook_comms = function(msg) {
  var data;
  logger.debug("handling notebook comms");
  data = JSON.parse(msg.content.data);
  if ('events' in data && 'references' in data) {
    return this.apply_json_patch(data);
  } else if ('doc' in data) {
    return this.replace_with_json(data['doc']);
  } else {
    throw new Error("handling notebook comms message: ", msg);
  }
};

_update_comms_callback = function(target, doc, comm) {
  if (target === comm.target_name) {
    return comm.on_msg(_handle_notebook_comms.bind(doc));
  }
};

_init_comms = function(target, doc) {
  var comm_manager, e, id, promise, ref, update_comms;
  if ((typeof Jupyter !== "undefined" && Jupyter !== null) && (Jupyter.notebook.kernel != null)) {
    logger.info("Registering Jupyter comms for target " + target);
    comm_manager = Jupyter.notebook.kernel.comm_manager;
    update_comms = function(comm) {
      return _update_comms_callback(target, doc, comm);
    };
    ref = comm_manager.comms;
    for (id in ref) {
      promise = ref[id];
      promise.then(update_comms);
    }
    try {
      return comm_manager.register_target(target, function(comm, msg) {
        logger.info("Registering Jupyter comms for target " + target);
        return comm.on_msg(_handle_notebook_comms.bind(doc));
      });
    } catch (error1) {
      e = error1;
      return logger.warn("Jupyter comms failed to register. push_notebook() will not function. (exception reported: " + e + ")");
    }
  } else {
    return console.warn('Jupyter notebooks comms not available. push_notebook() will not function');
  }
};

_create_view = function(model) {
  var view;
  view = new model.default_view({
    model: model
  });
  base.index[model.id] = view;
  return view;
};

_render_document_to_element = function(element, document, use_for_title) {
  var i, len, model, ref, render_model, unrender_model, views;
  views = {};
  render_model = function(model) {
    var view;
    view = _create_view(model);
    views[model.id] = view;
    return element.appendChild(view.el);
  };
  unrender_model = function(model) {
    var view;
    if (model.id in views) {
      view = views[model.id];
      element.removeChild(view.el);
      delete views[model.id];
      return delete base.index[model.id];
    }
  };
  ref = document.roots();
  for (i = 0, len = ref.length; i < len; i++) {
    model = ref[i];
    render_model(model);
  }
  if (use_for_title) {
    window.document.title = document.title();
  }
  document.on_change(function(event) {
    if (event instanceof RootAddedEvent) {
      return render_model(event.model);
    } else if (event instanceof RootRemovedEvent) {
      return unrender_model(event.model);
    } else if (use_for_title && event instanceof TitleChangedEvent) {
      return window.document.title = event.title;
    }
  });
  return views;
};

add_model_static = function(element, model_id, doc) {
  var model, view;
  model = doc.get_model_by_id(model_id);
  if (model == null) {
    throw new Error("Model " + model_id + " was not in document " + doc);
  }
  view = _create_view(model);
  return delay(function() {
    return replaceWith(element, view.el);
  });
};

export var add_document_static = function(element, doc, use_for_title) {
  return delay(function() {
    return _render_document_to_element(element, doc, use_for_title);
  });
};

export var add_document_standalone = function(document, element, use_for_title) {
  if (use_for_title == null) {
    use_for_title = false;
  }
  return _render_document_to_element(element, document, use_for_title);
};

_sessions = {};

_get_session = function(websocket_url, session_id, args_string) {
  var subsessions;
  if ((websocket_url == null) || websocket_url === null) {
    throw new Error("Missing websocket_url");
  }
  if (!(websocket_url in _sessions)) {
    _sessions[websocket_url] = {};
  }
  subsessions = _sessions[websocket_url];
  if (!(session_id in subsessions)) {
    subsessions[session_id] = pull_session(websocket_url, session_id, args_string);
  }
  return subsessions[session_id];
};

add_document_from_session = function(element, websocket_url, session_id, use_for_title) {
  var args_string, promise;
  args_string = window.location.search.substr(1);
  promise = _get_session(websocket_url, session_id, args_string);
  return promise.then(function(session) {
    return _render_document_to_element(element, session.document, use_for_title);
  }, function(error) {
    logger.error("Failed to load Bokeh session " + session_id + ": " + error);
    throw error;
  });
};

add_model_from_session = function(element, websocket_url, model_id, session_id) {
  var args_string, promise;
  args_string = window.location.search.substr(1);
  promise = _get_session(websocket_url, session_id, args_string);
  return promise.then(function(session) {
    var model, view;
    model = session.document.get_model_by_id(model_id);
    if (model == null) {
      throw new Error("Did not find model " + model_id + " in session");
    }
    view = _create_view(model);
    return replaceWith(element, view.el);
  }, function(error) {
    logger.error("Failed to load Bokeh session " + session_id + ": " + error);
    throw error;
  });
};

export var inject_css = function(url) {
  var element;
  element = link({
    href: url,
    rel: "stylesheet",
    type: "text/css"
  });
  return document.body.appendChild(element);
};

export var inject_raw_css = function(css) {
  var element;
  element = style({}, css);
  return document.body.appendChild(element);
};

fill_render_item_from_script_tag = function(script, item) {
  var info;
  info = script.dataset;
  if ((info.bokehLogLevel != null) && info.bokehLogLevel.length > 0) {
    set_log_level(info.bokehLogLevel);
  }
  if ((info.bokehDocId != null) && info.bokehDocId.length > 0) {
    item['docid'] = info.bokehDocId;
  }
  if ((info.bokehModelId != null) && info.bokehModelId.length > 0) {
    item['modelid'] = info.bokehModelId;
  }
  if ((info.bokehSessionId != null) && info.bokehSessionId.length > 0) {
    item['sessionid'] = info.bokehSessionId;
  }
  return logger.info("Will inject Bokeh script tag with params " + (JSON.stringify(item)));
};

export var embed_items = function(docs_json, render_items, app_path, absolute_url) {
  var child, container, docid, docs, elem, element_id, i, item, len, loc, promise, protocol, results, use_for_title, websocket_url;
  protocol = 'ws:';
  if (window.location.protocol === 'https:') {
    protocol = 'wss:';
  }
  if (absolute_url != null) {
    loc = new URL(absolute_url);
  } else {
    loc = window.location;
  }
  if (app_path != null) {
    if (app_path === "/") {
      app_path = "";
    }
  } else {
    app_path = loc.pathname.replace(/\/+$/, '');
  }
  websocket_url = protocol + '//' + loc.host + app_path + '/ws';
  logger.debug("embed: computed ws url: " + websocket_url);
  docs = {};
  for (docid in docs_json) {
    docs[docid] = Document.from_json(docs_json[docid]);
  }
  results = [];
  for (i = 0, len = render_items.length; i < len; i++) {
    item = render_items[i];
    if (item.notebook_comms_target != null) {
      _init_comms(item.notebook_comms_target, docs[docid]);
    }
    element_id = item['elementid'];
    elem = document.getElementById(element_id);
    if (elem == null) {
      throw new Error("Error rendering Bokeh model: could not find tag with id: " + element_id);
    }
    if (!document.body.contains(elem)) {
      throw new Error("Error rendering Bokeh model: element with id '" + element_id + "' must be under <body>");
    }
    if (elem.tagName === "SCRIPT") {
      fill_render_item_from_script_tag(elem, item);
      container = div({
        "class": BOKEH_ROOT
      });
      replaceWith(elem, container);
      child = div();
      container.appendChild(child);
      elem = child;
    }
    use_for_title = (item.use_for_title != null) && item.use_for_title;
    promise = null;
    if (item.modelid != null) {
      if (item.docid != null) {
        add_model_static(elem, item.modelid, docs[item.docid]);
      } else if (item.sessionid != null) {
        promise = add_model_from_session(elem, websocket_url, item.modelid, item.sessionid);
      } else {
        throw new Error("Error rendering Bokeh model " + item['modelid'] + " to element " + element_id + ": no document ID or session ID specified");
      }
    } else {
      if (item.docid != null) {
        add_document_static(elem, docs[item.docid], use_for_title);
      } else if (item.sessionid != null) {
        promise = add_document_from_session(elem, websocket_url, item.sessionid, use_for_title);
      } else {
        throw new Error("Error rendering Bokeh document to element " + element_id + ": no document ID or session ID specified");
      }
    }
    if (promise !== null) {
      results.push(promise.then(function(value) {
        return console.log("Bokeh items were rendered successfully");
      }, function(error) {
        return console.log("Error rendering Bokeh items ", error);
      }));
    } else {
      results.push(void 0);
    }
  }
  return results;
};
