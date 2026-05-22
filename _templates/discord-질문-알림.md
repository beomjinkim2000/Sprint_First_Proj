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

let inQ = false;
const qLines = [];
for (const line of lines) {
  if (line.includes('white-space:nowrap">질문<')) { inQ = true; continue; }
  if (inQ && line.includes('white-space:nowrap">')) break;
  if (inQ) {
    const s = line.trim();
    if (s && !s.startsWith('> [!') && s !== '>') {
      const clean = s.startsWith('> ') ? s.slice(2) : s;
      if (clean) qLines.push(clean);
    }
  }
}

const title = tfile.name.replace(/^\[Q&A\]-/, '').replace(/\.md$/, '');
const text = qLines.join(' ');
const preview = text.length > 1500 ? text.slice(0, 1500) + '...' : text;

let msg = `❓ **새 질문이 등록됐어요!** 아는 분 답변 부탁드립니다 🙏\n> **제목:** ${title}`;
if (preview) msg += `\n> **질문:** ${preview}`;

try {
  const res = await fetch(WEBHOOK, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content: msg })
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  new Notice("✅ Discord에 질문 알림을 보냈습니다!");
} catch(e) {
  new Notice("❌ 전송 실패: " + String(e));
}

if (tempFile) await app.vault.delete(tempFile);
_%>
