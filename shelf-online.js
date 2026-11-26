/* Game Shelf online play.
   Inside Claude, games get multiplayer from window.claude.use('room'). On the shelf that does not exist,
   so this file provides the same small "room" interface on top of a Supabase Realtime broadcast channel:
     room.presence(patch)   merge patch into my state and share it        -> Promise
     room.peers()           [{peer, kind:'viewer', isMe, sameTab, by, presence}, ...]  (includes me)
     room.onPeers(fn)       fn({peers}) whenever the list or anyone's state changes
     room.connected() / room.onConnection(fn)
     room.emit(ev, data) / room.on(ev, fn)   one-off events; fn({data, peer, isMe, sameTab})
   It also provides an anonymous 'user' (id only). 'db' is not provided, so games keep saving locally.
   No database tables are used. Include it before a game's own script:
     <script src="../shelf-online.js" data-channel="my-game"></script>                                  */
(function () {
  'use strict';
  if (window.claude && typeof window.claude.use === 'function') return;   // real Claude runtime: leave it alone

  var CFG = {
    url: 'https://fxexfdvvajpkwmwttlti.supabase.co',
    key: 'sb_publishable_PFlAlY8b0oudCapnwXR7zQ_3X4MoWjv',
    lib: 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.118.0/dist/umd/supabase.js',
    sendMs: 200,      // fastest state broadcast while something is changing (5 per second)
    beatMs: 2000,     // heartbeat when nothing changes, so late joiners see everyone
    staleMs: 6000,    // drop a peer not heard from for this long
    maxPeers: 24,
    maxBytes: 4000    // ignore oversized states from other clients
  };
  var tag = document.currentScript;
  var channelName = 'shelf:' + ((tag && tag.dataset.channel) || 'lobby').replace(/[^\w-]/g, '').slice(0, 40);

  function loadLib() {
    return new Promise(function (resolve, reject) {
      if (window.supabase && window.supabase.createClient) return resolve();
      var s = document.createElement('script');
      s.src = CFG.lib; s.async = true;
      s.onload = function () { window.supabase && window.supabase.createClient ? resolve() : reject(new Error('supabase-js missing')); };
      s.onerror = function () { reject(new Error('supabase-js failed to load')); };
      document.head.appendChild(s);
    });
  }

  // A stable anonymous id for this browser, used as the player's "user id".
  function uid() {
    var k = 'shelf-uid', v = null;
    try { v = localStorage.getItem(k); } catch (e) {}
    if (!v || !/^u[a-z0-9]{8,24}$/.test(v)) {
      v = 'u' + Math.random().toString(36).slice(2, 12) + Date.now().toString(36);
      try { localStorage.setItem(k, v); } catch (e) {}
    }
    return v;
  }

  function makeRoom() {
    return loadLib().then(function () {
      var client = window.supabase.createClient(CFG.url, CFG.key, {
        auth: { persistSession: false, autoRefreshToken: false, detectSessionInUrl: false },
        realtime: { params: { eventsPerSecond: 10 } }
      });
      var me = 'p' + Math.random().toString(36).slice(2, 10) + Date.now().toString(36), by = uid();
      var state = {}, peers = new Map(), joined = false, lastSent = '', lastSendAt = 0, lastEmitAt = 0;
      var peerCbs = [], connCbs = [], evCbs = {}, peersDirty = true;
      var ch = client.channel(channelName, { config: { broadcast: { self: false, ack: false } } });
      var okId = function (v) { return typeof v === 'string' && v.length > 0 && v.length <= 40; };
      var small = function (v) { try { return JSON.stringify(v).length <= CFG.maxBytes; } catch (e) { return false; } };
      var call = function (fn, arg) { try { fn(arg); } catch (e) {} };

      ch.on('broadcast', { event: 's' }, function (msg) {
        var p = msg && msg.payload;
        if (!p || !okId(p.id) || p.id === me || !p.s || typeof p.s !== 'object' || !small(p.s)) return;
        if (!peers.has(p.id) && peers.size >= CFG.maxPeers) return;
        peers.set(p.id, { s: p.s, by: okId(p.by) ? p.by : '', t: Date.now() });
        peersDirty = true;
      });
      ch.on('broadcast', { event: 'bye' }, function (msg) {
        var p = msg && msg.payload; if (p && okId(p.id) && peers.delete(p.id)) peersDirty = true;
      });
      ch.on('broadcast', { event: 'e' }, function (msg) {          // one-off events, e.g. emotes
        var p = msg && msg.payload;
        if (!p || !okId(p.id) || p.id === me || !okId(p.ev) || !small(p.d)) return;
        (evCbs[p.ev] || []).forEach(function (fn) { call(fn, { data: p.d, peer: p.id, isMe: false, sameTab: false }); });
      });
      ch.subscribe(function (status) {
        var was = joined; joined = status === 'SUBSCRIBED';
        if (joined) lastSent = '';
        if (was !== joined) connCbs.forEach(function (fn) { call(fn, joined); });
      });

      function send(event, payload) { try { ch.send({ type: 'broadcast', event: event, payload: payload }); } catch (e) {} }
      function list() {
        var now = Date.now(), out = [{ peer: me, kind: 'viewer', isMe: true, sameTab: true, by: by, presence: state }];
        peers.forEach(function (v, id) {
          if (now - v.t > CFG.staleMs) { peers.delete(id); peersDirty = true; }
          else out.push({ peer: id, kind: 'viewer', isMe: false, sameTab: false, by: v.by, presence: v.s });
        });
        return out;
      }
      setInterval(function () {
        if (peerCbs.length) {
          var now0 = Date.now();
          peers.forEach(function (v, id) { if (now0 - v.t > CFG.staleMs) { peers.delete(id); peersDirty = true; } });
          if (peersDirty) { peersDirty = false; var snap = { peers: list() }; peerCbs.forEach(function (fn) { call(fn, snap); }); }
        }
        if (!joined) return;
        var now = Date.now(), json;
        try { json = JSON.stringify(state); } catch (e) { return; }
        var changed = json !== lastSent;
        if (now - lastSendAt < (changed ? CFG.sendMs : CFG.beatMs)) return;
        lastSent = json; lastSendAt = now;
        send('s', { id: me, by: by, s: state });
      }, 50);
      addEventListener('pagehide', function () { if (joined) send('bye', { id: me }); });

      return {
        presence: function (patch) { if (patch && typeof patch === 'object') Object.assign(state, patch); return Promise.resolve(); },
        peers: list,
        connected: function () { return joined; },
        onPeers: function (fn) {
          if (typeof fn !== 'function') return function () {};
          peerCbs.push(fn); peersDirty = true;
          return function () { peerCbs = peerCbs.filter(function (f) { return f !== fn; }); };
        },
        onConnection: function (fn) {
          if (typeof fn !== 'function') return function () {};
          connCbs.push(fn);
          return function () { connCbs = connCbs.filter(function (f) { return f !== fn; }); };
        },
        on: function (ev, fn) {
          if (!okId(ev) || typeof fn !== 'function') return function () {};
          (evCbs[ev] = evCbs[ev] || []).push(fn);
          return function () { evCbs[ev] = (evCbs[ev] || []).filter(function (f) { return f !== fn; }); };
        },
        emit: function (ev, data) {
          if (!okId(ev) || !small(data)) return Promise.reject(new Error('bad event'));
          var now = Date.now();
          if (now - lastEmitAt < 250) return Promise.resolve();         // at most 4 events a second
          lastEmitAt = now;
          if (joined) send('e', { id: me, ev: ev, d: data });
          (evCbs[ev] || []).forEach(function (fn) { call(fn, { data: data, peer: me, isMe: true, sameTab: true }); });
          return Promise.resolve();
        }
      };
    });
  }

  // Players are anonymous on the shelf: an id, but no name, email or cross-device account.
  var user = {
    id: function () { return Promise.resolve(uid()); },
    me: function () { return Promise.resolve({ name: '' }); },
    profiles: function () { return Promise.resolve({}); }
  };

  var roomPromise = null;
  window.claude = {
    shelf: true,
    use: function (capability) {
      if (capability === 'user') return Promise.resolve(user);
      if (capability === 'room') { if (!roomPromise) roomPromise = makeRoom(); return roomPromise; }
      return Promise.reject(new Error('Not available outside Claude: ' + capability));   // e.g. 'db': games fall back to local saves
    }
  };
})();
