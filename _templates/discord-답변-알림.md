<%*
const WEBHOOK = "https://discord.com/api/webhooks/1493432111548465244/33ebLhZEHh6FX3PRJBcP8T1MvkuxUoSTJtzruBTpSBeWYc8LCgXfTmHtznAuqmsarrOv";

let tfile = app.workspace.getActiveFile();
const tempFile = (tfile && !tfile.name.startsWith('[Q&A]')) ? tfile : null;

if (!tfile || !tfile.name.startsWith('[Q&A]')) {
  tfile = null;
  app.workspace.iterateAllLeaves(leaf => {
    if (!tfile && leaf.view?.file?.name.startsWith('[Q&A]')) {
      tfile = leaf.view.file;
    }
  });
}

if (!tfile) {
  new Notice("⚠️ 열려있는 Q&A 파일을 찾을 수 없습니다.");
  if (tempFile) await app.vault.delete(tempFile);
  return;
}

const content = await app.vault.read(tfile);
const lines = content.split('\n');

let inSec = false;
let curAuthor = null;
let curLines = [];
const callouts = [];

for (const line of lines) {
  if (line.includes('white-space:nowrap">답변<')) {
    if (curAuthor !== null) { callouts.push([curAuthor, curLines.join(' ')]); curAuthor = null; curLines = []; }
    inSec = true; continue;
  }

  if (inSec && line.includes('white-space:nowrap">')) {
    if (curAuthor !== null) { callouts.push([curAuthor, curLines.join(' ')]); curAuthor = null; curLines = []; }
    inSec = false; continue;
  }

  if (!inSec) continue;

  const m = line.match(/^>\s*\[!note\]\s*(.+)/);
  if (m) {
    if (curAuthor !== null) callouts.push([curAuthor, curLines.join(' ')]);
    curAuthor = m[1].trim(); curLines = [];
  } else if (curAuthor !== null && line.startsWith('>')) {
    const text = line.slice(1).trim();
    if (text) curLines.push(text);
  }
}
if (curAuthor !== null) callouts.push([curAuthor, curLines.join(' ')]);

if (callouts.length === 0) {
  new Notice("⚠️ 답변/댓글에 [!note] 블록이 없습니다.");
  if (tempFile) await app.vault.delete(tempFile);
  return;
}

const [author, answerText] = callouts[callouts.length - 1];
const title = tfile.name.replace(/^\[Q&A\]-/, '').replace(/\.md$/, '');
const preview = answerText.length > 1500 ? answerText.slice(0, 1500) + '...' : answerText;

let msg = `💬 **${author}님이 답변을 등록했습니다!**\n> **제목:** ${title}`;
if (preview) msg += `\n> **내용:** ${preview}`;

try {
  const res = await fetch(WEBHOOK, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content: msg })
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  new Notice("✅ Discord에 답변 알림을 보냈습니다!");
} catch(e) {
  new Notice("❌ 전송 실패: " + String(e));
}

if (tempFile) await app.vault.delete(tempFile);
_%>
