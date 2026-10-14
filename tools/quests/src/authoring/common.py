"""Helpers for writing chapters in Python: each src/authoring/<chapter>.py builds its quests with these and calls
chapter(), which writes src/chapters/<chapter>.json (the generator's input). Run: python src/authoring/<chapter>.py
from tools/quests, or python src/authoring/build_all.py. Short forms match the chapter format in tools/quests/README."""
import json
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "chapters")


def quest(id, title, tasks, rewards=(), text=(), after=(), **extra):
    q = {"id": id, "title": title}
    if after:
        q["after"] = list(after)
    if text:
        q["text"] = list(text) if not isinstance(text, str) else [text]
    q["tasks"] = list(tasks)
    if rewards:
        q["rewards"] = list(rewards)
    q.update(extra)
    return q


def talk_char(character, lines, title=None):
    t = {"talk": "character", "character": character, "lines": list(lines)}
    if title:
        t["title"] = title
    return t


def talk_org(org, lines, title=None):
    t = {"talk": "org", "org": org, "lines": list(lines)}
    if title:
        t["title"] = title
    return t


def talk_villager(profession, lines, title=None):
    t = {"talk": "villager", "profession": profession, "lines": list(lines)}
    if title:
        t["title"] = title
    return t


def item(id, count=1, **extra):
    t = {"item": id}
    if count != 1:
        t["count"] = count
    t.update(extra)
    return t


def reward_item(id, count=1, **extra):
    r = {"item": id}
    if count != 1:
        r["count"] = count
    r.update(extra)
    return r


def skill(tree, xp):
    return {"skill": tree, "xp": xp}


def give(item_with_nbt, title):
    return {"command": "/give {p} " + item_with_nbt, "title": title}


def give_guide():
    return give('patchouli:guide_book{"patchouli:book":"patchouli:fotf_field_guide"}', "The Field Guide")


def chapter(name, title, subtitle, icon, group, order, quests, **extra):
    data = {"title": title, "subtitle": subtitle, "icon": icon, "group": group, "order": order}
    data.update(extra)
    data["quests"] = quests
    path = os.path.join(OUT, name + ".json")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"wrote chapters/{name}.json: {len(quests)} quests")


def giver_org(org, lines, accept="I'll do it", requires=()):
    """The quest is offered by any representative of an organisation (sneak + right-click one in any village)."""
    g = {"type": "org", "org": org, "lines": list(lines), "accept": accept}
    if requires:
        g["requires"] = list(requires)
    return g


def encounter(lines=None, then="talk", **spec):
    """A character or mob turns up near the player for this step (see README: encounter)."""
    e = dict(spec, then=then)
    if lines:
        e["lines"] = list(lines)
    return {"encounter": e}
