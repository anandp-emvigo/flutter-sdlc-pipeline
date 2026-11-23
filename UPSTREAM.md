# Upstream sync

This plugin is the Flutter edition of [sdlc-pipeline](https://github.com/nithinemvigo/sdlc-pipeline).
Its version number always equals the sdlc-pipeline release it is synced with. Flutter-only
changes never bump the version; they are recorded in [`CHANGELOG.md`](CHANGELOG.md) as Flutter
revisions of that release.

## Current sync point

| sdlc-pipeline version | Upstream commit | Synced on |
|---|---|---|
| 3.4.1 | `d7753fe` | 2026-11-23 |

## Syncing a new upstream release

1. Diff the new upstream release against the commit above and port each change, keeping
   every agent and command Flutter-native (no web instructions, no "if Flutter" branches).
2. Set the version to the upstream version in `.claude-plugin/plugin.json`,
   `.claude-plugin/marketplace.json` and `.cursor-plugin/plugin.json`.
3. Add a row to the table above (newest first) and a new release section to `CHANGELOG.md`.
