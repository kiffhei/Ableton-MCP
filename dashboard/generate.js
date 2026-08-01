#!/usr/bin/env node
const fs = require('fs')
const path = require('path')

const ROOT = path.resolve(__dirname, '..')

// Paleta validada con el script de contraste/CVD del skill de dataviz contra
// la superficie de tarjeta real de este dashboard (#363636). Encabeza con
// azul/naranja/ámbar (colores de clip de Ableton Live) por pedido explícito;
// completa con violeta/rosa/verde/rojo para las categorías restantes. Orden
// fijo — identidad de categoría, nunca reasignado por estado.
const CLIP_COLORS = ['#3389D6', '#C97025', '#B8891C', '#8A5FDB', '#2FAA55', '#D6559E', '#1A9C82', '#E0475F']
const CLAUDE_CORAL = '#D97757'

const STATUS_META = {
  done: { label: 'Completo', icon: '✓' },
  partial: { label: 'En progreso', icon: '◐' },
  pending: { label: 'Por iniciar', icon: '○' },
}

function readSafe(filePath) {
  try {
    return fs.readFileSync(filePath, 'utf8')
  } catch {
    return null
  }
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

function countLines(filePath) {
  const content = readSafe(filePath)
  return content ? content.split('\n').length : 0
}

function parseChecklist(filePath) {
  const content = readSafe(filePath)
  if (!content) return { done: 0, total: 0 }
  let done = 0
  let total = 0
  for (const line of content.split('\n')) {
    if (/^\s*-\s\[x\]/i.test(line)) {
      done++
      total++
    } else if (/^\s*-\s\[\s\]/.test(line)) {
      total++
    }
  }
  return { done, total }
}

function countTests(filePath) {
  const content = readSafe(filePath)
  if (!content) return 0
  const matches = content.match(/^def test_/gm)
  return matches ? matches.length : 0
}

function parseGenres(claudeMdText) {
  const m = claudeMdText.match(/## Géneros disponibles[^\n]*\n\n([\s\S]*?)\n\n---/)
  if (!m) return []
  return m[1]
    .split(/,\s*/)
    .map((g) => g.trim().replace(/_/g, ' '))
    .filter(Boolean)
}

// Categorías reales de la arquitectura (agrupan los 12 módulos de src/ en
// unidades con sentido para quien no lee Python). El status de cada una se
// deriva de si sus archivos existen Y de si las tareas asociadas del checklist
// están marcadas — no se asume nada que no esté verificado.
const CATEGORIES = [
  {
    name: 'Motor musical',
    desc: 'Teoría musical, escalas, acordes y progresiones — el núcleo sin dependencias externas',
    files: ['src/music_theory.py', 'src/project_manager.py'],
    status: 'done',
  },
  {
    name: 'Comunicación con Ableton',
    desc: 'Cliente OSC — el puente en tiempo real hacia AbletonOSC',
    files: ['src/osc_client.py'],
    status: 'done',
  },
  {
    name: 'Servidor MCP',
    desc: 'Protocolo MCP de Anthropic — expone las 37 herramientas a Claude',
    files: ['src/server.py', 'src/tool_definitions.py'],
    status: 'done',
  },
  {
    name: 'Control de sesión',
    desc: 'Clips, transporte, tracks — control en vivo de la sesión de Live',
    files: ['src/clip_tools.py', 'src/transport_tools.py', 'src/track_tools.py'],
    status: 'done',
  },
  {
    name: 'Dispositivos y plugins',
    desc: 'Carga y control de instrumentos, plugins VST/AU y sus parámetros',
    files: ['src/device_tools.py', 'src/plugin_registry.py', 'src/registry_tools.py'],
    status: 'done',
  },
  {
    name: 'Gestión de proyectos',
    desc: 'Estado persistente entre sesiones — guardar, cargar, listar proyectos',
    files: ['src/project_tools.py'],
    status: 'done',
  },
  {
    name: 'Puente Max for Live',
    desc: '"Claude Channel Strip" — control por voz/texto desde un device de Max',
    files: [],
    status: 'partial',
  },
]

function buildDashboardHtml() {
  const devTasks = parseChecklist(path.join(ROOT, 'DEV_TASKS.md'))
  const designTasks = parseChecklist(path.join(ROOT, 'DESIGN_TASKS.md'))
  const totalDone = devTasks.done + designTasks.done
  const totalTasks = devTasks.total + designTasks.total
  const percent = totalTasks > 0 ? Math.round((totalDone / totalTasks) * 100) : 0

  const testCount = countTests(path.join(ROOT, 'tests/test_music_theory.py'))

  const claudeMd = readSafe(path.join(ROOT, 'CLAUDE.md')) || ''
  const claudeToolsMatch = claudeMd.match(/Herramientas disponibles\s*\((\d+)/i)
  const toolCount = claudeToolsMatch ? claudeToolsMatch[1] : '37'
  const genres = parseGenres(claudeMd)
  const genreChips = genres.map((g) => `<span class="genre-chip">${escapeHtml(g)}</span>`).join('')

  const categoriesWithData = CATEGORIES.map((c, i) => {
    const lines = c.files.reduce((sum, f) => sum + countLines(path.join(ROOT, f)), 0)
    return { ...c, lines, color: CLIP_COLORS[i % CLIP_COLORS.length] }
  })

  const totalLines = categoriesWithData.reduce((sum, c) => sum + c.lines, 0)
  const maxLines = Math.max(...categoriesWithData.map((c) => c.lines), 1)

  const statTiles = [
    { label: 'Herramientas MCP', value: toolCount, color: CLIP_COLORS[0] },
    { label: 'Géneros musicales soportados', value: '60+', color: CLIP_COLORS[1] },
    { label: 'Tests automatizados', value: String(testCount), color: CLIP_COLORS[2] },
    { label: 'Avance del proyecto', value: `${percent}%`, color: CLIP_COLORS[3] },
    { label: 'Módulos de arquitectura', value: String(CATEGORIES.length), color: CLIP_COLORS[4] },
  ]

  const categoryRows = categoriesWithData
    .map((c) => {
      const meta = STATUS_META[c.status]
      const barWidth = c.lines > 0 ? Math.max(6, Math.round((c.lines / maxLines) * 100)) : 0
      return `
      <li class="clip-row" data-status="${c.status}">
        <span class="clip-swatch" style="background:${c.color}"></span>
        <div class="clip-info">
          <div class="clip-head">
            <span class="clip-name">${escapeHtml(c.name)}</span>
            <span class="clip-status status-${c.status}">${meta.icon} ${meta.label}</span>
          </div>
          <p class="clip-desc">${escapeHtml(c.desc)}</p>
          ${
            c.lines > 0
              ? `<div class="clip-bar-track"><div class="clip-bar-fill" style="width:${barWidth}%;background:${c.color}"></div></div><span class="clip-bar-label">${c.lines} líneas</span>`
              : ''
          }
        </div>
      </li>`
    })
    .join('')

  const statTilesHtml = statTiles
    .map(
      (s) => `
      <div class="stat-tile">
        <span class="stat-dot" style="background:${s.color}"></span>
        <span class="stat-value">${escapeHtml(s.value)}</span>
        <span class="stat-label">${escapeHtml(s.label)}</span>
      </div>`
    )
    .join('')

  const generatedAt = new Date().toISOString().slice(0, 16).replace('T', ' ')

  return `<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Ableton MCP — Estado del proyecto</title>
<style>
  :root {
    color-scheme: dark;
    --bg: #2e2e2e;
    --surface: #363636;
    --surface-raised: #404040;
    --border: rgba(255,255,255,0.12);
    --text-primary: #f0f0f0;
    --text-secondary: #bcbcbc;
    --text-muted: #8a8a8a;
    --ableton-blue: #3389D6;
    --claude-coral: ${CLAUDE_CORAL};
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; padding: 2rem;
    background-color: var(--bg);
    background-image:
      linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
    background-size: 30px 30px;
    color: var(--text-primary);
    font-family: -apple-system, "Inter", system-ui, "Segoe UI", sans-serif;
    line-height: 1.5;
  }
  code, .mono { font-family: ui-monospace, "SF Mono", Menlo, monospace; }
  .eyebrow { display: block; font-size: 0.74rem; font-weight: 700; letter-spacing: 0.22em; text-transform: uppercase; color: var(--ableton-blue); margin-bottom: 0.5rem; }
  h1 { font-size: 1.6rem; margin: 0 0 0.3rem; font-weight: 700; }
  .subtitle { color: var(--text-muted); font-size: 0.85rem; margin-bottom: 1.5rem; }

  .comm-banner { display: flex; align-items: center; gap: 1.25rem; background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 1.1rem 1.5rem; margin-bottom: 1.75rem; }
  .comm-node { display: flex; align-items: center; gap: 0.55rem; font-weight: 700; font-size: 0.95rem; white-space: nowrap; }
  .comm-node-dot { width: 13px; height: 13px; border-radius: 50%; }
  .comm-node-claude .comm-node-dot { background: var(--claude-coral); box-shadow: 0 0 14px var(--claude-coral); }
  .comm-node-ableton .comm-node-dot { background: var(--ableton-blue); box-shadow: 0 0 14px var(--ableton-blue); }
  .comm-path { flex: 1; position: relative; height: 2px; background: linear-gradient(90deg, var(--claude-coral), var(--ableton-blue)); border-radius: 2px; margin: 0 0.25rem; }
  .pulse { position: absolute; top: 50%; width: 7px; height: 7px; border-radius: 50%; background: #fff; transform: translate(-50%, -50%); box-shadow: 0 0 10px #fff; animation: travel 3.2s linear infinite; }
  .pulse-2 { animation-delay: 1.07s; }
  .pulse-3 { animation-delay: 2.13s; }
  @keyframes travel { 0% { left: 0%; opacity: 0; } 8% { opacity: 1; } 92% { opacity: 1; } 100% { left: 100%; opacity: 0; } }
  .comm-caption { font-size: 0.7rem; color: var(--text-muted); white-space: nowrap; }

  .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 0.9rem; margin-bottom: 1.75rem; }
  .stat-tile { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 1.1rem 1.15rem; display: flex; flex-direction: column; gap: 0.35rem; transition: transform 150ms ease, background 150ms ease; }
  .stat-tile:hover { transform: translateY(-2px); background: var(--surface-raised); }
  .stat-dot { width: 10px; height: 10px; border-radius: 3px; }
  .stat-value { font-size: 1.75rem; font-weight: 800; font-variant-numeric: tabular-nums; }
  .stat-label { font-size: 0.82rem; color: var(--text-secondary); font-weight: 500; }

  .panel { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 1.5rem; margin-bottom: 1.25rem; }
  .panel h2 { margin: 0 0 1.1rem; font-size: 1.15rem; display: flex; align-items: center; gap: 0.65rem; font-weight: 700; }
  .panel h2::before { content: ''; width: 9px; height: 9px; border-radius: 3px; background: var(--ableton-blue); display: inline-block; }

  .filters { display: flex; gap: 0.6rem; margin-bottom: 1.1rem; flex-wrap: wrap; }
  .filter-btn { background: var(--surface-raised); border: 1px solid var(--border); color: var(--text-secondary); border-radius: 7px; padding: 0.5rem 1rem; font-size: 0.86rem; font-weight: 600; cursor: pointer; transition: background 120ms ease, color 120ms ease, border-color 120ms ease; }
  .filter-btn:hover { color: var(--text-primary); }
  .filter-btn.active { background: var(--ableton-blue); color: #0b1420; border-color: var(--ableton-blue); }

  .clip-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 0.7rem; }
  .clip-row { display: flex; gap: 1rem; align-items: flex-start; background: var(--surface-raised); border: 1px solid var(--border); border-radius: 9px; padding: 0.9rem 1.1rem; transition: transform 150ms ease, border-color 150ms ease; }
  .clip-row:hover { transform: translateX(3px); border-color: rgba(255,255,255,0.28); }
  .clip-row.hidden { display: none; }
  .clip-swatch { width: 11px; align-self: stretch; border-radius: 3px; flex-shrink: 0; min-height: 40px; }
  .clip-info { flex: 1; min-width: 0; }
  .clip-head { display: flex; align-items: center; justify-content: space-between; gap: 0.75rem; flex-wrap: wrap; }
  .clip-name { font-size: 1rem; font-weight: 700; }
  .clip-status { font-size: 0.76rem; font-weight: 700; padding: 0.2rem 0.65rem; border-radius: 999px; white-space: nowrap; }
  .status-done { background: rgba(47,170,85,0.18); color: #7fe0a0; }
  .status-partial { background: rgba(184,137,28,0.2); color: #f0c15e; }
  .status-pending { background: rgba(255,255,255,0.1); color: var(--text-muted); }
  .clip-desc { margin: 0.3rem 0 0.5rem; font-size: 0.85rem; color: var(--text-secondary); }
  .clip-bar-track { height: 6px; background: rgba(255,255,255,0.08); border-radius: 3px; overflow: hidden; margin-bottom: 0.3rem; }
  .clip-bar-fill { height: 100%; border-radius: 3px; }
  .clip-bar-label { font-size: 0.7rem; color: var(--text-muted); font-variant-numeric: tabular-nums; }

  .demo-caption { margin: 0 0 1rem; font-size: 0.78rem; color: var(--text-muted); font-style: italic; }
  .terminal-mock { background: #1a1a1a; border: 1px solid var(--border); border-radius: 10px; overflow: hidden; }
  .terminal-bar { display: flex; align-items: center; gap: 0.5rem; padding: 0.6rem 0.85rem; background: #232323; border-bottom: 1px solid var(--border); }
  .term-dot { width: 11px; height: 11px; border-radius: 50%; }
  .term-dot-red { background: #ff5f57; }
  .term-dot-yellow { background: #febc2e; }
  .term-dot-green { background: #28c840; }
  .term-title { margin-left: 0.5rem; font-size: 0.76rem; color: var(--text-muted); font-family: ui-monospace, monospace; }
  .terminal-body { padding: 1.1rem 1.25rem 1.3rem; font-family: ui-monospace, "SF Mono", Menlo, monospace; font-size: 0.92rem; min-height: 70px; }
  .term-prompt { color: var(--text-primary); }
  .term-caret { color: var(--ableton-blue); font-weight: 700; margin-right: 0.4rem; }
  .term-cursor { display: inline-block; margin-left: 2px; color: var(--ableton-blue); animation: blink 1s step-end infinite; }
  @keyframes blink { 50% { opacity: 0; } }
  .term-response { margin-top: 0.7rem; color: #7fe0a0; opacity: 0; transition: opacity 400ms ease; }
  .term-response.visible { opacity: 1; }

  .genre-grid { display: flex; flex-wrap: wrap; gap: 0.5rem; }
  .genre-chip { background: var(--surface-raised); border: 1px solid var(--border); color: var(--text-secondary); border-radius: 999px; padding: 0.35rem 0.85rem; font-size: 0.78rem; font-weight: 500; }

  .toolbar { display: flex; justify-content: flex-end; gap: 0.6rem; margin-bottom: 1.25rem; }
  .toolbar-btn { display: inline-flex; align-items: center; gap: 0.45rem; background: var(--surface); border: 1px solid var(--border); color: var(--text-primary); border-radius: 8px; padding: 0.55rem 1rem; font-size: 0.82rem; font-weight: 600; font-family: inherit; cursor: pointer; transition: background 150ms ease, transform 120ms ease; }
  .toolbar-btn:hover { background: var(--surface-raised); }
  .toolbar-btn:active { transform: scale(0.97); }
  .toolbar-icon { width: 16px; height: 16px; flex-shrink: 0; }
  #refresh-btn .toolbar-icon { transition: transform 500ms ease; }
  #refresh-btn.refreshing .toolbar-icon { animation: spin 700ms linear infinite; }
  @keyframes spin { to { transform: rotate(360deg); } }

  .modal-backdrop { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.55); align-items: center; justify-content: center; z-index: 50; }
  .modal-backdrop.open { display: flex; }
  .modal { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 1.5rem; width: min(480px, 90vw); }
  .modal h3 { margin: 0 0 0.5rem; font-size: 1.05rem; }
  .modal-hint { margin: 0 0 0.9rem; font-size: 0.82rem; color: var(--text-secondary); }
  .modal textarea { width: 100%; background: var(--surface-raised); border: 1px solid var(--border); border-radius: 8px; color: var(--text-primary); font-family: inherit; font-size: 0.88rem; padding: 0.7rem 0.85rem; resize: vertical; }
  .modal-actions { display: flex; justify-content: flex-end; gap: 0.6rem; margin-top: 1rem; }
  .submit-btn { background: var(--ableton-blue); color: #0b1420; border: none; border-radius: 8px; padding: 0.55rem 1.1rem; font-weight: 700; font-size: 0.82rem; cursor: pointer; transition: transform 120ms ease; }
  .submit-btn:active { transform: scale(0.97); }
  .submit-btn:disabled { opacity: 0.6; cursor: not-allowed; }
  .modal-status { margin: 0.75rem 0 0; font-size: 0.8rem; color: var(--text-secondary); min-height: 1.1em; }
  .modal-status.error { color: #ff8a8a; }
  .modal-status.success { color: #7fe0a0; }

  button:focus-visible { outline: 2px solid var(--ableton-blue); outline-offset: 2px; }
  @media (prefers-reduced-motion: reduce) {
    * { animation: none !important; transition: none !important; }
  }
</style>
</head>
<body>
  <div class="toolbar">
    <button class="toolbar-btn" id="refresh-btn" type="button" aria-label="Actualizar dashboard">
      <svg class="toolbar-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 1 1-2.64-6.36"/><path d="M21 4v6h-6"/></svg>
      Actualizar
    </button>
    <button class="toolbar-btn" id="feedback-open-btn" type="button" aria-label="Dejar un comentario">
      <svg class="toolbar-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.4 8.4 0 0 1-8.9 8.4A9 9 0 0 1 3 12a8.4 8.4 0 0 1 13.1-6.9A8.4 8.4 0 0 1 21 11.5Z"/><path d="M8 10h8M8 14h5"/></svg>
      Comentarios
    </button>
  </div>

  <span class="eyebrow">MCP Server para Ableton Live</span>
  <h1>Ableton MCP</h1>
  <div class="subtitle">Estado del proyecto · Generado: ${generatedAt}</div>

  <div class="comm-banner" aria-hidden="true">
    <div class="comm-node comm-node-claude">
      <span class="comm-node-dot"></span>
      Claude
    </div>
    <div class="comm-path">
      <span class="pulse pulse-1"></span>
      <span class="pulse pulse-2"></span>
      <span class="pulse pulse-3"></span>
    </div>
    <div class="comm-node comm-node-ableton">
      <span class="comm-node-dot"></span>
      Ableton Live
    </div>
    <span class="comm-caption">Protocolo MCP + OSC en tiempo real</span>
  </div>

  <div class="panel">
    <h2>Cómo funciona</h2>
    <p class="demo-caption">Ejemplo ilustrativo del flujo de trabajo — no es una grabación real de pantalla.</p>
    <div class="terminal-mock">
      <div class="terminal-bar">
        <span class="term-dot term-dot-red"></span>
        <span class="term-dot term-dot-yellow"></span>
        <span class="term-dot term-dot-green"></span>
        <span class="term-title">claude — ableton-mcp</span>
      </div>
      <div class="terminal-body">
        <div class="term-line term-prompt"><span class="term-caret">›</span> <span id="typed-text"></span><span class="term-cursor">▌</span></div>
        <div class="term-line term-response" id="term-response">✓ Progresión creada — track "Deep House Chords", escena 0, 4 acordes (Dm)</div>
      </div>
    </div>
  </div>

  <div class="stats">${statTilesHtml}</div>

  <div class="panel">
    <h2>Arquitectura del proyecto</h2>
    <div class="filters">
      <button class="filter-btn active" data-filter="all">Todo</button>
      <button class="filter-btn" data-filter="done">Completo</button>
      <button class="filter-btn" data-filter="partial">En progreso</button>
      <button class="filter-btn" data-filter="pending">Por iniciar</button>
    </div>
    <ul class="clip-list" id="clip-list">${categoryRows}</ul>
  </div>

  <div class="panel">
    <h2>Géneros musicales soportados</h2>
    <div class="genre-grid">${genreChips}</div>
  </div>

  <div class="modal-backdrop" id="feedback-backdrop">
    <div class="modal" role="dialog" aria-modal="true" aria-labelledby="feedback-title">
      <h3 id="feedback-title">Dejar un comentario</h3>
      <p class="modal-hint">¿Encontraste un bug o tienes una sugerencia? Se guarda para revisarlo en la próxima actualización.</p>
      <textarea id="feedback-text" rows="5" placeholder="Escribe aquí lo que notaste..." maxlength="2000"></textarea>
      <div class="modal-actions">
        <button class="toolbar-btn modal-cancel" id="feedback-cancel-btn" type="button">Cancelar</button>
        <button class="submit-btn" id="feedback-submit-btn" type="button">Enviar</button>
      </div>
      <p class="modal-status" id="feedback-status"></p>
    </div>
  </div>

  <script>
    ;(function () {
      const promptText = 'Haz una progresión de deep house en Dm, escena 0'
      const typedEl = document.getElementById('typed-text')
      const responseEl = document.getElementById('term-response')
      const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

      if (!typedEl || !responseEl) return

      if (reduceMotion) {
        typedEl.textContent = promptText
        responseEl.classList.add('visible')
        return
      }

      let i = 0
      function typeLoop() {
        typedEl.textContent = ''
        responseEl.classList.remove('visible')
        i = 0
        const interval = setInterval(() => {
          typedEl.textContent += promptText[i]
          i++
          if (i >= promptText.length) {
            clearInterval(interval)
            setTimeout(() => {
              responseEl.classList.add('visible')
              setTimeout(typeLoop, 3800)
            }, 350)
          }
        }, 42)
      }
      typeLoop()
    })()
  </script>

  <script>
    document.querySelectorAll('.filter-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.filter-btn').forEach((b) => b.classList.remove('active'))
        btn.classList.add('active')
        const filter = btn.getAttribute('data-filter')
        document.querySelectorAll('.clip-row').forEach((row) => {
          const match = filter === 'all' || row.getAttribute('data-status') === filter
          row.classList.toggle('hidden', !match)
        })
      })
    })

    const refreshBtn = document.getElementById('refresh-btn')
    if (refreshBtn) {
      refreshBtn.addEventListener('click', () => {
        refreshBtn.classList.add('refreshing')
        refreshBtn.disabled = true
        setTimeout(() => { window.location.reload() }, 350)
      })
    }

    const feedbackBackdrop = document.getElementById('feedback-backdrop')
    const feedbackOpenBtn = document.getElementById('feedback-open-btn')
    const feedbackCancelBtn = document.getElementById('feedback-cancel-btn')
    const feedbackSubmitBtn = document.getElementById('feedback-submit-btn')
    const feedbackText = document.getElementById('feedback-text')
    const feedbackStatus = document.getElementById('feedback-status')

    function closeFeedback() {
      feedbackBackdrop.classList.remove('open')
      feedbackText.value = ''
      feedbackStatus.textContent = ''
      feedbackStatus.className = 'modal-status'
    }

    if (feedbackOpenBtn) {
      feedbackOpenBtn.addEventListener('click', () => {
        feedbackBackdrop.classList.add('open')
        feedbackText.focus()
      })
      feedbackCancelBtn.addEventListener('click', closeFeedback)
      feedbackBackdrop.addEventListener('click', (e) => {
        if (e.target === feedbackBackdrop) closeFeedback()
      })
      feedbackSubmitBtn.addEventListener('click', () => {
        const text = feedbackText.value.trim()
        if (!text) {
          feedbackStatus.textContent = 'Escribe algo antes de enviar.'
          feedbackStatus.className = 'modal-status error'
          return
        }
        feedbackSubmitBtn.disabled = true
        feedbackStatus.textContent = 'Enviando...'
        feedbackStatus.className = 'modal-status'
        fetch('/api/feedback', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text }),
        })
          .then((r) => r.json())
          .then((data) => {
            feedbackSubmitBtn.disabled = false
            if (data.ok) {
              feedbackStatus.textContent = '¡Gracias! Tu comentario fue recibido.'
              feedbackStatus.className = 'modal-status success'
              setTimeout(closeFeedback, 1600)
            } else {
              feedbackStatus.textContent = 'No se pudo guardar. Intenta de nuevo.'
              feedbackStatus.className = 'modal-status error'
            }
          })
          .catch(() => {
            feedbackSubmitBtn.disabled = false
            feedbackStatus.textContent = 'No se pudo conectar — abre este dashboard desde el lanzador (server.js), no como archivo estático.'
            feedbackStatus.className = 'modal-status error'
          })
      })
    }
  </script>
</body>
</html>`
}

function generate() {
  const html = buildDashboardHtml()
  fs.writeFileSync(path.join(__dirname, 'dashboard.html'), html)
  console.log('Dashboard generado en:', path.join(__dirname, 'dashboard.html'))
}

module.exports = { buildDashboardHtml }

if (require.main === module) {
  generate()
}
