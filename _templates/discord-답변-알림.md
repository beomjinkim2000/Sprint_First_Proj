<%*
const vaultPath = app.vault.adapter.basePath;
const filePath = `${vaultPath}/${tp.file.path(true)}`;
const script = `${vaultPath}/.githooks/discord_notify.py`;

if (!tp.file.title.startsWith('[Q&A]')) {
  new Notice("⚠️ Q&A 파일에서만 실행할 수 있습니다.");
  return;
}

try {
  await tp.system.exec_command(`python3 '${script}' answer '${filePath}'`);
  new Notice("✅ Discord에 답변 알림을 보냈습니다!");
} catch(e) {
  new Notice("❌ 전송 실패: " + String(e));
}
_%>
