import { createServer } from 'node:http';
import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import { mkdir, readdir, readFile, rename, stat } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const APP_DIR = path.dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = path.resolve(APP_DIR, '..');
const SKILLS_DIR = path.join(REPO_ROOT, 'skills');
const PUBLIC_DIR = path.join(APP_DIR, 'public');

const MIME = new Map([
  ['.html', 'text/html; charset=utf-8'],
  ['.css', 'text/css; charset=utf-8'],
  ['.js', 'text/javascript; charset=utf-8'],
  ['.json', 'application/json; charset=utf-8'],
  ['.svg', 'image/svg+xml'],
  ['.png', 'image/png'],
]);

function sendJson(res, status, payload) {
  const body = JSON.stringify(payload);
  res.writeHead(status, {
    'content-type': 'application/json; charset=utf-8',
    'content-length': Buffer.byteLength(body),
  });
  res.end(body);
}

function sendError(res, status, message) {
  sendJson(res, status, { error: message });
}

async function readBody(req) {
  const chunks = [];
  let size = 0;
  for await (const chunk of req) {
    size += chunk.length;
    if (size > 1024 * 1024) {
      throw new Error('request body too large');
    }
    chunks.push(chunk);
  }
  if (chunks.length === 0) return {};
  return JSON.parse(Buffer.concat(chunks).toString('utf8'));
}

function normalizeRelPath(value, { allowEmpty = false } = {}) {
  if (typeof value !== 'string') {
    throw new Error('path must be a string');
  }

  const raw = value.trim().replaceAll('\\', '/');
  if (!raw) {
    if (allowEmpty) return '';
    throw new Error('path is required');
  }
  if (raw.startsWith('/') || raw.includes('\0')) {
    throw new Error('absolute or invalid paths are not allowed');
  }

  const parts = raw.split('/').filter(Boolean);
  if (parts.some((part) => part === '.' || part === '..')) {
    throw new Error('path traversal is not allowed');
  }

  return parts.join('/');
}

function safeJoin(root, relPath) {
  const resolved = path.resolve(root, relPath);
  const relative = path.relative(root, resolved);
  if (relative.startsWith('..') || path.isAbsolute(relative)) {
    throw new Error('path escapes skills directory');
  }
  return resolved;
}

function parseFrontmatter(markdown) {
  const match = markdown.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!match) return {};

  const frontmatter = match[1];
  const name = frontmatter.match(/^name:\s*["']?([^"'\n]+)["']?\s*$/m)?.[1]?.trim();
  const inlineDescription = frontmatter.match(/^description:\s*["']?([^"'\n]+)["']?\s*$/m)?.[1]?.trim();
  let description = inlineDescription && !['|', '>', '|-', '>-'].includes(inlineDescription)
    ? inlineDescription
    : '';

  if (!description) {
    const block = frontmatter.match(/^description:\s*[>|][-+]?\s*\r?\n((?:[ \t]+.+\r?\n?)+)/m)?.[1];
    if (block) {
      description = block
        .split(/\r?\n/)
        .map((line) => line.trim())
        .filter(Boolean)
        .join(' ')
        .trim();
    }
  }

  return { name, description };
}

async function findSkills(dir = SKILLS_DIR, rel = '') {
  const entries = await readdir(dir, { withFileTypes: true });
  const hasSkill = entries.some((entry) => entry.isFile() && entry.name === 'SKILL.md');

  if (hasSkill) {
    const skillMd = path.join(dir, 'SKILL.md');
    const content = await readFile(skillMd, 'utf8');
    const meta = parseFrontmatter(content);
    const relPath = rel.replaceAll(path.sep, '/');
    const category = path.posix.dirname(relPath) === '.' ? '' : path.posix.dirname(relPath);
    const dirName = path.posix.basename(relPath);
    return [{
      relPath,
      category,
      folderName: dirName,
      name: meta.name || dirName,
      description: meta.description || '',
    }];
  }

  const skills = [];
  for (const entry of entries) {
    if (!entry.isDirectory()) continue;
    if (entry.name === '.git' || entry.name === 'node_modules' || entry.name === 'output') continue;
    const childRel = rel ? path.posix.join(rel, entry.name) : entry.name;
    skills.push(...await findSkills(path.join(dir, entry.name), childRel));
  }
  return skills;
}

function categoriesFromSkills(skills) {
  const categories = new Map();
  categories.set('', { path: '', label: '(root)', count: 0 });

  for (const skill of skills) {
    const pathParts = skill.category ? skill.category.split('/') : [''];
    let current = '';
    for (const part of pathParts) {
      current = current ? `${current}/${part}` : part;
      if (!categories.has(current)) {
        categories.set(current, { path: current, label: part || '(root)', count: 0 });
      }
    }
    const item = categories.get(skill.category || '');
    item.count += 1;
  }

  return [...categories.values()].sort((a, b) => {
    if (a.path === '') return -1;
    if (b.path === '') return 1;
    return a.path.localeCompare(b.path);
  });
}

async function listPayload() {
  const skills = (await findSkills()).sort((a, b) =>
    a.category.localeCompare(b.category) || a.name.localeCompare(b.name)
  );
  return {
    root: REPO_ROOT,
    skillsDir: SKILLS_DIR,
    skills,
    categories: categoriesFromSkills(skills),
  };
}

function runCommand(command, args, { timeoutMs = 120000 } = {}) {
  return new Promise((resolve) => {
    const child = spawn(command, args, { cwd: REPO_ROOT, env: process.env });
    const stdout = [];
    const stderr = [];
    const timer = setTimeout(() => {
      child.kill('SIGTERM');
    }, timeoutMs);

    child.stdout.on('data', (chunk) => stdout.push(chunk));
    child.stderr.on('data', (chunk) => stderr.push(chunk));
    child.on('error', (error) => {
      clearTimeout(timer);
      resolve({ code: -1, stdout: '', stderr: error.message });
    });
    child.on('close', (code) => {
      clearTimeout(timer);
      resolve({
        code,
        stdout: Buffer.concat(stdout).toString('utf8'),
        stderr: Buffer.concat(stderr).toString('utf8'),
      });
    });
  });
}

async function handleApi(req, res, url) {
  try {
    if (req.method === 'GET' && url.pathname === '/api/skills') {
      sendJson(res, 200, await listPayload());
      return;
    }

    if (req.method === 'POST' && url.pathname === '/api/folders') {
      const body = await readBody(req);
      const folder = normalizeRelPath(body.folder);
      const target = safeJoin(SKILLS_DIR, folder);
      await mkdir(target, { recursive: true });
      sendJson(res, 200, { ok: true, folder, ...(await listPayload()) });
      return;
    }

    if (req.method === 'POST' && url.pathname === '/api/move') {
      const body = await readBody(req);
      const skillPath = normalizeRelPath(body.skillPath);
      const targetFolder = normalizeRelPath(body.targetFolder ?? '', { allowEmpty: true });
      const source = safeJoin(SKILLS_DIR, skillPath);
      const sourceSkill = path.join(source, 'SKILL.md');
      if (!existsSync(sourceSkill)) {
        sendError(res, 404, 'source skill was not found');
        return;
      }

      const skillDirName = path.basename(source);
      const targetParent = safeJoin(SKILLS_DIR, targetFolder);
      const target = path.join(targetParent, skillDirName);
      safeJoin(SKILLS_DIR, path.relative(SKILLS_DIR, target));

      if (path.resolve(source) !== path.resolve(target)) {
        if (existsSync(target)) {
          sendError(res, 409, `destination already exists: ${path.relative(SKILLS_DIR, target)}`);
          return;
        }
        await mkdir(targetParent, { recursive: true });
        await rename(source, target);
      }

      sendJson(res, 200, {
        ok: true,
        from: skillPath,
        to: path.relative(SKILLS_DIR, target).replaceAll(path.sep, '/'),
        ...(await listPayload()),
      });
      return;
    }

    if (req.method === 'POST' && url.pathname === '/api/sync') {
      const sync = await runCommand('skillshare', ['sync', '--force']);
      const diff = await runCommand('skillshare', ['diff', '--json']);
      sendJson(res, sync.code === 0 ? 200 : 500, { sync, diff });
      return;
    }

    if (req.method === 'GET' && url.pathname === '/api/status') {
      const git = await runCommand('git', ['status', '--short', '--branch'], { timeoutMs: 20000 });
      const diff = await runCommand('skillshare', ['diff', '--json'], { timeoutMs: 60000 });
      sendJson(res, 200, { git, diff });
      return;
    }

    sendError(res, 404, 'not found');
  } catch (error) {
    sendError(res, 400, error.message || 'request failed');
  }
}

async function serveStatic(req, res, url) {
  const requested = url.pathname === '/' ? '/index.html' : url.pathname;
  const rel = normalizeRelPath(decodeURIComponent(requested).replace(/^\/+/, ''), { allowEmpty: true });
  const target = safeJoin(PUBLIC_DIR, rel || 'index.html');
  const info = await stat(target).catch(() => null);
  if (!info || !info.isFile()) {
    sendError(res, 404, 'not found');
    return;
  }
  const body = await readFile(target);
  res.writeHead(200, {
    'content-type': MIME.get(path.extname(target)) || 'application/octet-stream',
    'content-length': body.length,
  });
  res.end(body);
}

function parsePort() {
  const idx = process.argv.indexOf('--port');
  if (idx >= 0 && process.argv[idx + 1]) {
    return Number(process.argv[idx + 1]);
  }
  return Number(process.env.PORT || 19431);
}

const port = parsePort();
const host = process.env.HOST || '127.0.0.1';

createServer(async (req, res) => {
  const url = new URL(req.url, `http://${req.headers.host || `${host}:${port}`}`);
  if (url.pathname.startsWith('/api/')) {
    await handleApi(req, res, url);
    return;
  }
  await serveStatic(req, res, url);
}).listen(port, host, () => {
  console.log(`Skill Hub Manager running at http://${host}:${port}`);
  console.log(`Managing ${SKILLS_DIR}`);
});
