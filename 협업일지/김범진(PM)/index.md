---
title: "협업일지 — 김범진(PM)"
tags: [협업일지]
---

# 협업일지 — 김범진(PM)

```dataviewjs
// @prerender from="협업일지/김범진(PM)" list
const pages = dv.pages('"협업일지/김범진(PM)"')
  .where(p => p.file.name !== "index")
  .sort(p => p.file.name, 'desc');
dv.table(["파일", "날짜"], pages.map(p => [
  dv.fileLink(p.file.path, false, p.file.name),
  p.file.name.slice(0, 10)
]));
```
