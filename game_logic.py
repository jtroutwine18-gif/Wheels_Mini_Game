# game_logic.py
import random
from typing import Dict, List, Any, Tuple

# Wheels copied from your MTGwheelsV3.py (with one small fix: missing comma in First Condition list)
WHEELS: Dict[str, List[str]] = {
    "Tribe Type": [
        "Advisor", "Merfolk", "Serf", "Aetherborn", "Elf", "Serpent",
        "Ally", "Elk", "Minion", "Servo", "Angel", "Minotaur",
        "Faerie", "Mole", "Shaman", "Ape", "Shapeshifter",
        "Archer", "Fish", "Mongoose", "Sheep", "Archon", "Flagbearer", "Monk", "Siren",
        "Artificer", "Fox", "Monkey", "Skeleton", "Assassin", "Frog", "Moonfolk", "Slith",
        "Assembly-Worker", "Fungus", "Mutant", "Sliver", "Gargoyle", "Myr", "Mystic", "Snake",
        "Avatar", "Giant", "Naga", "Soldier", "Badger", "Gnome", "Nautilus",
        "Barbarian", "Goat", "Nephilim", "Basilisk", "Goblin", "Nightmare", "Specter", "Bat",
        "God", "Nightstalker", "Spellshaper", "Bear", "Golem", "Ninja", "Sphinx", "Beast",
        "Gorgon", "Noggle", "Spider", "Nomad", "Berserker",
        "Gremlin", "Nymph", "Spirit", "Bird", "Griffin", "Octopus", "Splinter",
        "Hag", "Ogre", "Boar", "Harpy", "Ooze", "Squid", "Bringer",
        "Hellion", "Squirrel", "Brushwagg", "Hippo", "Orc", "Starfish",
        "Hippogriff", "Camel", "Homarid", "Ouphe", "Survivor", "Ox",
        "Horror", "Cat", "Horse", "Pegasus", "Thopter", "Centaur", "Hound", "Human",
        "Treefolk", "Hydra", "Citizen", "Phoenix", "Cleric", "Troll", "Imp", "Construct",
        "Pirate", "Unicorn", "Insect", "Plant", "Vampire", "Crab", "Crocodile", "Jellyfish",
        "Juggernaut", "Rabbit", "Wall", "Rat", "Warrior", "Kithkin", "Knight", "Werewolf",
        "Dinosaur", "Kobold", "Kor", "Wizard", "Dragon", "Kraken", "Rogue", "Wolf",
        "Drake", "Dreadnought", "Worm", "Druid", "Dryad", "Lhurgoyf", "Saproling", "Wurm",
        "Dwarf", "Lizard", "Scarecrow", "Zombie", "Elder", "Eldrazi", "Scorpion",
        "Elemental", "Mercenary", "Scout", "Pick Your Own",
        "Tribeless (No Restriction to Tribe Type)", "Only 1 Set Per Tribe",
        "Artifact Creatures", "Changeling"
    ],

    "Mana Base": ["1", "2", "3", "4", "5", "6"],
    "Color Selection": ["Red", "Blue", "Green", "Black", "White", "Colorless"],

    "Structural Condition": [
        "Basic Lands Only",
        "Pain Lands Only",
        "Equal Quanities for All Card Types (Land Included)",
        "2 Cards Make A Playset",
        "22 Lands",
        "20 Lands",
        "26 Lands",
        "Freebie"
    ],

    "First Condition (Lands Unaffected)": [
        "Artisan",
        "4 Rare 4 Mythic",
        "4 Rare 0 Mythic",
        "0 Rare 4 Mythic",
        "1 Playset per Sub Creature Type",
        "2 Mythic 2 Rare",
        "Take One of Opponents",
        "Creatures Toughness > Attack",
        "Freebie",
        "Copy Opp's First Condition"
    ],

    "Second Condition (Lands Unaffected)": [
        "Creatures Only",
        "Token Creatures Only",
        "No Creatures",
        "No Tokens",
        "Creatures Mana cost 4+",
        "Creatures mana Cost less than 4",
        "Freebie",
        "No Enchantments",
        "Copy Opp's Second Condition"
    ],

    "Cheater's Wheel": [
        "All Instances",
        "All Sorceries",
        "All Enchantments",
        "No Creatures",
        "Nothing Higher Than 1",
        "Nothing Lower Than 4",
        "Opponent Picks",
        "Freebie"
    ],

    "Replacement": [
        "Opponent Choose All",
        "Mulligan 4",
        "Turn 3 Delay (Can Play Lands)",
        "Freebie",
        "Max Card Deck",
        "Pauper",
        "Only 1 Creature of a Power Level and Must Match Attack Defense",
        "Highlander",
        "Australian Highlander",
        "Opt Yes for Cheater Next Round",
        "BRAWL!!!"
    ],

    "Winner's Wheel": [
        "Pick Con Opp For You",
        "Pick All Opp's Con",
        "Freebie of Choice",
        "Pick Your Tribe",
        "Pick Your Colors Matching Mana Base",
        "Pick Your Color and Mana Base",
        "Get Out of Cheater Prompt Card"
    ]
}


def _pick_one(wheel_name: str) -> str:
    return random.choice(WHEELS[wheel_name])


def _pick_many(wheel_name: str, k: int) -> List[str]:
    return random.sample(WHEELS[wheel_name], k=k)


def spin_round(did_cheat: bool, did_win: bool) -> Dict[str, Any]:
    """
    Runs ONE full 'round spin' equivalent to your terminal game:
    - Skips Replacement & Color Selection during initial spin
    - Winner's Wheel only if did_win
    - Cheater's Wheel only if did_cheat
    - Tribe Type always 2 spins (non-repeat)
    - First Condition spins twice if did_cheat else once
    - Color Selection count = Mana Base
    """
    results: Dict[str, Any] = {}
    replaced: List[str] = []
    notes: List[str] = []

    for wheel_name in WHEELS.keys():
        if wheel_name in ["Replacement", "Color Selection"]:
            continue
        if wheel_name == "Winner's Wheel" and not did_win:
            continue
        if wheel_name == "Cheater's Wheel" and not did_cheat:
            continue

        if wheel_name == "Tribe Type":
            results[wheel_name] = _pick_many("Tribe Type", 2)
            continue

        if wheel_name.startswith("First Condition"):
            spins = 2 if did_cheat else 1
            results[wheel_name] = _pick_many(wheel_name, spins)
            continue

        results[wheel_name] = _pick_one(wheel_name)

    # Color Selection depends on Mana Base
    mana_count = int(results["Mana Base"])
    results["Color Selection"] = _pick_many("Color Selection", mana_count)

    # Replacement is allowed only if NOT cheater
    replacement_available = (not did_cheat)

    return {
        "results": results,
        "replaced": replaced,
        "replacement_used": False,
        "replacement_available": replacement_available,
        "notes": notes,
        "did_cheat": did_cheat,
        "did_win": did_win,
    }


def apply_replacement(state: Dict[str, Any], wheel_to_replace: str) -> Tuple[Dict[str, Any], str]:
    """
    Applies exactly ONE replacement per round, only if not cheater.
    Replacement replaces the selected wheel's value with a random choice from Replacement wheel.
    """
    if not state.get("replacement_available", False):
        return state, "No replacements allowed for cheaters."
    if state.get("replacement_used", False):
        return state, "No more replacements this round."

    results = state.get("results", {})
    if wheel_to_replace not in results:
        return state, "Invalid wheel selection."

    new_value = _pick_one("Replacement")
    results[wheel_to_replace] = new_value

    if wheel_to_replace not in state["replaced"]:
        state["replaced"].append(wheel_to_replace)

    state["replacement_used"] = True
    state["results"] = results
    return state, f"{wheel_to_replace} replaced with: {new_value}"
