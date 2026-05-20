<%*
const vaultPath = app.vault.adapter.basePath;
try {
  await tp.system.exec_command(`git -C "${vaultPath}" config core.hooksPath .githooks`);
} catch(e) {}
%>