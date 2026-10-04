from make_name_tags import clashes, tag_names


def test_clashing_names_get_their_mod_in_brackets():
    groups = [[('handcrafted:oak_chair', 'block.handcrafted.oak_chair', 'Oak Chair'),
               ('another_furniture:oak_chair', 'block.another_furniture.oak_chair', 'Oak Chair')]]
    assert tag_names(groups, {'handcrafted': 'Handcrafted'}) == {
        'block.handcrafted.oak_chair': 'Oak Chair (Handcrafted)',
        'block.another_furniture.oak_chair': 'Oak Chair (Another Furniture)',
    }


def test_clashes_ignore_case_spaces_and_same_mod_repeats():
    names = {
        'block.biomesoplenty.maple_planks': ('biomesoplenty:maple_planks', 'Maple Planks'),
        'block.regions_unexplored.maple_planks': ('regions_unexplored:maple_planks', 'maple  planks'),
        'item.alexscaves.disc_fragment_a': ('alexscaves:disc_fragment_a', 'Disc Fragment'),
        'item.alexscaves.disc_fragment_b': ('alexscaves:disc_fragment_b', 'Disc Fragment'),
        'item.naturalist.duck': ('naturalist:duck', 'Duck'),
    }
    groups = clashes(names, hidden=set())
    assert [sorted(i for i, _, _ in g) for g in groups] == [['biomesoplenty:maple_planks', 'regions_unexplored:maple_planks']]


def test_hidden_items_dont_count_as_clashes():
    names = {
        'item.farmersdelight.tomato': ('farmersdelight:tomato', 'Tomato'),
        'item.farm_and_charm.tomato': ('farm_and_charm:tomato', 'Tomato'),
    }
    assert clashes(names, hidden={'farm_and_charm:tomato'}) == []
