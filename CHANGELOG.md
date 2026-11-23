# Changelog

Versions match the [sdlc-pipeline](https://github.com/nithinemvigo/sdlc-pipeline) release each
one is synced with (see [`UPSTREAM.md`](UPSTREAM.md)). Changes made only in this Flutter edition
are listed as Flutter revisions under that release.

## 3.4.1

### Flutter revision 2 — #2

Rebuilt the pipeline Flutter-native. Every agent and command now works in Flutter terms from
the start, instead of web instructions with Flutter notes attached.

- Preflight requires the Flutter SDK and a stack profile; repos without `pubspec.yaml` are
  refused.
- The stack profile travels with every dispatch, replacing the per-stage "if Flutter" notes.
- Agents rewritten for Flutter: Dart-level plans and tests, codegen/platform/migration
  checks, theme-based design review, device QA, OWASP MASVS security review, profile-mode
  performance, per-platform compile before ship.
- Reviewers may read source in short windows to verify the plan's claims about existing code.

### Flutter revision 1 — #1

Ported sdlc-pipeline 3.4.1 (requirements-first `/pipeline-all`, BA requirements analysis,
acceptance gate) with Flutter notes added to each stage.
