import sys
from pathlib import Path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from flask import Flask, render_template_string, request, jsonify
from chatbot.nlu import NLU
from chatbot.router import Router
from database.db import init_database, execute_query

app = Flask(__name__)
nlu = NLU()
router = Router()
init_database()

HTML = r"""
<!DOCTYPE html>
<html lang="bg">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Футболен Мениджър</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: 'Segoe UI', system-ui, sans-serif;
  background: #0f0c29;
  color: #e0e0e0;
  min-height: 100vh;
}
.nav {
  background: rgba(255,255,255,0.05);
  border-bottom: 1px solid rgba(255,255,255,0.1);
  display: flex;
  gap: 2px;
  padding: 0 20px;
  overflow-x: auto;
}
.nav button {
  padding: 16px 24px;
  background: none;
  border: none;
  color: rgba(255,255,255,0.5);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all .2s;
  white-space: nowrap;
}
.nav button:hover { color: #fff; background: rgba(255,255,255,0.03); }
.nav button.active { color: #00d4ff; border-bottom-color: #00d4ff; }
.container { display: flex; height: calc(100vh - 57px); }
.sidebar {
  width: 320px;
  background: rgba(255,255,255,0.03);
  border-right: 1px solid rgba(255,255,255,0.1);
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.sidebar h2 {
  font-size: 16px;
  color: #00d4ff;
  margin-bottom: 8px;
}
.sidebar label {
  font-size: 12px;
  color: rgba(255,255,255,0.5);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.sidebar select, .sidebar input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 8px;
  background: rgba(255,255,255,0.05);
  color: #fff;
  font-size: 13px;
  outline: none;
}
.sidebar select:focus, .sidebar input:focus { border-color: #00d4ff; }
.sidebar select option { background: #1a1a2e; color: #fff; }
.btn {
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all .15s;
}
.btn-primary { background: #00d4ff; color: #000; }
.btn-primary:hover { box-shadow: 0 4px 15px rgba(0,212,255,0.3); transform: translateY(-1px); }
.btn-success { background: #00c853; color: #000; }
.btn-success:hover { box-shadow: 0 4px 15px rgba(0,200,83,0.3); transform: translateY(-1px); }
.btn-danger { background: #ff1744; color: #fff; }
.btn-danger:hover { box-shadow: 0 4px 15px rgba(255,23,68,0.3); transform: translateY(-1px); }
.btn-warning { background: #ffab00; color: #000; }
.btn-warning:hover { box-shadow: 0 4px 15px rgba(255,171,0,0.3); transform: translateY(-1px); }
.btn-sm { padding: 6px 12px; font-size: 12px; }
.btn-group { display: flex; gap: 8px; flex-wrap: wrap; }
.main {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}
.main h2 {
  font-size: 18px;
  color: #fff;
  margin-bottom: 16px;
}
.result-box {
  background: rgba(255,255,255,0.05);
  border-radius: 12px;
  padding: 20px;
  min-height: 200px;
  font-family: 'Consolas', monospace;
  font-size: 13px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
}
.result-box.loading { opacity: 0.5; }
.field-row { display: flex; gap: 8px; flex-wrap: wrap; }
.field-row > * { flex: 1; min-width: 120px; }
.inline-group { display: flex; gap: 8px; align-items: end; }
.inline-group .btn { flex-shrink: 0; }
.hidden { display: none !important; }
table { width: 100%; border-collapse: collapse; font-size: 13px; }
th, td { padding: 10px 12px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.08); }
th { color: rgba(255,255,255,0.5); font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; }
td { color: #e0e0e0; }
tr:hover td { background: rgba(255,255,255,0.03); }
.status-badge {
  display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600;
}
.badge-green { background: rgba(0,200,83,0.2); color: #00c853; }
.badge-red { background: rgba(255,23,68,0.2); color: #ff1744; }
.badge-blue { background: rgba(0,212,255,0.2); color: #00d4ff; }
</style>
</head>
<body>

<div class="nav" id="nav">
  <button class="active" data-tab="clubs">🏁 Клубове</button>
  <button data-tab="players">⚽ Играчи</button>
  <button data-tab="transfers">🔄 Трансфери</button>
  <button data-tab="leagues">🏆 Лиги</button>
  <button data-tab="matches">⚡ Мачове</button>
  <button data-tab="standings">📊 Класиране</button>
</div>

<div class="container">

<!-- SIDEBAR -->
<div class="sidebar" id="sidebar"></div>

<!-- MAIN -->
<div class="main">
  <h2 id="title">Клубове</h2>
  <div class="result-box" id="result">Изберете действие отляво</div>
  <div style="margin-top:16px;display:flex;gap:8px;flex-wrap:wrap" id="examples">
    <span style="color:rgba(255,255,255,0.3);font-size:12px;padding:4px 0">🔍 Бързи примери:</span>
    <button class="${BTN}primary btn-sm" onclick="api('покажи клубове')">🏁 Всички клубове</button>
    <button class="${BTN}primary btn-sm" onclick="api('покажи играчи на Левски София')">👥 Играчи Левски</button>
    <button class="${BTN}primary btn-sm" onclick="api('покажи играчи на ЦСКА София')">👥 Играчи ЦСКА</button>
    <button class="${BTN}primary btn-sm" onclick="api('покажи трансфери на клуб Левски София')">🔄 Трансфери Левски</button>
    <button class="${BTN}primary btn-sm" onclick="api('покажи класиране efbet Лига 2024/2025')">📊 Класиране</button>
    <button class="${BTN}primary btn-sm" onclick="api('помощ')">❓ Помощ</button>
  </div>
</div>

</div>

<script>
const BTN = 'btn btn-';
const state = {};

function qs(s, p) { return (p||document).querySelector(s); }
function qsa(s, p) { return (p||document).querySelectorAll(s); }

function api(text) {
  const box = document.getElementById('result');
  box.classList.add('loading');
  box.textContent = '⏳ Изпълнение...';
  return fetch('/api/chat', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({message: text})
  }).then(r => r.json()).then(d => {
    box.classList.remove('loading');
    box.textContent = d.response;
    return d;
  });
}

function renderSidebar(tab) {
  const sb = document.getElementById('sidebar');
  const title = document.getElementById('title');
  const map = {
    clubs: renderClubs,
    players: renderPlayers,
    transfers: renderTransfers,
    leagues: renderLeagues,
    matches: renderMatches,
    standings: renderStandings,
  };
  title.textContent = {clubs:'🏁 Клубове',players:'⚽ Играчи',transfers:'🔄 Трансфери',leagues:'🏆 Лиги',matches:'⚡ Мачове',standings:'📊 Класиране'}[tab];
  sb.innerHTML = '';
  (map[tab] || (()=>{}))();
}

// ---- CLUBS ----
function renderClubs() {
  const sb = document.getElementById('sidebar');
  sb.innerHTML = `
    <h2>Създай клуб</h2>
    <label>Име на клуб</label>
    <input id="clubName" placeholder="напр. Ботев Пловдив">
    <button class="${BTN}primary" onclick="api('добави клуб '+qg('clubName'))">➕ Създай</button>
    <div class="btn-group" style="margin-top:4px">
      <button class="${BTN}primary btn-sm" onclick="document.getElementById('clubName').value='Нов Клуб';api('добави клуб Нов Клуб')">📌 Пример</button>
    </div>
    <hr style="border-color:rgba(255,255,255,0.1);margin:8px 0">
    <h2>Действия</h2>
    <button class="${BTN}primary" onclick="api('покажи клубове')">📋 Всички клубове</button>
    <hr style="border-color:rgba(255,255,255,0.1);margin:8px 0">
    <h2>Избери клуб</h2>
    <label>Изберете клуб</label>
    <select id="selClub" onchange="selectClub(this.value)"></select>
    <div id="clubActions" class="hidden" style="display:flex;flex-direction:column;gap:8px;margin-top:8px">
      <button class="${BTN}primary btn-sm" onclick="api('покажи играчи на '+state.club)">👥 Играчи</button>
      <button class="${BTN}danger btn-sm" onclick="if(confirm('Сигурни ли сте?'))api('изтрий клуб '+state.club)">🗑️ Изтрий</button>
    </div>
  `;
  api('покажи клубове').then(d => {
    const sel = document.getElementById('selClub');
    const names = [...d.response.matchAll(/🏆\s+\d+\.\s+(.+)/g)].map(m=>m[1]);
    names.forEach(n => { const o = document.createElement('option'); o.value=n; o.textContent=n; sel.appendChild(o); });
  });
}
function selectClub(name) {
  state.club = name;
  document.getElementById('clubActions').classList.remove('hidden');
  document.getElementById('clubActions').style.display = 'flex';
}
function qg(id) { return document.getElementById(id).value.trim(); }

// ---- PLAYERS ----
function renderPlayers() {
  const sb = document.getElementById('sidebar');
  sb.innerHTML = `
    <h2>Добави играч</h2>
    <label>Име</label>
    <input id="pName" placeholder="напр. Иван Иванов">
    <label>Клуб</label>
    <select id="pClub"></select>
    <div class="field-row">
      <div><label>Позиция</label><select id="pPos"><option>GK</option><option>DF</option><option selected>MF</option><option>FW</option></select></div>
      <div><label>Номер</label><input id="pNum" type="number" min=1 max=99 value=20></div>
    </div>
    <button class="${BTN}success" onclick="api('добави играч '+qg('pName')+' в '+qs('#pClub').value+' позиция '+qs('#pPos').value+' номер '+qg('pNum'))">➕ Добави</button>
    <div class="btn-group" style="margin-top:4px">
      <button class="${BTN}success btn-sm" onclick="document.getElementById('pName').value='Иван Иванов';api('добави играч Иван Иванов в '+qs('#pClub').value+' позиция FW номер '+qg('pNum'))">📌 Пример Иван</button>
      <button class="${BTN}success btn-sm" onclick="document.getElementById('pName').value='Петър Петров';api('добави играч Петър Петров в '+qs('#pClub').value+' позиция GK номер '+qg('pNum'))">📌 Пример Петър</button>
    </div>
    <hr style="border-color:rgba(255,255,255,0.1);margin:8px 0">
    <h2>Преглед</h2>
    <label>Изберете клуб</label>
    <select id="viewClub" onchange="api('покажи играчи на '+this.value)"></select>
    <hr style="border-color:rgba(255,255,255,0.1);margin:8px 0">
    <h2>Номер / Статус</h2>
    <label>Играч</label>
    <input id="upName" placeholder="име на играч">
    <label>Клуб</label>
    <select id="upClub"></select>
    <div class="btn-group">
      <button class="${BTN}primary btn-sm" onclick="api('смени номер на '+qg('upName')+' от '+qs('#upClub').value+' на '+qg('upNum'))">🔢 Номер</button>
      <input id="upNum" type="number" min=1 max=99 value=10 style="width:70px">
    </div>
    <div class="btn-group" style="margin-top:4px">
      <button class="${BTN}success btn-sm" onclick="api('активирай '+qg('upName')+' от '+qs('#upClub').value)">✅ Активен</button>
      <button class="${BTN}warning btn-sm" onclick="api('контузи '+qg('upName')+' от '+qs('#upClub').value)">🤕 Контузен</button>
      <button class="${BTN}danger btn-sm" onclick="api('наказан '+qg('upName')+' от '+qs('#upClub').value)">⛔ Наказан</button>
    </div>
    <hr style="border-color:rgba(255,255,255,0.1);margin:8px 0">
    <h2>Изтрий играч</h2>
    <div class="inline-group">
      <input id="delName" placeholder="име на играч" style="flex:1">
      <select id="delClub"><option value="">Без клуб</option></select>
      <button class="${BTN}danger btn-sm" onclick="api('изтрий играч '+qg('delName')+' от '+qs('#delClub').value)">🗑️</button>
    </div>
  `;
  refreshClubDropdowns();
}
function refreshClubDropdowns() {
  api('покажи клубове').then(d => {
    const names = [...d.response.matchAll(/🏆\s+\d+\.\s+(.+)/g)].map(m=>m[1]);
    ['pClub','viewClub','upClub','delClub'].forEach(id => {
      const sel = document.getElementById(id); if(!sel) return;
      sel.innerHTML = names.map(n => '<option>'+n+'</option>').join('');
    });
  });
}

// ---- TRANSFERS ----
function renderTransfers() {
  const sb = document.getElementById('sidebar');
  sb.innerHTML = `
    <h2>Нов трансфер</h2>
    <label>Играч</label>
    <input id="tPlayer" placeholder="име на играч">
    <label>От клуб</label>
    <select id="tFrom"></select>
    <label>Към клуб</label>
    <select id="tTo"></select>
    <label>Сума (опционално)</label>
    <input id="tFee" placeholder="напр. 500000">
    <button class="${BTN}primary" onclick="doTransfer()">🔄 Трансферирай</button>
    <div class="btn-group" style="margin-top:4px">
      <button class="${BTN}primary btn-sm" onclick="document.getElementById('tPlayer').value='Живко Петров';api('трансфер Живко Петров от '+qs('#tFrom').value+' в '+qs('#tTo').value)">📌 Пример играч</button>
    </div>
    <hr style="border-color:rgba(255,255,255,0.1);margin:8px 0">
    <h2>История</h2>
    <label>Търсене по играч</label>
    <div class="inline-group">
      <input id="histPlayer" placeholder="име на играч" style="flex:1">
      <button class="${BTN}primary btn-sm" onclick="api('покажи трансфери на '+qg('histPlayer'))">🔍</button>
    </div>
    <label style="margin-top:8px">Търсене по клуб</label>
    <div class="inline-group">
      <select id="histClub"></select>
      <button class="${BTN}primary btn-sm" onclick="api('покажи трансфери на клуб '+qs('#histClub').value)">🔍</button>
    </div>
  `;
  api('покажи клубове').then(d => {
    const names = [...d.response.matchAll(/🏆\s+\d+\.\s+(.+)/g)].map(m=>m[1]);
    ['tFrom','tTo','histClub'].forEach(id => {
      const sel = document.getElementById(id); if(!sel) return;
      sel.innerHTML = names.map(n => '<option>'+n+'</option>').join('');
    });
  });
}
function doTransfer() {
  const player = qg('tPlayer');
  const from = qs('#tFrom').value;
  const to = qs('#tTo').value;
  const fee = qg('tFee');
  let cmd = 'трансфер '+player+' от '+from+' в '+to;
  if (fee) cmd += ' сума '+fee;
  api(cmd);
}

// ---- LEAGUES ----
function renderLeagues() {
  const sb = document.getElementById('sidebar');
  sb.innerHTML = `
    <h2>Създай лига</h2>
    <label>Име</label>
    <input id="lName" placeholder="напр. efbet Лига">
    <label>Сезон</label>
    <input id="lSeason" placeholder="2025/2026" value="2025/2026">
    <button class="${BTN}primary" onclick="api('създай лига '+qg('lName')+' '+qg('lSeason'))">🏆 Създай</button>
    <hr style="border-color:rgba(255,255,255,0.1);margin:8px 0">
    <h2>Управление</h2>
    <label>Изберете лига</label>
    <select id="selLeague" onchange="leagueChanged()"></select>
    <div id="leagueActions" class="hidden" style="display:flex;flex-direction:column;gap:8px;margin-top:8px">
      <label>Добави отбор</label>
      <div class="inline-group">
        <select id="addTeam"></select>
        <button class="${BTN}success btn-sm" onclick="api('добави отбор '+qs('#addTeam').value+' в лига '+state.league_name+' '+state.league_season)">➕</button>
      </div>
      <button class="${BTN}primary btn-sm" onclick="api('генерирай програма '+state.league_name+' '+state.league_season)">📅 Генерирай програма</button>
      <button class="${BTN}primary btn-sm" onclick="api('покажи програма '+state.league_name+' '+state.league_season)">📋 Програма</button>
      <button class="${BTN}primary btn-sm" onclick="api('покажи отбори в лига '+state.league_name+' '+state.league_season)">👥 Отбори</button>
    </div>
  `;
  api('покажи клубове').then(d => {
    const names = [...d.response.matchAll(/🏆\s+\d+\.\s+(.+)/g)].map(m=>m[1]);
    const sel = document.getElementById('addTeam');
    if(sel) sel.innerHTML = names.map(n=>'<option>'+n+'</option>').join('');
  });
  // populate league dropdown
  setTimeout(() => {
    const conn = new XMLHttpRequest();
    conn.open('POST','/api/raw');
    conn.setRequestHeader('Content-Type','application/json');
    conn.onload = function() {
      try {
        const data = JSON.parse(this.responseText);
        const sel = document.getElementById('selLeague');
        data.forEach(l => {
          const o = document.createElement('option');
          o.value = l.name+'||'+l.season;
          o.textContent = l.name+' ('+l.season+')';
          sel.appendChild(o);
        });
      } catch(e) {}
    };
    conn.send(JSON.stringify({query:"SELECT name, season FROM leagues ORDER BY season DESC"}));
  }, 100);
}
function leagueChanged() {
  const val = qs('#selLeague').value;
  if (!val) return;
  const parts = val.split('||');
  state.league_name = parts[0];
  state.league_season = parts[1];
  document.getElementById('leagueActions').classList.remove('hidden');
  document.getElementById('leagueActions').style.display = 'flex';
}

// ---- MATCHES ----
function renderMatches() {
  const sb = document.getElementById('sidebar');
  sb.innerHTML = `
    <h2>Избери мач</h2>
    <label>Лига</label>
    <select id="mLeague" onchange="loadRounds()"></select>
    <label>Кръг</label>
    <select id="mRound" onchange="loadMatches()"></select>
    <label>Мач</label>
    <select id="mMatch" onchange="selectMatch()"></select>
    <div id="matchActions" class="hidden" style="display:flex;flex-direction:column;gap:8px;margin-top:8px">
      <h2>Резултат</h2>
      <div class="inline-group">
        <input id="mHomeGoals" type="number" min=0 value=0 style="width:60px;text-align:center">
        <span style="color:rgba(255,255,255,0.3)">:</span>
        <input id="mAwayGoals" type="number" min=0 value=0 style="width:60px;text-align:center">
        <button class="${BTN}primary btn-sm" onclick="setResult()">💾 Запиши</button>
      </div>
      <hr style="border-color:rgba(255,255,255,0.1);margin:8px 0">
      <h2>Гол</h2>
      <div class="inline-group">
        <input id="gPlayer" placeholder="име на играч" style="flex:1">
        <input id="gMinute" type="number" min=1 max=120 value=10 style="width:60px">
        <button class="${BTN}success btn-sm" onclick="addGoal()">⚽</button>
      </div>
      <h2>Картон</h2>
      <div class="inline-group">
        <input id="cPlayer" placeholder="име на играч" style="flex:1">
        <select id="cType"><option value="Y">🟨 Жълт</option><option value="R">🟥 Червен</option></select>
        <input id="cMinute" type="number" min=1 max=120 value=10 style="width:60px">
        <button class="${BTN}warning btn-sm" onclick="addCard()">🚫</button>
      </div>
      <hr style="border-color:rgba(255,255,255,0.1);margin:8px 0">
      <button class="${BTN}primary btn-sm" onclick="api('покажи събития '+state.match_id)">📋 Събития</button>
      <div class="btn-group" style="margin-top:4px">
        <button class="${BTN}success btn-sm" onclick="document.getElementById('gPlayer').value='Росен Иванов';document.getElementById('gMinute').value='30';addGoal()">⚽ Пример гол</button>
        <button class="${BTN}warning btn-sm" onclick="document.getElementById('cPlayer').value='Димитър Петров';document.getElementById('cMinute').value='60';addCard()">🟨 Пример картон</button>
      </div>
    </div>
    <hr style="border-color:rgba(255,255,255,0.1);margin:8px 0">
    <h2>Кръг</h2>
    <div class="inline-group">
      <select id="viewLeague"></select>
      <input id="viewRound" type="number" min=1 value=1 style="width:60px">
      <button class="${BTN}primary btn-sm" onclick="api('покажи кръг '+qg('viewRound')+' '+qs('#viewLeague').value)">📋</button>
    </div>
  `;
  api('покажи клубове');
  // populate league dropdowns
  setTimeout(() => {
    const conn = new XMLHttpRequest();
    conn.open('POST','/api/raw');
    conn.setRequestHeader('Content-Type','application/json');
    conn.onload = function() {
      try {
        const data = JSON.parse(this.responseText);
        ['mLeague','viewLeague'].forEach(id => {
          const sel = document.getElementById(id); if(!sel) return;
          sel.innerHTML = data.map(l => {
            const o = document.createElement('option');
            o.value = l.name+'||'+l.season;
            o.textContent = l.name+' ('+l.season+')';
            return o;
          }).join('');
        });
        loadRounds();
      } catch(e) {}
    };
    conn.send(JSON.stringify({query:"SELECT name, season FROM leagues ORDER BY season DESC"}));
  }, 100);
}
function loadRounds() {
  const val = qs('#mLeague').value;
  if (!val) return;
  const parts = val.split('||');
  state.m_league = parts[0];
  state.m_season = parts[1];
  api('покажи програма '+state.m_league+' '+state.m_season).then(d => {
    const rounds = [...d.response.matchAll(/🔄 КРЪГ (\d+)/g)].map(m=>parseInt(m[1]));
    const sel = document.getElementById('mRound');
    sel.innerHTML = [...new Set(rounds)].sort((a,b)=>a-b).map(r => '<option value='+r+'>Кръг '+r+'</option>').join('');
    loadMatches();
  });
}
function loadMatches() {
  const round = qs('#mRound').value;
  if (!round) return;
  api('покажи кръг '+round+' '+state.m_league+' '+state.m_season).then(d => {
    const sel = document.getElementById('mMatch');
    const matches = [...d.response.matchAll(/🏆\s+(.+?)\s+\((\d+:\d+|неизигран)\)\s+\[ID:(\d+)\]/g)];
    sel.innerHTML = matches.map(m => '<option value="'+m[3]+'">'+m[1]+' ('+m[2]+')</option>').join('');
    selectMatch();
  });
}
function selectMatch() {
  const id = qs('#mMatch').value;
  if (!id) return;
  state.match_id = id;
  api('избери мач '+id).then(() => {
    document.getElementById('matchActions').classList.remove('hidden');
    document.getElementById('matchActions').style.display = 'flex';
  });
}
function setResult() {
  const txt = qs('#mMatch option:checked').textContent;
  const teams = txt.split(' (')[0];
  const parts = teams.split(' - ');
  api('резултат '+parts[0]+'-'+parts[1]+' '+qg('mHomeGoals')+':'+qg('mAwayGoals')+' запиши');
}
function addGoal() {
  const txt = qs('#mMatch option:checked').textContent;
  const teams = txt.split(' (')[0];
  const parts = teams.split(' - ');
  // Determine which club the player is in by checking
  api('гол '+qg('gPlayer')+' за '+parts[0]+' '+qg('gMinute'));
}
function addCard() {
  const txt = qs('#mMatch option:checked').textContent;
  const teams = txt.split(' (')[0];
  const parts = teams.split(' - ');
  api('картон '+qg('cPlayer')+' за '+parts[0]+' '+qs('#cType').value+' '+qg('cMinute'));
}

// ---- STANDINGS ----
function renderStandings() {
  const sb = document.getElementById('sidebar');
  sb.innerHTML = `
    <h2>Класиране</h2>
    <label>Лига</label>
    <select id="sLeague"></select>
    <button class="${BTN}primary" onclick="api('покажи класиране '+qs('#sLeague').value)">📊 Покажи</button>
  `;
  setTimeout(() => {
    const conn = new XMLHttpRequest();
    conn.open('POST','/api/raw');
    conn.setRequestHeader('Content-Type','application/json');
    conn.onload = function() {
      try {
        const data = JSON.parse(this.responseText);
        const sel = document.getElementById('sLeague');
        sel.innerHTML = data.map(l => {
          const o = document.createElement('option');
          o.value = l.name+' '+l.season;
          o.textContent = l.name+' ('+l.season+')';
          return o;
        }).join('');
      } catch(e) {}
    };
    conn.send(JSON.stringify({query:"SELECT name, season FROM leagues ORDER BY season DESC"}));
  }, 100);
}

function runCmd(cmd) {
  api(cmd);
}

// ---- NAV ----
qsa('.nav button').forEach(btn => {
  btn.onclick = function() {
    qsa('.nav button').forEach(b => b.classList.remove('active'));
    this.classList.add('active');
    renderSidebar(this.dataset.tab);
  };
});

// init
renderSidebar('clubs');
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    msg = data.get("message", "").strip()
    if not msg:
        return jsonify({"response": "Моля, въведете съобщение"})
    result = nlu.parse(msg)
    response = router.route(result["intent"], result["params"], msg)
    return jsonify({"response": response})

@app.route("/api/raw", methods=["POST"])
def raw_query():
    data = request.get_json()
    q = data.get("query", "")
    if q.strip().upper().startswith("SELECT"):
        rows = execute_query(q, fetch_all=True)
        return jsonify([dict(r) for r in rows])
    return jsonify([])

if __name__ == "__main__":
    import webbrowser
    webbrowser.open("http://127.0.0.1:5000")
    app.run(debug=False, port=5000)
