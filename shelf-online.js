/* Game Shelf online play.
   Inside Claude, games get multiplayer from window.claude.use('room'). On the shelf that does not exist,
   so this file provides the same small "room" interface on top of a Supabase Realtime broadcast channel:
     room.presence(patch)  merge patch into my state and share it        -> Promise
     room.peers()          [{peer, kind:'viewer', isMe, presence}, ...]  (includes me)
     room.connected()      true while the channel is joined
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
    maxBytes: 1500    // ignore oversized states from other clients
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

  function makeRoom() {
    return loadLib().then(function () {
      var client = window.supabase.createClient(CFG.url, CFG.key, {
        auth: { persistSession: false, autoRefreshToken: false, detectSessionInUrl: false },
        realtime: { params: { eventsPerSecond: 10 } }
      });
      var me = 'p' + Math.random().toString(36).slice(2, 10) + Date.now().toString(36);
      var state = {}, peers = new Map(), joined = false, lastSent = '', lastSendAt = 0;
      var ch = client.channel(channelName, { config: { broadcast: { self: false, ack: false } } });

      ch.on('broadcast', { event: 's' }, function (msg) {
        var p = msg && msg.payload;
        if (!p || typeof p.id !== 'string' || p.id === me || p.id.length > 40 || !p.s || typeof p.s !== 'object') return;
        if (!peers.has(p.id) && peers.size >= CFG.maxPeers) return;
        try { if (JSON.stringify(p.s).length > CFG.maxBytes) return; } catch (e) { return; }
        peers.set(p.id, { s: p.s, t: Date.now() });
      });
      ch.on('broadcast', { event: 'bye' }, function (msg) {
        var p = msg && msg.payload; if (p && typeof p.id === 'string') peers.delete(p.id);
      });
      ch.subscribe(function (status) { joined = status === 'SUBSCRIBED'; if (joined) lastSent = ''; });

      function send(event, payload) { try { ch.send({ type: 'broadcast', event: event, payload: payload }); } catch (e) {} }
      setInterval(function () {
        if (!joined) return;
        var now = Date.now(), json;
        try { json = JSON.stringify(state); } catch (e) { return; }
        var changed = json !== lastSent;
        if (now - lastSendAt < (changed ? CFG.sendMs : CFG.beatMs)) return;
        lastSent = json; lastSendAt = now;
        send('s', { id: me, s: state });
      }, 50);
      addEventListener('pagehide', function () { if (joined) send('bye', { id: me }); });

      return {
        presence: function (patch) { if (patch && typeof patch === 'object') Object.assign(state, patch); return Promise.resolve(); },
        peers: function () {
          var now = Date.now(), out = [{ peer: me, kind: 'viewer', isMe: true, presence: state }];
          peers.forEach(function (v, id) {
            if (now - v.t > CFG.staleMs) peers.delete(id);
            else out.push({ peer: id, kind: 'viewer', isMe: false, presence: v.s });
          });
          return out;
        },
        connected: function () { return joined; }
      };
    });
  }

  var roomPromise = null;
  window.claude = {
    shelf: true,
    use: function (capability) {
      if (capability !== 'room') return Promise.reject(new Error('Not available outside Claude: ' + capability));
      if (!roomPromise) roomPromise = makeRoom();
      return roomPromise;
    }
  };
})();
