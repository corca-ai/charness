#!/usr/bin/env node
/**
 * Vendored Slack API wrapper for fetching thread messages.
 * Usage: node slack-api.mjs <channel_id> <thread_ts> [--attachments-dir <path>]
 * Outputs JSON to stdout: { messages: [...], users: [...] }
 *
 * This file is adapted from a reference implementation in
 * corca-ai/claude-plugins. charness owns the runtime surface shipped here.
 */

import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const SKILL_DIR = join(__dirname, '..');
const CACHE_DIR = join(SKILL_DIR, '.cache');
const CACHE_FILE = join(CACHE_DIR, 'users.json');

function loadToken() {
  if (process.env.SLACK_BOT_TOKEN) {
    return process.env.SLACK_BOT_TOKEN;
  }
  throw new Error(
    'SLACK_BOT_TOKEN not found in the process environment. Provide a runtime grant or env fallback.'
  );
}

function loadUserCache() {
  if (existsSync(CACHE_FILE)) {
    try {
      return JSON.parse(readFileSync(CACHE_FILE, 'utf-8'));
    } catch {
      return {};
    }
  }
  return {};
}

function saveUserCache(cache) {
  if (!existsSync(CACHE_DIR)) {
    mkdirSync(CACHE_DIR, { recursive: true });
  }
  writeFileSync(CACHE_FILE, JSON.stringify(cache, null, 2));
}

async function slackApi(endpoint, token, options = {}) {
  const baseUrl = 'https://slack.com/api/';
  const method = options.method || 'GET';
  const headers = {
    Authorization: `Bearer ${token}`,
    'Content-Type': 'application/json',
  };

  let url = baseUrl + endpoint;
  const fetchOptions = { method, headers };

  if (method === 'GET' && options.params) {
    const searchParams = new URLSearchParams(options.params);
    url += '?' + searchParams.toString();
  } else if (method === 'POST' && options.body) {
    fetchOptions.body = JSON.stringify(options.body);
  }

  const response = await fetch(url, fetchOptions);
  const data = await response.json();

  if (!data.ok) {
    const error = new Error(data.error || 'Slack API error');
    error.slackError = data.error;
    error.needed = data.needed;
    throw error;
  }

  return data;
}

async function fetchThread(channelId, threadTs, token) {
  try {
    const data = await slackApi('conversations.replies', token, {
      params: {
        channel: channelId,
        ts: threadTs,
        limit: 100,
      },
    });
    return data.messages || [];
  } catch (error) {
    if (error.slackError === 'not_in_channel') {
      console.error('Bot not in channel, attempting to join...');
      await joinChannel(channelId, token);
      const data = await slackApi('conversations.replies', token, {
        params: {
          channel: channelId,
          ts: threadTs,
          limit: 100,
        },
      });
      return data.messages || [];
    }
    throw error;
  }
}

async function joinChannel(channelId, token) {
  try {
    await slackApi('conversations.join', token, {
      method: 'POST',
      body: { channel: channelId },
    });
    console.error('Successfully joined channel');
  } catch (error) {
    if (error.slackError === 'missing_scope') {
      const requiredScope = error.needed || 'channels:join';
      throw new Error(
        `Error: missing_scope\nRequired scope: ${requiredScope}\n` +
          'Please add this scope to your Slack app at https://api.slack.com/apps'
      );
    }
    throw error;
  }
}

async function fetchUserInfo(userId, token) {
  const data = await slackApi('users.info', token, {
    params: { user: userId },
  });
  return data.user?.real_name || data.user?.name || userId;
}

async function resolveUsers(userIds, token, cache) {
  const users = [];
  let cacheUpdated = false;

  for (const userId of userIds) {
    if (!userId) continue;

    let realName = cache[userId];
    if (!realName) {
      try {
        realName = await fetchUserInfo(userId, token);
        cache[userId] = realName;
        cacheUpdated = true;
      } catch (error) {
        console.error(`Failed to fetch user ${userId}: ${error.message}`);
        realName = userId;
      }
    }
    users.push({ id: userId, real_name: realName });
  }

  if (cacheUpdated) {
    saveUserCache(cache);
  }

  return users;
}

async function downloadFile(file, token, attachmentsDir, usedNames) {
  const url = file.url_private_download;
  if (!url) return null;

  let localName = file.name;
  if (usedNames.has(localName)) {
    const dotIdx = localName.lastIndexOf('.');
    const base = dotIdx > 0 ? localName.slice(0, dotIdx) : localName;
    const ext = dotIdx > 0 ? localName.slice(dotIdx) : '';
    let n = 2;
    while (usedNames.has(`${base}_${n}${ext}`)) n++;
    localName = `${base}_${n}${ext}`;
  }
  usedNames.add(localName);

  const localPath = join(attachmentsDir, localName);
  if (existsSync(localPath)) {
    console.error(`Skipping (already exists): ${file.name}`);
    return localName;
  }

  const response = await fetch(url, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (!response.ok) {
    console.error(`Failed to download ${file.name}: HTTP ${response.status}`);
    return null;
  }

  const buffer = Buffer.from(await response.arrayBuffer());
  writeFileSync(localPath, buffer);
  console.error(`Downloaded: ${file.name} (${buffer.length} bytes)`);
  return localName;
}

async function downloadFiles(messages, token, attachmentsDir) {
  if (!attachmentsDir) return;

  mkdirSync(attachmentsDir, { recursive: true });
  const usedNames = new Set();

  for (const msg of messages) {
    if (!msg.files || msg.files.length === 0) continue;

    for (const file of msg.files) {
      const localName = await downloadFile(file, token, attachmentsDir, usedNames);
      if (localName) {
        file.local_path = localName;
      }
    }
  }
}

async function main() {
  const args = process.argv.slice(2);
  const channelId = args[0];
  const threadTs = args[1];

  let attachmentsDir = null;
  const attachIdx = args.indexOf('--attachments-dir');
  if (attachIdx !== -1 && args[attachIdx + 1]) {
    attachmentsDir = args[attachIdx + 1];
  }

  if (!channelId || !threadTs) {
    console.error(
      'Usage: node slack-api.mjs <channel_id> <thread_ts> [--attachments-dir <path>]'
    );
    process.exit(1);
  }

  const token = loadToken();
  const cache = loadUserCache();
  const messages = await fetchThread(channelId, threadTs, token);

  await downloadFiles(messages, token, attachmentsDir);
  const userIds = [...new Set(messages.map((message) => message.user).filter(Boolean))];
  const users = await resolveUsers(userIds, token, cache);
  console.log(JSON.stringify({ messages, users }));
}

main().catch((error) => {
  if (error.slackError === 'missing_scope') {
    const requiredScope = error.needed || 'unknown';
    console.error(
      `Error: missing_scope\nRequired scope: ${requiredScope}\n` +
        'Please add this scope to your Slack app at https://api.slack.com/apps'
    );
  } else {
    console.error(error.message);
  }
  process.exit(1);
});
