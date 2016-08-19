// Generated by CoffeeScript 1.10.0
var bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; };

(function(window, $, templates) {
  var FETCH_INTERVAL, fetch, locale, provider, registry, stateUrl, update;
  FETCH_INTERVAL = 3000;
  locale = (window.location.pathname.split('/'))[1];
  stateUrl = "/" + locale + "/state/";
  window.state = {};
  registry = {};
  window.state.provider = function(name) {
    var config, instance;
    instance = registry[name];
    if (instance == null) {
      instance = new provider(name);
      registry[name] = instance;
      config = {
        get: instance.get
      };
      Object.defineProperty(window.state, name, config);
    }
    return instance;
  };
  provider = (function() {
    function provider(name) {
      this.postprocessor = bind(this.postprocessor, this);
      this.onchange = bind(this.onchange, this);
      this.get = bind(this.get, this);
      this.set = bind(this.set, this);
      this.invokeCallbacks = bind(this.invokeCallbacks, this);
      this.name = name;
      this.data = void 0;
      this.callbacks = [];
    }

    provider.prototype.invokeCallbacks = function() {
      var fn, i, len, ref, results;
      ref = this.callbacks;
      results = [];
      for (i = 0, len = ref.length; i < len; i++) {
        fn = ref[i];
        results.push(fn(this));
      }
      return results;
    };

    provider.prototype.set = function(data, stealth) {
      if (stealth == null) {
        stealth = false;
      }
      this.data = data;
      if (!stealth) {
        return this.invokeCallbacks();
      }
    };

    provider.prototype.get = function() {
      if (window.state.__trapper__ != null) {
        window.state.__trapper__(this.name);
      }
      return this.data;
    };

    provider.prototype.onchange = function(callback) {
      if ($.inArray(callback, this.callbacks) === -1) {
        return this.callbacks.push(callback);
      }
    };

    provider.prototype.postprocessor = function(fn, target) {
      var processor;
      if (target == null) {
        target = null;
      }
      processor = function(provider) {
        var copy, data, processed;
        data = provider.get();
        processed = fn(data);
        if (target === null) {
          provider.set(processed, true);
          return;
        }
        if (typeof target === 'string') {
          data[target] = processed;
          return;
        }
        copy = target.slice();
        while (copy.length > 1) {
          data = data[copy.shift()];
        }
        data[copy.shift()] = processed;
      };
      return this.onchange(processor);
    };

    return provider;

  })();
  update = function(data) {
    var instance, key, results, value;
    results = [];
    for (key in data) {
      value = data[key];
      instance = window.state.provider(key);
      results.push(instance.set(value));
    }
    return results;
  };
  fetch = function() {
    var res;
    res = $.get(stateUrl);
    res.done(function(data) {
      update(data);
      return setTimeout(fetch, FETCH_INTERVAL);
    });
    return res.fail(function() {
      console.log('State synchronization failed.');
      return setTimeout(fetch, FETCH_INTERVAL);
    });
  };
  return setTimeout(fetch, FETCH_INTERVAL);
})(this, this.jQuery, this.templates);
