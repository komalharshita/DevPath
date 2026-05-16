// storage.js — local persistence for saved projects and recent views.
// No server storage; data stays in the browser.

var DevPathStore = (function () {
  var SAVED_KEY = "devpath_saved_v1";
  var RECENT_KEY = "devpath_recent_v1";
  var MAX_RECENT = 5;

  function read(key) {
    try {
      var raw = localStorage.getItem(key);
      return raw ? JSON.parse(raw) : [];
    } catch (e) {
      return [];
    }
  }

  function write(key, list) {
    try {
      localStorage.setItem(key, JSON.stringify(list));
    } catch (e) {
      /* quota or private mode — fail quietly */
    }
  }

  function normalizeEntry(id, title, level) {
    return {
      id: parseInt(id, 10),
      title: title || "Project",
      level: level || ""
    };
  }

  return {
    getSaved: function () {
      return read(SAVED_KEY);
    },

    isSaved: function (id) {
      var numId = parseInt(id, 10);
      return read(SAVED_KEY).some(function (item) {
        return item.id === numId;
      });
    },

    toggleSaved: function (id, title, level) {
      var numId = parseInt(id, 10);
      var list = read(SAVED_KEY);
      var idx = list.findIndex(function (item) { return item.id === numId; });

      if (idx >= 0) {
        list.splice(idx, 1);
        write(SAVED_KEY, list);
        return false;
      }

      list.unshift(normalizeEntry(id, title, level));
      write(SAVED_KEY, list);
      return true;
    },

    removeSaved: function (id) {
      var numId = parseInt(id, 10);
      var list = read(SAVED_KEY).filter(function (item) {
        return item.id !== numId;
      });
      write(SAVED_KEY, list);
    },

    getRecent: function () {
      return read(RECENT_KEY);
    },

    addRecent: function (id, title, level) {
      var numId = parseInt(id, 10);
      var entry = normalizeEntry(id, title, level);
      var list = read(RECENT_KEY).filter(function (item) {
        return item.id !== numId;
      });
      list.unshift(entry);
      if (list.length > MAX_RECENT) {
        list = list.slice(0, MAX_RECENT);
      }
      write(RECENT_KEY, list);
    }
  };
})();
