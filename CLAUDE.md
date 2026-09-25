# CLAUDE.md — UFO 50 Full (Archipelago world + game mod)

This repo is a full Archipelago checkout whose **only local work** is the world in
`worlds/ufo50_full/` (the "UFO 50 Full" apworld). Everything else is stock Archipelago —
don't touch it. There is a **separate, companion repo** for the in-game mod (see
["The game mod"](#the-game-mod) below); the two are developed together and must agree on
every id.

- apworld repo: `github.com/morraconda/ufo50-apworld-full`, branch `main`.
- mod repo: sibling directory `../ufo50-ap-mod/` (not a git repo here).
- YAML generator repo: sibling directory `../ufo50-ap-yaml-generator/`
  (`github.com/morraconda/ufo50-ap-yaml-generator`) — see ["The YAML generator"](#the-yaml-generator).
- AP game name: **`UFO 50 Full`**. `required_client_version = (0, 5, 0)`.

UFO 50 is a 50-game retro collection. This world randomizes all 50 games at once: each
game is a mini-world with its own items, locations, regions and logic, unlocked by
finding its **Cartridge**.

---

## `worlds/ufo50_full/` layout

| file | role |
|---|---|
| `__init__.py` | `UFO50World`, the `ufo50_games` registry, item-pool/region assembly, filler + traps |
| `constants.py` | `BASE_ID`, `game_ids` (name → 1..50, **in-game menu order**), `get_game_base_id` |
| `game_ids.py` | same map sorted by id, plus `id_to_name` — reference only |
| `options.py` | `UFO50Options` dataclass + `ufo50_option_groups` |
| `general_items.py` | `cartridge_items`, `trap_items`, the meta id block (`META_BASE_ID`) |
| `goal_locations.py` | shared Gift/Gold/Cherry location handling; goal = **Gold** |
| `game_helpers.py` | boilerplate every per-game module delegates to (`level_id`, `get_items`, `build_regions`, …) |
| `games/<game>/` | one package per game: `items.py`, `locations.py`, `rules.py`, `regions.py` |
| `test/` | plain `unittest` generation tests (no pytest in this tree) |
| `docs/` | player-facing setup + game docs |

### ID math (must match the mod exactly)

```
BASE_ID = 2106155000000        # 21061550_00_000
ap_id            = BASE_ID + subgame*1000 + offset
subgame          = (ap_id - BASE_ID) // 1000
item/location id = (ap_id - BASE_ID)  % 1000
```

- **subgame 1..50** = the games, `subgame == game_ids[name]`. Offsets `1..996` are the
  game's own items/locations; `997/998/999` are its Gift/Gold/Cherry goal locations;
  `0..9` are reserved for game-wide items. `game_helpers.level_id(level, slot)` gives
  `level*10 + slot` for level-structured games.
- **subgame 0** = "Main Menu" namespace. The **Cartridge items live here**: `<Game> Cartridge`
  has id `BASE_ID + game_num`, i.e. subgame 0 / item_id `1..50`.
- **subgame 51** = reserved **meta namespace** for cross-game items (traps, future stuff).
  `META_BASE_ID = BASE_ID + 51000`. `Controls Swap Trap` = `META_BASE_ID + 1`.
- `Intentional Nothing Filler Item` = `BASE_ID - 100` (negative offset → the mod ignores
  it); only used when a slot has zero real games.

### The per-game module contract

`UFO50World` calls these **by name** on `ufo50_games[name].{items,locations,regions}`, so
each game keeps thin wrappers with these exact signatures and delegates mechanics to
`game_helpers` / `goal_locations`:

- `items.py`: `get_items()`, `get_item_groups()`, `create_item(name, world, cls=None)`,
  `create_items(world) -> list[Item]`, `get_filler_item_name(world)`.
- `locations.py`: `get_locations()`, `get_location_groups()`,
  `create_locations(world, regions)`. Its `location_table` **must** end with
  `Gift` / `Gold` / `Cherry`, routed through `goal_locations` (aliased
  `is_completion_event_location` / `place_completion_event`).
- `regions.py`: `create_regions_and_rules(world) -> dict[str, Region]`, usually just
  `build_regions(world, GAME_NAME, [...region names...], create_locations, create_rules)`.
  Region objects are titled `"<Game> - <region>"`; every game has a `"<Game> - Menu"`
  that `UFO50World` connects from the hub `Menu` via `Boot <Game>` (gated on the Cartridge).

### Goal / progression model

- Every game listed in the `games` option is **both enabled and a goal**. Goal = reach
  that game's **`<Game> - Gold`** location. There is no Cherry goal; the client treats a
  Cherry as also satisfying Gold.
- A goal game's `Gold` is a real sendable location carrying a **locked filler item**
  (must survive reconnects); `Completed All Games` (the `Victory` event in `Menu`) is
  gated on `can_reach_location` of every goal game's Gold.
- **Sphere-1 deferral** (`defer_sphere_1_games`, on by default; option display name
  "Defer No Logic Games"): games whose every check is reachable at boot
  (`_game_is_sphere1_only`): fill gates their `Boot <Game>` entrance behind holding
  all three `Artificial Logic Gate 1/2/3` items (`general_items.logic_gate_items`,
  subgame-51 ids), so critical-path items can't land on a game that's fully open at
  boot. **Generator-only** — the gates are never sent to the mod and lock nothing
  in-game (you boot any game whose Cartridge you hold). The gate items are added to
  the pool in `create_items` and fill scatters them. Cartridges are awarded normally
  (no special starting-game preference). `create_items` raises `OptionError` if
  deferral is on but there is nowhere reachable to place the gates — i.e. every
  reachable starting game is itself a no-logic game (`_lock_sphere1_only_games` in
  `set_rules` just applies the boot rule from `self.deferred_sphere1_games`).
- `starting_game_amount` cartridges are precollected. `cherry_enabled_games` is a strict
  allowlist of games that keep their `<Game> - Cherry` location; an **explicit empty list
  = no game has a Cherry**. Its default (`options._CHERRY_OFF_BY_DEFAULT`) enables Cherry
  for every game *except* the ~15 whose Cherry is a deep "beat basically the whole game"
  gate. `Games`' own default is every game, in `death_link.py` (`DEATH_LINK_RULES`) order.
  Cherry removal happens in `create_regions` after each game's `create_rules` (an orphaned
  rule on the removed location is harmless). Velgress' pool exactly fills its location
  count, so when *its* Cherry is off it drops one item (`Progressive Gun` ×3→×2) via
  `_create_items(quantity_overrides=…)`. If items still exceed open locations,
  `create_items` **fails generation** (`OptionError`).

### Filler and traps

`create_items()` builds each game's pool, adds all Cartridges, then pads the remaining
unfilled locations with filler:

- **filler**: `get_filler_item_name()` picks a *random included game* (avoiding
  `bad_filler_games`, whose "filler" is a do-nothing item) and asks it for a filler name.
- **traps**: `trap_percentage` (0–100, General Options) — each padding slot is a trap
  with that probability instead of filler. Only trap today: **`Controls Swap Trap`**
  (`ItemClassification.trap`), from `general_items.trap_items`. Registered in
  `item_name_to_id` / `item_name_groups` (`"Traps"` group); `create_item` stamps the
  `trap` classification. The mod reads the received item and acts — the percentage is
  **not** in slot_data.

### slot_data → mod

`fill_slot_data()` sends `included_games` (list of game **numbers**), `goal_games`
(numbers), and the per-game option values the mod needs (`porgy_*`,
`block_koala_level_randomizer`, `warptank_level_randomizer`, `defer_sphere_1_games`,
`cherry_enabled_games` (game names), `death_link` (bool), `deathlink_games` (game
numbers — an explicit game list, empty = none)). `trap_percentage` is **not** sent.
Add a key here whenever the mod needs to know an option.

**Read every slot_data scalar/proxy with the raw, unchecked call —
`apclient_json_number_at(0, key)` / `apclient_json_proxy(0, key)` — never wrapped in a
GML `try`/`catch`, and never preceded by an `apclient_json_exists(0, key)` check on that
same key.** `gm-apclientpp` is open source
(`github.com/black-sliver/gm-apclientpp`, wrapping `github.com/black-sliver/apclientpp`)
— when this class of bug shows up again, read the actual C++
(`src/gm-apclientpp.cpp`) instead of guessing from symptoms. Relevant facts confirmed
from that source:
- JSON data from an event lives in a `std::vector<const json*> script_data`; proxy `0`
  is always that event's root. `apclient_json_proxy(proxy, key)` pushes a new entry and
  returns its index, or `-1` on failure — it never mutates or invalidates an
  *existing* entry (so "reading other keys first corrupts handle 0" is not what's
  happening, despite once looking that way empirically).
- `apclient_json_number_at`, `apclient_json_proxy`, and `apclient_json_exists` **all**
  wrap their body in their own internal C++ `try`/`catch` and, on any failure, call
  `show_error(ex.what())` then return a sentinel (`0.`, `-1`, or `false`/`GM_FALSE`).
  They never let a C++ exception reach GameMaker's own exception system, which is why a
  GML-side `try`/`catch` around them can't do anything useful — there's nothing left to
  catch by the time control returns to GML — and `show_error()` is almost certainly what
  actually produces the generic "Unknown exception" popup, not an uncaught native throw.
- `apclient_json_number_at(proxy, key)` does `script_data.at(int_proxy)->at(key)
  .get<double>()`. `.get<double>()` throws if the JSON value at that key **isn't a
  number** — e.g. a JSON `true`/`false`. **Confirmed root cause of one real bug**: the
  apworld sent `"death_link": False` — a bare Python bool, not `int(False)` — which
  serializes as JSON `false`, not `0`; reading it via `apclient_json_number_at` threw
  internally (caught, `show_error`'d, returned `0.`) on every single connect regardless
  of any mod-side code. Fixed apworld-side (`worlds/ufo50_full/__init__.py`,
  `fill_slot_data`): `"death_link": int(False)`. **Every slot_data value read via
  `apclient_json_number_at` must be a genuine number on the wire, not a Python bool
  literal** — an `Options` `.value` happens to already be `int`, so this only bites a
  bare literal like `False`/`True` written directly into `fill_slot_data`.
- Separately (still not fully explained at the C++ level, but empirically confirmed and
  the fix holds regardless): wrapping a scalar read in `apclient_json_exists(0, key)`
  immediately followed by `apclient_json_number_at(0, key)` on the *same* key — the
  pattern the now-deleted `ap_json_number_required`/`ap_json_proxy_required`
  (`gml_Script_ap_json_number_required.gml`, removed entirely rather than kept as dead
  code since this mod hadn't shipped a release with it yet) and their `try`/`catch`
  replacement `ap_json_number_safe`/`ap_json_proxy_safe` (also removed) both used — makes
  the read come back `0` regardless of the real value. This was caught by diffing against
  the last known-working release: it reads `golds_to_goal`/`cherries_to_goal`/
  `porgy_check_on_touch`/`porgy_radar`/`block_koala_level_randomizer`/
  `warptank_level_randomizer` with plain, unwrapped `apclient_json_number_at(0, key)`
  calls and works; wrapping those exact same reads is what broke them. **Never
  reintroduce a check-then-read-the-same-key helper, and never wrap these calls in
  `try`/`catch` either.**

The missing-key-on-an-old-seed problem the deleted wrappers were trying to solve is
still real and still unsolved: a raw call on a genuinely missing key still triggers
`show_error()`'s "Unknown exception" popup (though it also still returns a harmless `0.`
fallback, so the read itself doesn't corrupt anything — it's an unwanted dialog, not a
crash). If you need to guard a new slot_data key against an old seed, don't check-then-
read the same key and don't reach for `try`/`catch`; `apclient_json_typeof(proxy)` off a
proxy obtained from a *different* call (not the vector-mutating pattern already ruled
out) may be viable but is untested — verify against the real C++ source before trusting
it.

### Testing

No pytest. Generation tests are `unittest`:

```
python -m unittest discover -t . -s worlds/ufo50_full/test
python -m unittest worlds.ufo50_full.test.test_all_games
```

They build multiworlds with `test/__init__.py:generate(options, seed)` and assert
"all locations reachable with all items" + "beatable after `distribute_items_restrictive`".
They do **not** pin item counts or ids. `ALL_GAMES = list(ufo50_games.keys())`.
Quick ad-hoc check:

```python
from worlds.ufo50_full.test import generate, ALL_GAMES
mw = generate({"games": ALL_GAMES, "starting_game_amount": 5, "trap_percentage": 40}, seed=7)
```

### Adding / editing a game

1. `constants.game_ids` already has all 50 — a game is "implemented" once it's in
   `ufo50_games` in `__init__.py` (keep menu order) with a real `games/<game>/` package.
2. Follow the module contract above; lean on `game_helpers` / `goal_locations`.
3. Give the mod a matching `Archipelago_<Game>.yaml` using the **same offsets**.
4. Run the generation tests; add the game to `test/test_all_games.py:_PER_GAME`.

**Never edit the `Games` option docstring in `options.py` (the "Fully / Somewhat /
Placeholder Implemented" lists) without asking first** — not even to move a game between
tiers after giving it logic. That categorisation is the maintainer's call; mention the
suggested move in your summary instead.

### Tiered logic ("more upgrades → more checks")

When a game's checks gate on *how many* upgrades you hold rather than on a specific
route, split them into **tiers**. Tiers are **hand-rolled per game** in its own
`rules.py`: there's no shared helper or required table shape, so each game writes
whatever reads most naturally for its requirements. The conventions:

- Tiers are numbered from **1 = sphere 1** (no requirements), and each tier is defined
  by what it **requires**. Write both down: what each tier needs, and which locations
  sit in it.
- Gift/Gold/Cherry go in a tier like any other check.
- **Spell out tier 1 explicitly.** Define a `tier1` that returns `True` and assign every
  sphere-1 check to it with the same `rule(...)` calls as the other tiers, so every
  location's tier shows in `rules.py` (none are free just because a rule is missing).
- Keep `locations.sphere_1_locs` in step with tier 1.

Games that use tiers now:
- **Waldorf's Journey:** `tier1`..`tier4` closures (N-1 copies of each upgrade), with
  locations assigned tier by tier.
- **Planet Zoldath:** `tier1`..`tier5` closures, with locations assigned tier by tier.
- **Magic Garden:** `_SPHERE_TWO/_MID/_HIGH/_TOP_TIER_LOCS` tuples plus one predicate
  per tier.
- **Campanella 2:** a `WORLD_REQUIREMENTS` table whose tiers are regions A→D.
- **Seaside Drive:** an inline `{location: count}` dict.
- **Devilition:** a `round_requirements(n)` function whose requirements other
  locations borrow.

TODO hot-spots (incomplete logic *within* otherwise-working games): Vainger boss/route
tuning, Mini & Max NPC-quest checks (disabled), Party House per-threshold rule tables.

---

## The game mod

Lives in **`../ufo50-ap-mod/`**:

```
Full Archipelago/
  code/                     full-file GML: new scripts (gml_Script_*), replaced object events
  config/
    code_patch/             Archipelago_<Game>.yaml  — find/replace patches into decompiled GML
    new_object/  existing_object/   *.json object definitions
    textures_properties/    sprite config
  dll/gm-apclientpp.dll     the apclientpp bridge
  info.txt  gamebanana.json icon.png
ufo50-vanilla-code/         ~14k decompiled GML files — READ-ONLY reference for writing `find:` blocks
```

An external UFO 50 mod loader applies `config/code_patch/*.yaml` to the game's GML at
load and registers everything in `code/` (any `gml_Script_<name>.gml` becomes a callable
script — no manifest). Author `find:` blocks against `ufo50-vanilla-code/`, **not** the
`code/` folder.

**Prefer code patches wherever possible.** Per-game behaviour goes inline in that game's
`Archipelago_<Game>.yaml`, not in new `code/` files — no per-game `gml_Script_*` helpers,
even when the same small check is needed in two or three events (repeat it inline, or
compute it once into a local at the top of the event with a `prepend`). `code/` is for
shared framework scripts (`has_item`, `collect_location`, `ap_send_death`, …) and full-file
overrides that genuinely can't be expressed as patches.

### YAML patch format

```yaml
gml_Object_o44_Player_Other_11:        # target event/script (decompiled filename minus .gml)
  - type: findreplacetrim              # see types below
    find: |-
      <exact vanilla snippet>
    code: |-
      <replacement / inserted code>
```

Patch `type`s in use (by frequency): `findreplacetrim` (whitespace-insensitive match —
**prefer this**), `findreplace`, `prepend` (to top of event, no `find`), `findprepend`
(before matched text), `append`, `findappend` (after matched text), `findappendtrim`.
There is **no `findprependtrim`** — to insert before a block whitespace-insensitively,
use `findreplacetrim` and repeat the `find` inside `code`. `find:` blocks may contain
blank lines. Multiple patches per event = a YAML list under one key, applied in order.
Non-game framework files: `Archipelago_Internal_General.yaml`, `Archipelago_Internal_Saving.yaml`,
`Archipelago_Internal_Text.yaml`, `Archipelago_Internal_Traps.yaml`, `Archipelago_Internal_DeathLink.yaml`.

**Never end a `code:` block with a `//` line comment as its last line — except plain
`append` on a bare object event.** YAML's `|-` (strip chomping) drops the block's own
trailing newline, and `check_patches.py` only validates that `find:` text matches — it
does **not** parse the resulting merged GML for brace balance. Whatever the loader
splices onto the end of your code (often a closing `}`) can land on that trailing `//`
line and get silently commented out, producing a generic, hard-to-place loader error:
`"<script>: Unexpected end of code (expected '}' or 'end')"`. This applies to every type
where something follows the insertion point in the merged source: `findappend(trim)`
(original content resumes after), `findprepend` (the matched text itself resumes after),
`findreplace(trim)` (whatever followed the replaced span resumes after), `prepend` (rest
of the event body resumes after), and even `append` **when the target is a global
script/function** (`gml_GlobalScript_*`, has a closing `}` after the append point) —
only `append` on a bare object event (`gml_Object_..._Step_0` etc., a raw statement list
with nothing after it) or a full-file override under `code/` (you control every
surrounding line yourself) is actually safe. This bit an `Archipelago_Internal_Saving.yaml`
edit to `gml_GlobalScript_scrSaveNotification` (a `findappendtrim` whose inserted block
ended in three `//` lines, right before the with-block's closing `}` in vanilla). Fix:
put trailing explanatory comments in a self-terminating `/* ... */` block instead, or
make sure the block's last line is real code.

**One key per event object.** The loader parses each yaml as a mapping, so a
`gml_Object_..._Step_0:` key that appears twice in one file has its earlier copy
silently dropped (last wins). When adding a patch for an event a game already hooks,
add the item to the **existing** key's list — never append a second copy of the key.

### DeathLink

Opt-in via `death_link`; narrowed by `deathlink_games` — a strict game list (an
explicit empty list = no game, its `default` is every game, `death_link.py` order).
`fill_slot_data` sends it as sorted game numbers; the mod defaults `global.ap_dl_games[]`
all-false and flips on only the listed numbers. Spec table:
`death_link.py:DEATH_LINK_RULES` (send / receive phrase per game). Central plumbing:
`Archipelago_Internal_DeathLink.yaml` — reads the options on connect, enables the `DeathLink`
tag + bounce filter, parses incoming DeathLink bounces (own-echo guarded, dropped when
not in a game), and gates by game via `global.ap_dl_games[]`. Per game, a `# DeathLink:`
block in that game's yaml:
- **send** — at the death / game-over / battle-loss point, call
  `ap_send_death("<suffix>")` (alias is prepended; debounced ~3 s, gated).
- **receive** — a per-frame hook: `if (ap_deathlink_take()) { <effect> }` — kill the
  player, `hp -= N`, etc. `ap_deathlink_take()` consumes the pending death and arms
  the same cooldown so the effect it triggers doesn't echo back out.

Assumes gm-apclientpp's `apclient_death_link(cause)` sends, `apclient_connect_update`
takes a tags-JSON string, and `apclient_set_bounce_targets(games, slots, tags)` — flagged
in the yaml if the DLL build differs. Done: all 49 games with a meaningful death/loss
(Quibble Race = N/A by design). The last nine (Magic Garden, Mortol, Bushido Ball,
Block Koala, Camouflage, Golfaria, The Big Bell Race, Waldorf, Night Manor) hook
game-specific signals: Camouflage/Magic Garden watch a `matchOver`/`state` flag with a
rising-edge send latch; Golfaria zeroes `golfStrokes`; Big Bell Race routes through
`scr28_Damage`; Bushido Ball hooks the score-goal/timeout branches in the STATE_PLAY
handler; Waldorf/Mortol/Night Manor replicate the vanilla death transition on receive.

**All `find:` blocks are validated** against `ufo50-vanilla-code/` (and `code/` where an
event is fully overridden) by `../ufo50-ap-mod/check_patches.py` — it flags non-trim
`findappend`/`findprepend`/`findreplace` whose text doesn't match byte-for-byte (the
"No-op find and replace performed" loader error) and ambiguous trim anchors. Run it
after touching any `Archipelago_*.yaml`.

### Runtime AP model (in `code/`)

- `oArchipelago` (persistent, created in `rmInit`) polls `apclient_poll()` in Step and
  dispatches `apclient_json_source()` cases: `ap_slot_connected` (reads slot_data into
  `global.*`), `ap_items_received`, `ap_location_checked`, `ap_location_info` (scouts), …
- **Received items**: `global.ap_items_received[subgame][string(item_id)] = count`, an
  array of 52 structs (indices 0..51), built in `Archipelago_Internal_General.yaml` and persisted
  via `Archipelago_Internal_Saving.yaml` (`currProfileSaveData.apItemsReceived`).
  `global.included_games[0..51]` gates which subgames the loop processes — subgame 0 and
  **51** are force-set `true`. Cartridge items (subgame 0, id 1..50) are filtered by
  `global.included_games[item_id]`.
- **Per-game scripts** (`global.currGameID` picks the subgame):
  `has_item(id)` / `get_item_count(id)`, `collect_location(id)` /
  `is_location_collected(id)`, `scout_location`/`is_location_scouted` +
  `get_location_item`/`get_location_player`/`apclient_get_item_name`. `*_manual(gameID, id)`
  variants take an explicit subgame.
- **`global.ap_*` state is lazily initialized, not Create_0-initialized** — `ap_connected`,
  `game_goals`, `ap_cherry_earned`, `ap_locations_found`, `included_games` (and likely
  `ap_items_received`/`ap_scouts`) are only ever assigned inside event-driven code: the
  `ap_slot_connected` case in `oArchipelago_Step_0.gml`, or `scrLoadProfile` (patched in
  `Archipelago_Internal_General.yaml`) which runs slightly later, after `ap_connected`
  already flipped true. Every *existing* read of these globals happens to be reachable
  only after a write already occurred somewhere upstream in the same frame/flow, so this
  gap was invisible until code that runs **unconditionally every frame regardless of
  connection state** — e.g. a persistent HUD in `oArchipelago`'s own Draw event — read one
  cold at game boot. GameMaker's "not set before reading it" on an unset `global.*` fires
  at the point of the raw read, even mid-expression (a `variable && globalvar` short
  circuit only protects the second read if `variable` itself can never be true before the
  global is set) or as a bare function argument (`is_array(global.x)` still reads `global.x`
  first). Fix: explicit defaults for all five in `oArchipelago_Create_0.gml` (`false`/`[]`
  of 52 `NO_GOAL`/`false`/`{}` entries, mirroring the shape `scrLoadProfile` builds). Any
  new always-on `oArchipelago` code must either read only Create_0-initialized globals or
  add its own default there first.
- **`check_victory()` runs exactly once per frame, unconditionally, from
  `oArchipelago_Step_0.gml`** (right after `apclient_poll()`, self is always
  `oArchipelago`) — the single place that computes `goal_game_count`/`golds_have`/
  `golds_needed`/`cherries_have`/`cherries_needed`/`victory` and fires
  `apclient_status_update(AP_CLIENT_STATUS_GOAL)`. It used to also be called from
  `Other_15.gml`'s `SUB_SORT_PERFORM` (self=`oLibrary`) and
  `Archipelago_Internal_Saving.yaml`'s `scrSaveNotification` patch (self=whichever object
  won) — three separate instances each keeping their own undeclared (non-`var`) copies of
  the same numbers, computed at different moments. Don't add more call sites; anything
  that needs these values (e.g. `oArchipelago_Draw_0.gml`'s golds/cherries-toward-goal
  HUD readout, top-right of the library screen) reads them straight off `self`
  (`golds_have`, `golds_needed`, etc.), since `self` is always `oArchipelago` and Step
  always runs before Draw in the same frame. `golds_needed`/`cherries_needed` are
  `min(ap_golds_to_goal/ap_cherries_to_goal, goal_game_count)` — same formula
  `UFO50World.create_regions` (`worlds/ufo50_full/__init__.py`) uses goal-side;
  `golds_to_goal` has `range_start = 1` so `golds_needed` should never legitimately be 0
  once connected.
- **Attract mode is permanently disabled**, so new patches should **not** add an
  attract-mode guard at all. `Archipelago_Internal_General.yaml` disables it game-wide via
  three patches: `gml_Object_oTitleScreens_Other_12` (`attractTimer++` → `= 0`, so the
  title-screen attract trigger never fires), `gml_Object_oLibrary_Step_1` (resets
  `global.attractModeLibraryTimer` every frame), and `gml_Object_oLibrary_Other_25`
  (unconditional `exit;`, pre-empting the library-attract code that sets
  `global.attractMode = true`). `global.attractMode` can therefore never become `true`
  again anywhere in the game.

### Conventions when patching a game

- **Location checks**: usually a per-frame sweep in the game's `_Game_Step_0` (prepend)
  that calls `collect_location(n)` for anything satisfied, guarded by
  `!is_location_collected(n)` — so save-loaded progress reports too. Boss/one-shot
  events use `findprepend`/`findappend` at the win point.
- **Monotonic value ladders back-fill every lower rung.** When a set of checks is a
  ladder on one number that only ratchets up over a run — a score, rank, currency,
  running count — the per-frame sweep walks the **whole threshold list** and
  `collect_location(i)` for *every* rung the current value meets, deduped by
  `!is_location_collected`: `for i: if (current >= thresh[i]) collect(i)`. Reaching N
  awards 1..N, because a higher score/rank/count means the lower rungs were passed
  (even if the value jumped straight past them or the player never paused there).
  This applies to: **Attactics** rank, **Party House** popularity / cash / house
  space / star guests, **Mini & Max** shinies, **Kick Club** / **Campanella** /
  **Ninpek** points, **Magic Garden** score, **Overbold** `$N Wave`, and any similar
  score/rank/count ladder.
- **Do NOT back-fill level completions or one-off collectibles.** Stage / mission /
  level clears and individually-placed pickups stay one independent condition per
  location (`if (levelCleared[i]) collect(i)`, `if (gotItem[i]) collect(i)`) — reaching
  a later one does not imply the earlier ones. A non-linear game (Lords of Diskonia)
  can reach node N without 1..N-1, so its per-node checks are not a ladder.
- **Fire on the action, not the animation**: hook the frame the triggering thing
  actually happens (the killing blow lands / the goal is touched / the clear flag is
  set), never a post-hoc win screen, results tally, death cutscene, screen wipe, or
  delayed state transition. Good: Campanella level clear on reaching `o03_Goal`;
  Campanella 3 boss on `o08__ePar` spawning `o08_bossDeath`. When the only clean signal
  really is a late one, add the early hook *and* keep the late one as a
  `is_location_collected`-deduped fallback (Campanella 3, Bug Hunter, Hyper Contender).
- **Items apply mid-run "where possible"** (see the `ufo50-mod-midrun-items` memory):
  - unlock-style (abilities, weapon tiers, gates, characters): a **live**
    `has_item`/`get_item_count` read every frame — nothing to latch.
  - additive stat/currency/lives (meat, pieces, fuel, cash, teeth, extra lives): a
    **delta latch** — `global.ap<NN>_<thing>_granted` (or an instance `ap<Thing>Seen`)
    holds how much is already folded in; each frame `want = f(get_item_count)`, and if
    `want > seen` add the delta and set `seen = want`. Re-base `seen` at the run/level
    boundary patch so it never double-counts. Persist the latch via the game's SaveGame
    script only if the pool it feeds persists.
  - Boundary-only by design: Rail Heist per-level time/ammo (levels are seconds long),
    Party House `+1 Starting Popularity`/`+1 Starting Cash`.
- **Greyed-out / locked UI**: draw a translucent black box over the icon
  (`draw_set_alpha(0.55); draw_set_color(c_black); draw_rectangle(...)`) and refuse the
  action; don't play the game's "can't afford" feedback for an AP-locked option
  (see Combatants radial menu, Rock On! Island build menu).
- **Never add a new mod-side gameplay restriction (refuse an action, block a trade,
  disable a menu option, force an early state change) beyond what's explicitly asked
  for — in any case.** A visual-only lock (dimmed icon, gate overlay) is the safe
  default for representing an unfound/not-yet-unlocked item; do not also make it
  functionally block the interaction unless the user says to. Concretely: Planet
  Zoldath's equipment items are a softlock/BK safety net, not a real progression gate
  (either copy of a "Progressive <Item>" unlocks it, holding both does nothing extra —
  see items.py) — a self-initiated "AP-locked equipment trade refusal" patch that force-
  exited the merchant dialogue mid-state-machine (`subState = 10; exit;` inside the
  trade-confirm handler) left `o48_Game` in a state the rest of that state machine never
  anticipated, causing an intermittent native crash on later level generation that took
  a long debugging session to trace back to this one unrequested patch. The trade should
  have just completed normally, same as vanilla, with only the gate icon (already added
  for other reasons) indicating the lock visually.

### Traps (`Archipelago_Internal_Traps.yaml`)

`Controls Swap Trap` = subgame **51** / item **1**. On a genuinely new receipt
(`count > old_count`), `global.ap_controls_swap_timer = 30*60`. `oArchipelago` Step
counts it down **only while `instance_exists(oGame) && !global.paused`** (so it waits for
you to be in a game and freezes on pause). While it's `> 0`, `scrGetInput` swaps
`fire1 <-> fire2` (hold + pressed + released) for the slot — this also covers
`scrGetInputBoth`/`scrGetInputMerged`, which funnel through it. `scrGetInputMergedFire1`
(a couple of 2P co-op modes, reads raw keys) is intentionally not swapped.

To add another trap: pick subgame-51 offset in `general_items.trap_items` + register it
in `__init__.py` like `Controls Swap Trap`, then handle `subgame_id == 51 && item_id == N`
in `Archipelago_Internal_Traps.yaml`.

---

## The YAML generator

Lives in **`../ufo50-ap-yaml-generator/`** (own git repo, `.nojekyll` → served as a static
GitHub Pages site). A single-page, no-build web form that writes a player YAML for
`UFO 50 Full`.

```
index.html        the whole app (vanilla JS, no deps); renders entirely from options.json
options.json      GENERATED — every option, its kind/default/doc, plus games_order + status tiers
dump_options.py   regenerates options.json from this apworld checkout
carts/<n>.png     cartridge art, n = 1-based index into games_order (death_link.py order)
```

**Whenever `options.py` changes (new option, changed default/docstring/range/choices, group
changes) — or the `Games` docstring tiers or `death_link.py` order change — re-run the dump
and commit `options.json` in that repo:**

```
cd ../ufo50-ap-yaml-generator
python dump_options.py < /dev/null        # checkout defaults to ../ufo50-apworld-full
```

It imports `worlds.AutoWorldRegister`, so other worlds' missing deps (e.g. a `zilliandomizer`
`ModuleNotFoundError` traceback) print noise but are harmless — success is the final
`wrote …/options.json: N options` line. Then `git diff options.json` to sanity-check.

What `dump_options.py` pulls, and what's hard-coded where:

- Options come from `Options.get_option_groups(world, Visibility.template)`, i.e.
  `ufo50_option_groups` plus AP's common groups. Kind is inferred from the option class
  (toggle / choice / range / set / list / counter / text / raw YAML). `HIDDEN` keys
  (`progression_balancing`, `accessibility`) and the `Item & Location Options` group are
  still written to the YAML at their default but not shown.
- `AP_VERSION` (the `requires: version:` written into YAMLs) is a constant in the script —
  bump it by hand. `world_version` comes from `worlds/ufo50_full/archipelago.json`.
- `games_order` = `list(DEATH_LINK_RULES)` — grid order and cart art numbering.
- `status_tiers` / `status` are **parsed out of the `Games` docstring**: each line whose
  text before `:` ends in `Implemented` starts a tier, following comma-separated names
  belong to it. Keep that docstring's shape; the script warns about unknown/missing game
  names. (Tier edits themselves are still the maintainer's call — see
  ["Adding / editing a game"](#adding--editing-a-game).)
- `index.html` hard-codes a few option keys/names: `games` + `cherry_enabled_games` are
  merged into one clickable cart grid (off → on → on-with-Cherry); `SIDE =
  starting_game_amount, golds_to_goal, cherries_to_goal` sit next to the grid; the rest of
  `"General Options"` goes under a collapsed "More options". A group named
  `"<Game> Options"` where `<Game>` is a valid game name is only shown when that game is
  included; otherwise it's written at its `options.py` default (toggles too — never
  forced off). Every control's initial value is its `options.json` default, so the
  generator has no defaults of its own. **Renaming any of those keys or the
  `General Options` / `<Game> Options` group names needs a matching `index.html` edit**;
  anything else is picked up from `options.json` automatically.
- Local testing: `python -m http.server` in that folder (it `fetch`es `options.json`, so
  opening the file directly fails).

---

## Dead code

**When a change makes code unused, delete it in the same change** — never leave it
commented out, `if (false)`-guarded, or sitting as an unreferenced helper "in case". This
applies to both repos and to the comments too: a doc comment that describes behaviour the
change removed is dead code with extra steps (the `ap_json_number_required` /
`ap_json_number_safe` scripts under ["slot_data → mod"](#slot_data--mod) were deleted
outright rather than kept as dead code, and that's the standard).

What counts, per repo:

- **apworld** — helper functions, constants, and per-game lookup tables (especially
  special-case dicts keyed by game/level/item name) whose last caller just went away, and
  now-unused imports. Check a name with
  `grep -rn "\bNAME\b" worlds/ufo50_full/` and confirm the only hit is its own
  definition. Don't strip a name that's part of the per-game module contract
  (`get_items`, `create_locations`, …) just because nothing in the package calls it —
  `UFO50World` calls those **by name**.
- **mod** — `gml_Script_<name>.gml` files under `code/` that nothing calls. The loader
  registers every file in `code/` unconditionally, so an uncalled script ships silently
  and never shows up as an error. A script's own body never mentions its own name, so
  `grep -rl "\b<name>\b" code config` returning nothing (or only its own file) means
  uncalled. Also drop whole `find:`/`code:` patch pairs that no longer do anything rather
  than leaving a patch that matches and re-inserts what it replaced.
- **never** — anything in `ufo50-vanilla-code/`. It's read-only decompile reference, and a
  vanilla identifier that only appears inside a `find:` block is doing its job, not dead.

**Scope it to your own change.** Remove what *this* change orphaned; pre-existing dead
code gets **reported, not swept up** — a wider scan is welcome, an unrequested cleanup
commit is not. Known-uncalled today, left alone: `code/gml_Script_is_location_hinted.gml`.

---

## Gotchas

- `constants.game_ids` also contains `"Main Menu": 0`; it's excluded from the `games`
  option and from `ufo50_games`. `unimplemented_ufo50_games` is therefore `["Main Menu"]`,
  not empty — that's why the module-level `base_id` used for the nothing-filler id is
  defined.
- All 50 real games are implemented (in `ufo50_games` **and** with a mod YAML). "Beat
  half the games" gating and filler-game selection both key off the *implemented* set.
- The apworld and the mod both hard-code `BASE_ID = 2106155000000` and the
  subgame*1000+offset scheme; any new id must be added to **both**.
- The mod's `code/` folder is the deployed override set; `ufo50-vanilla-code/` is the
  decompile reference. Never write `find:` blocks against `code/`.
