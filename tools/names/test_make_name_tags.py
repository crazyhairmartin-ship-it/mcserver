from make_name_tags import clashes, is_furniture, rename


def test_species_swap_renames_the_whole_wood_set_of_one_mod():
    names = {
        'block.regions_unexplored.maple_planks': ('regions_unexplored:maple_planks', 'Maple Planks'),
        'block.regions_unexplored.stripped_maple_log': ('regions_unexplored:stripped_maple_log', 'Stripped Maple Log'),
        'block.biomesoplenty.maple_planks': ('biomesoplenty:maple_planks', 'Maple Planks'),
    }
    spec = {'species': [{'mod': 'regions_unexplored', 'word': 'Maple', 'to': 'Sugar Maple'}], 'renames': {}}
    assert rename(names, spec) == {
        'block.regions_unexplored.maple_planks': 'Sugar Maple Planks',
        'block.regions_unexplored.stripped_maple_log': 'Stripped Sugar Maple Log',
    }


def test_species_swap_matches_whole_words_at_the_start_of_the_id():
    names = {
        'block.bloomingnature.fir_log': ('bloomingnature:fir_log', 'Fir Log'),
        'item.bloomingnature.firefly_bottle': ('bloomingnature:firefly_bottle', 'Firefly Bottle'),
    }
    spec = {'species': [{'mod': 'bloomingnature', 'word': 'Fir', 'to': 'Silver Fir'}], 'renames': {}}
    assert rename(names, spec) == {'block.bloomingnature.fir_log': 'Silver Fir Log'}


def test_single_renames_go_by_item_id():
    names = {'item.mimi.flute': ('mimi:flute', 'Flute')}
    assert rename(names, {'species': [], 'renames': {'mimi:flute': 'Concert Flute'}}) == {'item.mimi.flute': 'Concert Flute'}


def test_clashes_ignore_case_spaces_and_same_mod_repeats():
    names = {
        'block.biomesoplenty.maple_planks': ('biomesoplenty:maple_planks', 'Maple Planks'),
        'block.regions_unexplored.maple_planks': ('regions_unexplored:maple_planks', 'maple  planks'),
        'item.alexscaves.disc_fragment_a': ('alexscaves:disc_fragment_a', 'Disc Fragment'),
        'item.alexscaves.disc_fragment_b': ('alexscaves:disc_fragment_b', 'Disc Fragment'),
    }
    groups = clashes(names, hidden=set())
    assert [sorted(i for i, _, _ in g) for g in groups] == [['biomesoplenty:maple_planks', 'regions_unexplored:maple_planks']]


def test_hidden_items_and_furniture_dont_count_as_clashes():
    names = {
        'item.farmersdelight.tomato': ('farmersdelight:tomato', 'Tomato'),
        'item.farm_and_charm.tomato': ('farm_and_charm:tomato', 'Tomato'),
        'block.handcrafted.oak_chair': ('handcrafted:oak_chair', 'Oak Chair'),
        'block.candlelight.oak_chair': ('candlelight:oak_chair', 'Oak Chair'),
    }
    assert clashes(names, hidden={'farm_and_charm:tomato'}) == []
    assert is_furniture('candlelight:acacia_cabinet', 'Acacia Cabinet')
    assert not is_furniture('farmersdelight:rope', 'Rope')


def test_species_swap_covers_the_bare_block_too():
    names = {'block.meadow.limestone': ('meadow:limestone', 'Limestone')}
    spec = {'species': [{'mod': 'meadow', 'word': 'Limestone', 'to': 'Alpine Limestone'}], 'renames': {}}
    assert rename(names, spec) == {'block.meadow.limestone': 'Alpine Limestone'}


def test_species_swap_leaves_furniture_alone():
    names = {'block.beachparty.palm_chair': ('beachparty:palm_chair', 'Palm Chair')}
    spec = {'species': [{'mod': 'beachparty', 'word': 'Palm', 'to': 'Coconut Palm'}], 'renames': {}}
    assert rename(names, spec) == {}
