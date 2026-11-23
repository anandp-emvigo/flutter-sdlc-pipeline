# Preflight failure report template

The orchestrator reads this file **only** when Stage -1 halts. Keeping it out of
`pipeline.md` removes ~1,400 tokens from every orchestrator turn of every successful run,
at the cost of one `Read` in the rare failure case.

Emit exactly this, filled in. Show "How to fix" entries **only** for dependencies that
are not ✅.

---

## 🚦 /pipeline preflight — cannot start

| Dependency | Status | Provides |
|---|---|---|
| superpowers | ✅ Ready / ❌ Missing / ⚠️ Installed but disabled | Planning, TDD & execution discipline |
| gstack | ✅ Ready / ❌ Missing / ⚠️ Installed but disabled | `/office-hours`, `/spec`, `/ship` |
| claude-mem | ✅ Ready / ❌ Missing / ⚠️ Installed but disabled | Persistent memory across sessions |
| Flutter SDK | ✅ Ready / ❌ Not on `PATH` / ⚠️ Pinned version not installed | `flutter` / `dart` for build, test, QA and ship |

**How to fix** *(only the items above that aren't ✅)*

❌ Missing → install it:

- **superpowers**
  ```
  /plugin marketplace add obra/superpowers-marketplace
  /plugin install superpowers@superpowers-marketplace
  ```
- **gstack** *(installs via git, not the plugin marketplace)*
  ```
  git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git ~/.claude/skills/gstack
  cd ~/.claude/skills/gstack && ./setup
  ```
- **claude-mem**
  ```
  /plugin marketplace add thedotmack/claude-mem
  /plugin install claude-mem
  ```

- **Flutter SDK** — install from [docs.flutter.dev/get-started/install](https://docs.flutter.dev/get-started/install)
  and make sure `flutter --version` works in this shell. Run `flutter doctor` to diagnose.
  If the repo pins a version with FVM (`.fvmrc`): `fvm install` in the repo root.

⚠️ Installed but disabled → enable it: `/plugin` (CLI) or **Customize → Plugins**
(Cowork/Desktop), toggle it on.

Then **restart your session** and run `/pipeline` again — plugin changes only take effect
in a fresh session.
