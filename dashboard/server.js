#!/usr/bin/env node
const http = require('http')
const fs = require('fs')
const path = require('path')
const { buildDashboardHtml } = require('./generate.js')

const PORT = 4757
const FEEDBACK_FILE = path.join(__dirname, 'feedback.md')
const MAX_COMMENT_LENGTH = 2000

function readBody(req) {
  return new Promise((resolve, reject) => {
    let data = ''
    let size = 0
    req.on('data', (chunk) => {
      size += chunk.length
      if (size > 20000) {
        reject(new Error('payload too large'))
        req.destroy()
        return
      }
      data += chunk
    })
    req.on('end', () => resolve(data))
    req.on('error', reject)
  })
}

function appendFeedback(text) {
  const safeText = String(text).trim().slice(0, MAX_COMMENT_LENGTH)
  if (!safeText) return false
  const timestamp = new Date().toISOString().replace('T', ' ').slice(0, 19)
  const entry = `\n### ${timestamp}\n\n${safeText}\n`
  if (!fs.existsSync(FEEDBACK_FILE)) {
    fs.writeFileSync(FEEDBACK_FILE, '# Feedback recibido — Ableton MCP Dashboard\n\nNotas y bugs reportados desde el dashboard, para revisar en próximas sesiones.\n')
  }
  fs.appendFileSync(FEEDBACK_FILE, entry)
  return true
}

const server = http.createServer(async (req, res) => {
  try {
    if (req.method === 'POST' && req.url === '/api/feedback') {
      const body = await readBody(req)
      let parsed
      try {
        parsed = JSON.parse(body)
      } catch {
        res.writeHead(400, { 'Content-Type': 'application/json' })
        res.end(JSON.stringify({ ok: false, error: 'JSON inválido' }))
        return
      }
      const ok = appendFeedback(parsed.text || '')
      res.writeHead(ok ? 200 : 400, { 'Content-Type': 'application/json' })
      res.end(JSON.stringify({ ok }))
      return
    }

    const html = buildDashboardHtml()
    res.writeHead(200, {
      'Content-Type': 'text/html; charset=utf-8',
      'Cache-Control': 'no-store, no-cache, must-revalidate',
      Pragma: 'no-cache',
    })
    res.end(html)
  } catch (err) {
    res.writeHead(500, { 'Content-Type': 'text/plain; charset=utf-8' })
    res.end('Error: ' + err.message)
  }
})

server.listen(PORT, () => {
  console.log(`Ableton MCP dashboard disponible en http://localhost:${PORT}/`)
})
