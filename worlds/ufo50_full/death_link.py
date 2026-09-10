"""DeathLink send / receive conditions, per UFO 50 game.

DeathLink is opt-in via the ``death_link`` yaml option. When it is on, the mod
watches each game for its **send** condition and fires a DeathLink; and when a
DeathLink arrives from another world it applies that game's **receive** condition.
The ``deathlink_games`` option narrows this to a chosen subset of games (empty =
all of them); a game left out plays with no DeathLink at all.

The mod side lives in ``Archipelago_DeathLink.yaml`` (central plumbing) plus a
``# DeathLink:`` block in each game's ``Archipelago_<Game>.yaml``; this table is
the spec it implements, kept here so the apworld documents the behaviour too.

Each entry is ``game name -> (send, receive)``:

* ``send``     -- what, in that game, fires a DeathLink to everyone else.
* ``receive``  -- what that game does to you when a DeathLink arrives.
* ``None``     -- that direction is disabled (Bug Hunter can't be killed by a
                  DeathLink in a meaningful way, Block Koala has no "death", etc.).

Where the player gave a single phrase it is used for **both** directions. A few
games send on a game-over but receive something softer (lose N HP / N pieces /
N days) so a DeathLink mid-run is a setback, not an instant loss.
"""

from typing import Optional


class DeathLinkRule:
    """One game's DeathLink behaviour. ``send`` / ``receive`` are short human
    phrases; ``None`` means that direction does nothing."""

    __slots__ = ("send", "receive")

    def __init__(self, send: Optional[str], receive: Optional[str]) -> None:
        self.send = send
        self.receive = receive

    def __repr__(self) -> str:
        return f"DeathLinkRule(send={self.send!r}, receive={self.receive!r})"


def _both(what: str) -> DeathLinkRule:
    """Same phrase for send and receive (the common case)."""
    return DeathLinkRule(what, what)


DEATH_LINK_RULES: dict[str, DeathLinkRule] = {
    "Barbuta":            _both("death"),
    "Bug Hunter":         DeathLinkRule("game over", "lose 5 kills"),
    "Ninpek":             _both("death"),
    "Paint Chase":        _both("course fail"),
    "Magic Garden":       _both("death"),
    "Mortol":             DeathLinkRule("killed by an enemy (not the sacrifice ritual)", "death"),
    "Velgress":           _both("death"),
    "Planet Zoldath":     DeathLinkRule("death", "lose 3 HP"),
    "Attactics":          _both("lose a battle"),
    "Devilition":         DeathLinkRule("game over", "lose 15 pieces"),
    "Kick Club":          _both("death"),
    "Avianos":            DeathLinkRule("lose a battle", "lose all units"),
    "Mooncat":            _both("death"),
    "Bushido Ball":       _both("lose a round"),
    "Block Koala":        DeathLinkRule("undo", "forced restart level"),
    "Camouflage":         DeathLinkRule("get eaten", "get eaten by a bird"),
    "Campanella":         _both("death"),
    "Golfaria":           _both("run out of strokes"),
    "The Big Bell Race":  _both("death"),
    "Warptank":           _both("death"),
    "Waldorf's Journey":  _both("death"),
    "Porgy":              _both("death"),
    "Onion Delivery":     _both("death"),
    "Caramel Caramel":    _both("death"),
    "Party House":        DeathLinkRule("run out of time", "lose 3 days"),
    "Hot Foot":           DeathLinkRule("game over", "the enemy scores 5 points"),
    "Divers":             _both("game over"),
    "Rail Heist":         _both("death"),
    "Vainger":            _both("death"),
    "Rock On! Island":    DeathLinkRule("game over", "lose 10 HP"),
    "Pingolf":            DeathLinkRule("finish a hole over par", "gain 2 strokes"),
    "Mortol II":          DeathLinkRule("killed by an enemy (not the sacrifice)", "death"),
    "Fist Hell":          _both("death"),
    "Overbold":           DeathLinkRule("game over", "lose 6 HP"),
    "Campanella 2":       DeathLinkRule("game over", "lose 4 HP"),
    "Hyper Contender":    _both("lose a fight"),
    "Valbrace":           _both("death"),
    "Rakshasa":           DeathLinkRule("game over", "death"),
    "Star Waspir":        _both("death"),
    "Grimstone":          _both("game over"),
    "Lords of Diskonia":  _both("lose a battle"),
    "Night Manor":        _both("death"),
    "Elfazar's Hat":      _both("death"),
    "Pilot Quest":        _both("death"),
    "Mini & Max":         _both("death"),
    "Combatants":         _both("lose a battle"),
    "Quibble Race":       DeathLinkRule(None, None),
    "Seaside Drive":      _both("death"),
    "Campanella 3":       _both("death"),
    "Cyber Owls":         _both("death"),
}
