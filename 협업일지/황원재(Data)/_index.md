---
title: "협업일지 — 황원재(Data)"
tags: [협업일지]
---

# 협업일지 — 황원재(Data)

```dataview
TABLE file.link as "파일", file.mtime as "날짜"
FROM "협업일지/황원재(Data)"
WHERE file.name != "_index"
SORT file.name DESC
```
