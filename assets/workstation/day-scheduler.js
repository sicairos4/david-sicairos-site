/* Day planner — 15-minute blocks (2026-11-21, David order).
   Fill in the date + wake-up time and it builds your pre-schedule.
   Click a block to shade it, double-click to name the task, drag a
   block to move it, drag its bottom edge to extend it.
   STORAGE: browser localStorage only (+ JSON export/import for a file
   copy you can keep in Google Drive). No hosted database, no network,
   no Supabase. "Add named blocks to day schedule" copies named blocks
   into the existing Workstation block form, so they save with the day
   through the normal Save selected day flow. */
(function () {
  'use strict';
  var host = document.getElementById('dayScheduler');
  if (!host) return;
  var $ = function (id) { return document.getElementById(id); };
  var SLOT = 15, MAX_SLOTS = 96;
  var state = { date: '', wake: 420, end: 1320, tasks: [], selected: null };
  var nextId = 1;

  function pad(n) { return String(n).padStart(2, '0'); }
  function fmt(min) { return pad(Math.floor(min / 60)) + ':' + pad(min % 60); }
  function parse(t) {
    if (!/^\d{2}:\d{2}$/.test(t || '')) return null;
    var h = +t.slice(0, 2), m = +t.slice(3);
    if (h > 23 || m > 59) return null;
    return h * 60 + m;
  }
  function todayStr() {
    var d = new Date();
    return d.getFullYear() + '-' + pad(d.getMonth() + 1) + '-' + pad(d.getDate());
  }
  function key() { return '209-day-schedule:' + state.date; }
  function status(msg) { var s = $('daySchedulerStatus'); if (s) s.textContent = msg || ''; }
  function slots() {
    return Math.max(0, Math.min(MAX_SLOTS, Math.floor((state.end - state.wake) / SLOT)));
  }
  function slotStart(i) { return state.wake + i * SLOT; }
  function taskAt(slot) {
    for (var i = 0; i < state.tasks.length; i++) {
      var t = state.tasks[i];
      if (slot >= t.start && slot < t.start + t.len) return t;
    }
    return null;
  }
  function save() {
    try {
      localStorage.setItem(key(), JSON.stringify({
        date: state.date, wake: fmt(state.wake), end: fmt(state.end),
        tasks: state.tasks
      }));
    } catch (e) { /* private mode: grid still works for the session */ }
  }
  function load() {
    state.tasks = []; state.selected = null;
    try {
      var raw = localStorage.getItem(key());
      if (!raw) return false;
      var data = JSON.parse(raw);
      if (!data || !Array.isArray(data.tasks)) return false;
      if (data.wake) { var w = parse(data.wake); if (w !== null) state.wake = w; }
      if (data.end) { var e = parse(data.end); if (e !== null) state.end = e; }
      state.tasks = data.tasks.filter(function (t) {
        return t && typeof t.name === 'string' && Number.isInteger(t.start) &&
          Number.isInteger(t.len) && t.len > 0;
      }).map(function (t) {
        return { id: t.id || ('t' + (nextId++)), name: t.name,
          start: t.start, len: t.len, shaded: !!t.shaded };
      });
      nextId = state.tasks.reduce(function (m, t) {
        var n = parseInt(String(t.id).replace(/\D/g, ''), 10);
        return isNaN(n) ? m : Math.max(m, n + 1);
      }, 1);
      return true;
    } catch (e) { return false; }
  }
  function rangeFree(start, len, ignoreId) {
    if (start < 0 || start + len > slots()) return false;
    for (var i = 0; i < state.tasks.length; i++) {
      var t = state.tasks[i];
      if (t.id === ignoreId) continue;
      if (start < t.start + t.len && t.start < start + len) return false;
    }
    return true;
  }
  function buildPreSchedule() {
    var n = slots();
    if (n < 2) { status('Pick a wake-up time earlier than the end time first.'); return; }
    if (state.tasks.length && !confirm('Replace the current plan for this date with a fresh pre-schedule?')) return;
    state.tasks = [
      { id: 't' + (nextId++), name: 'Wake up', start: 0, len: 1, shaded: false }
    ];
    if (n > 1) state.tasks.push({
      id: 't' + (nextId++), name: 'Morning routine', start: 1,
      len: Math.min(4, n - 1), shaded: false
    });
    state.selected = null;
    save(); render();
    status('Pre-schedule built from ' + fmt(state.wake) + ' — name the blocks, shade, drag or extend them.');
  }
  function render() {
    var grid = $('daySchedulerGrid');
    if (!grid) return;
    grid.replaceChildren();
    var n = slots();
    var wakeInput = $('dsWake'), endInput = $('dsEnd'), dateInput = $('dsDate');
    if (wakeInput) wakeInput.value = fmt(state.wake);
    if (endInput) endInput.value = fmt(state.end);
    if (dateInput) dateInput.value = state.date;
    grid.style.setProperty('--ds-rows', String(Math.max(n, 1)));
    for (var i = 0; i < n; i++) {
      var label = document.createElement('div');
      label.className = 'ds-time';
      label.textContent = fmt(slotStart(i));
      label.style.gridRow = String(i + 1);
      label.style.gridColumn = '1';
      grid.append(label);
      var t = taskAt(i);
      if (t && t.start === i) {
        var el = document.createElement('div');
        el.className = 'ds-block' + (t.shaded ? ' ds-shaded' : '') +
          (state.selected === t.id ? ' ds-selected' : '');
        el.style.gridRow = (i + 1) + ' / span ' + t.len;
        el.style.gridColumn = '2';
        el.draggable = true;
        el.dataset.taskId = t.id;
        el.dataset.startSlot = String(i);
        var name = document.createElement('span');
        name.className = 'ds-name';
        name.textContent = t.name;
        el.append(name);
        var meta = document.createElement('span');
        meta.className = 'ds-meta';
        meta.textContent = fmt(slotStart(t.start)) + '–' + fmt(slotStart(t.start + t.len));
        el.append(meta);
        var grip = document.createElement('span');
        grip.className = 'ds-resize';
        grip.title = 'Drag to extend';
        grip.dataset.taskId = t.id;
        el.append(grip);
        el.addEventListener('click', function (ev) {
          if (ev.target.classList.contains('ds-resize')) return;
          selectTask(this.dataset.taskId);
        });
        el.addEventListener('dblclick', function () { renameTask(this.dataset.taskId); });
        el.addEventListener('dragstart', function (ev) {
          ev.dataTransfer.setData('text/plain', this.dataset.taskId);
          ev.dataTransfer.effectAllowed = 'move';
        });
        el.addEventListener('dragover', function (ev) { ev.preventDefault(); });
        el.addEventListener('drop', function (ev) {
          ev.preventDefault();
          moveTask(ev.dataTransfer.getData('text/plain'), +this.dataset.startSlot);
        });
        grip.addEventListener('pointerdown', function (ev) { startResize(ev, this.dataset.taskId); });
        grid.append(el);
      } else if (!t) {
        var free = document.createElement('div');
        free.className = 'ds-free';
        free.style.gridRow = String(i + 1);
        free.style.gridColumn = '2';
        free.dataset.slot = String(i);
        free.title = fmt(slotStart(i)) + ' — click to shade, double-click to name';
        free.addEventListener('click', function () { toggleShadeSlot(+this.dataset.slot); });
        free.addEventListener('dblclick', function () { nameSlot(+this.dataset.slot); });
        free.addEventListener('dragover', function (ev) {
          ev.preventDefault();
          this.classList.add('ds-drop');
        });
        free.addEventListener('dragleave', function () { this.classList.remove('ds-drop'); });
        free.addEventListener('drop', function (ev) {
          ev.preventDefault();
          this.classList.remove('ds-drop');
          moveTask(ev.dataTransfer.getData('text/plain'), +this.dataset.slot);
        });
        grid.append(free);
      }
    }
    if (!n) {
      var empty = document.createElement('p');
      empty.className = 'ds-empty';
      empty.textContent = 'Set a wake-up time earlier than the end time, then build your pre-schedule.';
      grid.append(empty);
    }
    syncToolbar();
  }
  function selectTask(id) {
    state.selected = id;
    render();
    var t = state.tasks.find(function (x) { return x.id === id; });
    if (t) status('Selected "' + t.name + '" ' + fmt(slotStart(t.start)) + '–' + fmt(slotStart(t.start + t.len)) + '.');
  }
  function selectedTask() {
    return state.tasks.find(function (x) { return x.id === state.selected; }) || null;
  }
  function syncToolbar() {
    var t = selectedTask();
    var bar = $('dsSelectedActions');
    if (bar) bar.hidden = !t;
    [['dsExtend', !!t], ['dsShorten', !!t], ['dsRename', !!t],
     ['dsShade', !!t], ['dsDelete', !!t]].forEach(function (pair) {
      var b = $(pair[0]);
      if (b) b.disabled = !pair[1];
    });
    var shade = $('dsShade');
    if (shade && t) shade.textContent = t.shaded ? 'Unshade block' : 'Shade block';
  }
  function toggleShadeSlot(slot) {
    var t = taskAt(slot);
    if (t) { t.shaded = !t.shaded; state.selected = t.id; }
    else {
      state.tasks.push({ id: 't' + (nextId++), name: '', start: slot, len: 1, shaded: true });
      state.selected = state.tasks[state.tasks.length - 1].id;
    }
    save(); render();
    status('Block shaded. Double-click it to name the task.');
  }
  function nameSlot(slot) {
    var t = taskAt(slot);
    if (t) { renameTask(t.id); return; }
    var created = { id: 't' + (nextId++), name: '', start: slot, len: 1, shaded: false };
    state.tasks.push(created);
    state.selected = created.id;
    save(); render();
    renameTask(created.id);
  }
  function renameTask(id) {
    var t = state.tasks.find(function (x) { return x.id === id; });
    if (!t) return;
    var grid = $('daySchedulerGrid');
    var el = grid && grid.querySelector('[data-task-id="' + CSS.escape(id) + '"]');
    if (!el) return;
    var input = document.createElement('input');
    input.type = 'text';
    input.className = 'ds-rename';
    input.maxLength = 300;
    input.value = t.name;
    input.setAttribute('aria-label', 'Task name');
    el.replaceChildren(input);
    input.focus();
    input.select();
    var done = false;
    function commit() {
      if (done) return;
      done = true;
      t.name = input.value.trim();
      save(); render();
      status(t.name ? 'Named "' + t.name + '".' : 'Block cleared back to free.');
    }
    input.addEventListener('keydown', function (ev) {
      if (ev.key === 'Enter') { ev.preventDefault(); commit(); }
      if (ev.key === 'Escape') { done = true; render(); }
      ev.stopPropagation();
    });
    input.addEventListener('blur', commit);
  }
  function moveTask(id, toSlot) {
    var t = state.tasks.find(function (x) { return x.id === id; });
    if (!t || toSlot === t.start) return;
    if (!rangeFree(toSlot, t.len, t.id)) {
      status('That spot is taken — drop "' + t.name + '" on a free stretch.');
      return;
    }
    t.start = toSlot;
    state.selected = t.id;
    save(); render();
    status('Moved "' + (t.name || 'block') + '" to ' + fmt(slotStart(toSlot)) + '.');
  }
  function extendSelected(delta) {
    var t = selectedTask();
    if (!t) return;
    var next = t.len + delta;
    if (next < 1) return;
    if (delta > 0 && !rangeFree(t.start, next, t.id)) {
      status('No free room below "' + t.name + '" to extend into.');
      return;
    }
    t.len = next;
    save(); render();
    status('"' + t.name + '" is now ' + (t.len * SLOT) + ' minutes.');
  }
  function deleteSelected() {
    var t = selectedTask();
    if (!t) return;
    if (!confirm('Remove "' + (t.name || 'this block') + '" from the plan?')) return;
    state.tasks = state.tasks.filter(function (x) { return x.id !== t.id; });
    state.selected = null;
    save(); render();
    status('Block removed.');
  }
  function startResize(ev, id) {
    var t = state.tasks.find(function (x) { return x.id === id; });
    if (!t || ev.button !== 0) return;
    ev.preventDefault();
    ev.stopPropagation();
    var grid = $('daySchedulerGrid');
    var startY = ev.clientY;
    var startLen = t.len;
    var rowH = 30;
    var moved = false;
    function onMove(e) {
      var d = Math.round((e.clientY - startY) / rowH);
      if (d === 0) return;
      var next = Math.max(1, startLen + d);
      if (next === t.len) return;
      if (next > startLen && !rangeFree(t.start, next, t.id)) return;
      t.len = next;
      moved = true;
      render();
      var el = grid.querySelector('[data-task-id="' + CSS.escape(id) + '"]');
      if (el) el.classList.add('ds-selected');
      status('"' + t.name + '" — ' + (t.len * SLOT) + ' minutes (release to keep).');
    }
    function onUp() {
      document.removeEventListener('pointermove', onMove);
      document.removeEventListener('pointerup', onUp);
      if (moved) { save(); render(); status('"' + t.name + '" extended to ' + (t.len * SLOT) + ' minutes.'); }
    }
    document.addEventListener('pointermove', onMove);
    document.addEventListener('pointerup', onUp);
  }
  function exportJson() {
    var data = { date: state.date, wake: fmt(state.wake), end: fmt(state.end), tasks: state.tasks };
    var blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = '209-day-schedule-' + state.date + '.json';
    document.body.append(a);
    a.click();
    a.remove();
    setTimeout(function () { URL.revokeObjectURL(a.href); }, 1000);
    status('Exported 209-day-schedule-' + state.date + '.json — save it to Google Drive to keep a cloud copy.');
  }
  function importJson(file) {
    if (!file) return;
    var reader = new FileReader();
    reader.onload = function () {
      try {
        var data = JSON.parse(String(reader.result));
        if (!data || !Array.isArray(data.tasks)) throw new Error('bad file');
        state.date = typeof data.date === 'string' && data.date ? data.date : state.date;
        var w = parse(data.wake), e = parse(data.end);
        if (w !== null) state.wake = w;
        if (e !== null) state.end = e;
        state.tasks = data.tasks.filter(function (t) {
          return t && typeof t.name === 'string' && Number.isInteger(t.start) && Number.isInteger(t.len) && t.len > 0;
        }).map(function (t) {
          return { id: t.id || ('t' + (nextId++)), name: t.name, start: t.start, len: t.len, shaded: !!t.shaded };
        });
        state.selected = null;
        save(); render();
        status('Imported ' + state.tasks.length + ' blocks for ' + state.date + '.');
      } catch (err) {
        status('That file is not a day-schedule JSON export.');
      }
    };
    reader.readAsText(file);
  }
  function pushToDaySchedule() {
    var named = state.tasks.filter(function (t) { return t.name.trim(); })
      .sort(function (a, b) { return a.start - b.start; });
    if (!named.length) { status('Name a block first — only named blocks copy into the day schedule.'); return; }
    var form = $('blockForm');
    if (!form || !window.WorkstationApp || !window.WorkstationApp.record) {
      status('Load your saved Workstation day first (Load saved account), or use Export JSON to keep this plan as a file.');
      return;
    }
    var before = 0;
    try { before = (window.WorkstationApp.record.plan.scheduleBlocks || []).length; } catch (e) {}
    var i = 0;
    (function next() {
      if (i >= named.length) {
        setTimeout(function () {
          var after = before;
          try { after = (window.WorkstationApp.record.plan.scheduleBlocks || []).length; } catch (e) {}
          var added = Math.max(0, after - before);
          status(added ? ('Added ' + added + ' of ' + named.length + ' named block' + (added === 1 ? '' : 's') + ' to the day schedule. Save the day to keep them.') : 'No blocks were added — check the times against existing blocks, then try again.');
        }, 400);
        return;
      }
      var t = named[i++];
      var title = $('blockTitle'), start = $('blockStart'), end = $('blockEnd');
      if (!title || !start || !end) { status('Day schedule form is not on this page.'); return; }
      title.value = t.name;
      start.value = fmt(slotStart(t.start));
      end.value = fmt(slotStart(t.start + t.len));
      form.requestSubmit();
      setTimeout(next, 200);
    })();
  }
  function bind() {
    var setup = $('daySchedulerSetup');
    if (setup) setup.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var d = $('dsDate').value, w = parse($('dsWake').value), e = parse($('dsEnd').value);
      if (!d || w === null || e === null) { status('Fill in the date, wake-up time and end time.'); return; }
      if (w >= e) { status('Wake-up time must be earlier than the end time.'); return; }
      state.date = d; state.wake = w; state.end = e;
      var day = $('day');
      if (day) day.value = d;
      var morning = $('morningStart');
      if (morning) morning.value = fmt(w);
      if (load()) { render(); status('Loaded the saved plan for ' + d + '.'); }
      else buildPreSchedule();
    });
    var dateInput = $('dsDate');
    if (dateInput) dateInput.addEventListener('change', function () {
      if (!dateInput.value) return;
      state.date = dateInput.value;
      var day = $('day');
      if (day) day.value = state.date;
      load(); render();
      status(state.tasks.length ? 'Loaded the saved plan for ' + state.date + '.' : 'No saved plan for ' + state.date + ' yet — build the pre-schedule.');
    });
    var saveBtn = $('dsSave');
    if (saveBtn) saveBtn.addEventListener('click', function () { save(); status('Saved for ' + state.date + ' in this browser.'); });
    var exp = $('dsExport');
    if (exp) exp.addEventListener('click', exportJson);
    var imp = $('dsImport'), impFile = $('dsImportFile');
    if (imp && impFile) {
      imp.addEventListener('click', function () { impFile.click(); });
      impFile.addEventListener('change', function () {
        importJson(impFile.files && impFile.files[0]);
        impFile.value = '';
      });
    }
    var clear = $('dsClear');
    if (clear) clear.addEventListener('click', function () {
      if (!state.tasks.length) return;
      if (!confirm('Clear all blocks for ' + state.date + '?')) return;
      state.tasks = []; state.selected = null;
      save(); render();
      status('Cleared. Build the pre-schedule to start over.');
    });
    var push = $('dsPush');
    if (push) push.addEventListener('click', pushToDaySchedule);
    var ext = $('dsExtend');
    if (ext) ext.addEventListener('click', function () { extendSelected(1); });
    var sho = $('dsShorten');
    if (sho) sho.addEventListener('click', function () { extendSelected(-1); });
    var ren = $('dsRename');
    if (ren) ren.addEventListener('click', function () { if (state.selected) renameTask(state.selected); });
    var sh = $('dsShade');
    if (sh) sh.addEventListener('click', function () {
      var t = selectedTask();
      if (!t) return;
      t.shaded = !t.shaded; save(); render();
    });
    var del = $('dsDelete');
    if (del) del.addEventListener('click', deleteSelected);
    var day = $('day');
    if (day) day.addEventListener('change', function () {
      if (!day.value) return;
      state.date = day.value;
      load(); render();
    });
  }
  function boot() {
    var day = $('day'), morning = $('morningStart');
    state.date = (day && day.value) || todayStr();
    var w = morning ? parse(morning.value) : null;
    if (w !== null) state.wake = w;
    load();
    bind();
    render();
    if (state.tasks.length) status('Loaded the saved plan for ' + state.date + '.');
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot, { once: true });
  else boot();
})();
