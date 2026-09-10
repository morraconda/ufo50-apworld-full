# CLAUDE.md — UFO 50 Full (Archipelago world + game mod)

This repo is a full Archipelago checkout whose **only local work** is the world in
`worlds/ufo50_full/` (the "UFO 50 Full" apworld). Everything else is stock Archipelago —
don't touch it. There is a **separate, companion repo** for the in-game mod (see
["The game mod"](#the-game-mod) below); the two are developed together and must agree on
every id.

- apworld repo: `github.com/morraconda/ufo50-apworld-full`, branch `main`.
- mod repo: sibling directory `../ufo50-ap-mod/` (not a git repo here).
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
  (`_game_is_sphere1_only`) and that you did **not** start with get their `Boot <Game>`
  entrance gated behind holding all three `Artificial Logic Gate 1/2/3` items
  (`general_items.logic_gate_items`, subgame-51 ids). Those three progression items are
  added to the pool in `create_items` and fill scatters them, so none of a deferred
  game's checks can sit at the start of the critical path. Cartridges are awarded
  normally (no special starting-game preference). `create_items` raises `OptionError`
  if deferral is on but there is nowhere reachable to place the gates (`_lock_sphere1_only_games`
  in `set_rules` just applies the boot rule from `self.deferred_sphere1_games`).
- `starting_game_amount` cartridges are precollected. `cherry_enabled_games` is a strict
  allowlist of games that keep their `<Game> - Cherry` location; an **explicit empty list
  = no game has a Cherry**. Its default (`options._CHERRY_OFF_BY_DEFAULT`) enables Cherry
  for every game *except* the ~15 whose Cherry is a deep "beat basically the whole game"
  gate. `Games`' own default is every game, in `death_link.py` (`DEATH_LINK_RULES`) order.
  Cherry removal happens in `create_regions` after each game's `create_rules` (an orphaned
  rule on the removed location is harmless). Velgress / Mortol II's pools exactly fill
  their location count, so when *their* Cherry is off they drop one item
  (`Progressive Gun` ×3→×2, `+10 Life` ×7→×6) via `_create_items(quantity_overrides=…)`.
  If items still exceed open locations, `create_items` **fails generation** (`OptionError`).

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

TODO hot-spots (incomplete logic *within* otherwise-working games): Vainger boss/route
tuning, Mini & Max NPC-quest checks (disabled), Party House per-threshold rule tables.

---

## The game mod

Lives in **`../ufo50-ap-mod/`**:

```
Full Archipelago Mod/
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
- **Attract mode**: every gameplay patch must be a no-op when `global.attractMode` — the
  title-screen demo still has to play. Standard guard: `if (!global.attractMode) { … }`
  or `(global.attractMode || <ap condition>)`.

### Conventions when patching a game

- **Location checks**: usually a per-frame sweep in the game's `_Game_Step_0` (prepend)
  that calls `collect_location(n)` for anything satisfied, guarded by
  `!is_location_collected(n)` — so save-loaded progress reports too. Boss/one-shot
  events use `findprepend`/`findappend` at the win point.
- **Award only the check that was actually earned — never a cumulative `for i in
  1..current: collect_location(i)` fill.** Reaching milestone N sends *only* N's check,
  not 1..N (a value like a score / rank / floor / party level can jump, and a
  non-linear game like Lords of Diskonia can reach N without 1..N-1). For a
  monotonic-milestone sweep, collect only `f(min(current, MAX))`. Per-element flag
  sweeps (`if (levelCleared[i]) collect(i)`, one independent condition per location)
  are fine and stay. **Overbold is the sole exception** — its `$N Wave` checks are
  deliberately cumulative (`for i: if (prize >= i*100) collect(i)`).
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
