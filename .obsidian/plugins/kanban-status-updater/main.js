'use strict';

var obsidian = require('obsidian');

function __awaiter(thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
}

const DEFAULT_SETTINGS = {
    statusPropertyName: 'status',
    showNotifications: false,
    debugMode: false
};

class KanbanStatusUpdaterPlugin extends obsidian.Plugin {
    constructor() {
        super(...arguments);
        this._debounceTimer = null;
    }

    onload() {
        return __awaiter(this, void 0, void 0, function* () {
            yield this.loadSettings();
            if (this.settings.showNotifications) {
                new obsidian.Notice('Kanban Status Updater activated');
            }
            this.log('Plugin loaded — vault watcher mode');

            // 칸반 파일이 저장될 때마다 Q&A frontmatter 동기화
            this.registerEvent(this.app.vault.on('modify', (file) => {
                if (!(file instanceof obsidian.TFile)) return;
                if (!file.name.includes('칸반')) return;
                clearTimeout(this._debounceTimer);
                this._debounceTimer = setTimeout(() => {
                    this.syncFromKanban(file);
                }, 400);
            }));

            this.addSettingTab(new KanbanStatusUpdaterSettingTab(this.app, this));
        });
    }

    onunload() {
        clearTimeout(this._debounceTimer);
        this.log('Plugin unloaded');
    }

    // 칸반 파일을 파싱해서 카드 위치 → Q&A frontmatter 동기화
    syncFromKanban(file) {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                const content = yield this.app.vault.read(file);
                const laneMap = this.parseKanbanLanes(content);
                this.log(`Parsed ${Object.keys(laneMap).length} cards from ${file.name}`);

                for (const [stem, lane] of Object.entries(laneMap)) {
                    yield this.updateNoteStatus(stem, lane);
                }
            } catch (error) {
                this.log(`Error syncing from kanban: ${error.message}`);
            }
        });
    }

    // 칸반 마크다운 파싱 → {stem: lane}
    parseKanbanLanes(content) {
        const result = {};
        let currentLane = null;
        for (const line of content.split('\n')) {
            const laneMatch = line.match(/^## (.+)$/);
            if (laneMatch) {
                currentLane = laneMatch[1].trim();
                continue;
            }
            if (currentLane) {
                const cardMatch = line.match(/\[\[(.+?)(?:\|.+?)?\]\]/);
                if (cardMatch) {
                    result[cardMatch[1]] = currentLane;
                }
            }
        }
        return result;
    }

    updateNoteStatus(notePath, status) {
        return __awaiter(this, void 0, void 0, function* () {
            try {
                const file = this.app.metadataCache.getFirstLinkpathDest(notePath, '');
                if (!file) {
                    this.log(`Note not found: ${notePath}`);
                    return;
                }
                const metadata = this.app.metadataCache.getFileCache(file);
                const oldStatus = metadata?.frontmatter?.[this.settings.statusPropertyName] ?? null;

                if (oldStatus === status) {
                    this.log(`${file.basename}: status already "${status}", skipping`);
                    return;
                }

                yield this.app.fileManager.processFrontMatter(file, (fm) => {
                    fm[this.settings.statusPropertyName] = status;
                });

                if (this.settings.showNotifications) {
                    new obsidian.Notice(`${file.basename}: "${oldStatus}" → "${status}"`, 3000);
                }
                this.log(`${file.basename}: "${oldStatus}" → "${status}"`);
            } catch (error) {
                this.log(`Error updating ${notePath}: ${error.message}`);
            }
        });
    }

    log(message) {
        if (this.settings.debugMode) {
            console.log(`[KSU] ${message}`);
        }
    }

    loadSettings() {
        return __awaiter(this, void 0, void 0, function* () {
            this.settings = Object.assign({}, DEFAULT_SETTINGS, yield this.loadData());
        });
    }

    saveSettings() {
        return __awaiter(this, void 0, void 0, function* () {
            yield this.saveData(this.settings);
        });
    }
}

class KanbanStatusUpdaterSettingTab extends obsidian.PluginSettingTab {
    constructor(app, plugin) {
        super(app, plugin);
        this.plugin = plugin;
    }
    display() {
        const { containerEl } = this;
        containerEl.empty();
        new obsidian.Setting(containerEl)
            .setName('Status property name')
            .setDesc('The name of the property to update when a card is moved')
            .addText(text => text
                .setPlaceholder('status')
                .setValue(this.plugin.settings.statusPropertyName)
                .onChange((value) => __awaiter(this, void 0, void 0, function* () {
                    this.plugin.settings.statusPropertyName = value;
                    yield this.plugin.saveSettings();
                })));
        new obsidian.Setting(containerEl)
            .setName('Show notifications')
            .setDesc('Show a notification when a status is updated')
            .addToggle(toggle => toggle
                .setValue(this.plugin.settings.showNotifications)
                .onChange((value) => __awaiter(this, void 0, void 0, function* () {
                    this.plugin.settings.showNotifications = value;
                    yield this.plugin.saveSettings();
                })));
        new obsidian.Setting(containerEl)
            .setName('Debug mode')
            .setDesc('Enable detailed logging')
            .addToggle(toggle => toggle
                .setValue(this.plugin.settings.debugMode)
                .onChange((value) => __awaiter(this, void 0, void 0, function* () {
                    this.plugin.settings.debugMode = value;
                    yield this.plugin.saveSettings();
                })));
    }
}

module.exports = KanbanStatusUpdaterPlugin;
