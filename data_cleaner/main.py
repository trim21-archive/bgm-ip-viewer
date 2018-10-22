from collections import defaultdict
from typing import List, Dict, Union, Any
import base64
from bgm import settings
from bgm.models import Subject, Relation, Map
from peewee import DoesNotExist
import time

blank_list = ['角色出演', '片头曲', '片尾曲', '其他', '画集', '原声集']


def remove_relation(source, target, rebuild=True):
    source = int(source)
    target = int(target)
    Relation.update(removed=True).where(
        (Relation.id == f'{source}-{target}') | (Relation.id == f'{target}-{source}')
    )


def rebuild_map(map_id=None, item_id=None):
    if item_id:
        map_id = Subject.get_by_id(item_id).map

    if map_id:
        # id_list = [x.id for x in Subject.select(Subject.id).where(Subject.map == int(map_id))]
        Subject.update(map=None).where(Subject.map == map_id).execute()
        Relation.update(map=None).where(Relation.map == map_id).execute()


def remove_nodes(node_id, rebuild=True):
    Subject.delete_by_id(node_id)
    Relation.delete().where((Relation.source == node_id) | (Relation.target == node_id)).execute()


def nodes_need_to_remove(*node_ids):
    for node in node_ids:
        assert isinstance(node, int)
    Subject.delete().where(Subject.id.in_(node_ids)).execute()
    Relation.delete().where(Relation.source.in_(node_ids) | Relation.target.in_(node_ids)).execute()


def relations_need_to_remove(kwargs):
    for id_1, id_2 in kwargs:
        Relation.update(removed=True).where(((Relation.source == id_1) & (Relation.target == id_2)) |
                                            ((Relation.source == id_2) & (Relation.target == id_1))).execute()


done_id = set()


def pre_remove_relation():
    edge_need_remove = set()
    for edge in Relation.select().where(Relation.relation.in_(blank_list)):
        # if edge.relation in blank_list:
        edge_need_remove.add(edge.id)
        edge_need_remove.add(f'{edge.target}-{edge.source}')
    CHUNK = 500
    edge_need_remove = list(edge_need_remove)
    assert '7771-1058' in edge_need_remove
    while len(edge_need_remove):
        Relation.update(removed=True).where(Relation.id.in_(edge_need_remove[:CHUNK])).execute()
        edge_need_remove = edge_need_remove[CHUNK:]


def add_new_subject(subject_id):
    print('add', subject_id)
    subject_id = int(subject_id)

    def add_new_subject_func(source_id):
        source_id = int(source_id)
        edges = list(Relation.get_relation_of_subject(source_id))
        for edge in edges:
            assert not edge.removed
        map_id = None

        for edge in edges:
            if edge.map:
                map_id = edge.map
                break

        if not map_id:
            m = Map.create()
            map_id = m.id

        for edge in edges:
            if not edge.map:
                if len(list(Subject.select().where(Subject.id.in_([edge.source, edge.target])))) == 2:
                    edge.map = map_id

        Subject.update(map=map_id).where(Subject.id == source_id).execute()
        Relation.update(map=map_id).where(Relation.id.in_([x.id for x in edges])
                                          & Relation.removed.is_null()).execute()

        done_id.add(source_id)

        for edge in edges:
            yield edge.target

    worker([subject_id, ], work_fun=add_new_subject_func)


import types


def worker(start_job=None, work_fun=None):
    if not isinstance(work_fun, types.FunctionType):
        raise ValueError('work_fun must be a function')
    yield_job = []
    if start_job is None:
        start_job = [x.id for x in Subject.select(Subject.id).where(Subject.map.is_null())]

    def do(j):
        # time.sleep(0.1)
        if j in done_id:
            return
        for node in work_fun(j):
            yield_job.append(node)
        done_id.add(j)

    while True:
        # print('\r', len(yield_job) + len(start_job), end='')
        if yield_job:
            j = yield_job.pop()
            do(j)
        elif start_job:
            j = start_job.pop()
            do(j)
        else:
            # print()
            # print('finish process map, start save to db')
            break


def first_run():
    nodes_need_to_remove(91493, 102098, 228714, 231982, 932, 84944, 78546)
    relations_need_to_remove([
        (91493, 8),
        (8108, 35866),
        (446, 123207),
        (123207, 27466),
        (123217, 4294),  # 高达 三国
    ])
    print(Subject.select().where(Subject.map.is_null()).count())
    print()
    Subject.update(map=None).execute()
    Relation.update(map=None).execute()
    Map.delete().execute()
    print(Subject.select().where(Subject.map.is_null()).count())
    print()

    # pre_remove_relation()

    from collections import defaultdict

    relations_from_source = defaultdict(list)
    relations_from_target = defaultdict(list)
    relation_from_id = defaultdict(set)
    for edge in Relation.select().where(Relation.removed.is_null() & Relation.map.is_null()):
        relations_from_source[edge.source].append(edge)
        relations_from_target[edge.target].append(edge)
        relation_from_id[edge.source].add(edge)
        relation_from_id[edge.target].add(edge)

    subjects = {}  # type: Dict[int, Subject]
    for s in Subject.select().where((Subject.subject_type != 'Music')):
        subjects[s.id] = s

    def deal_with_node(source_id):
        source_id = int(source_id)
        edges = relation_from_id[source_id]
        map_id = None

        for edge in edges:
            if edge.map:
                map_id = edge.map
                break

        if not map_id:
            m = Map.create()
            map_id = m.id

        for edge in edges:
            if not edge.map:
                if subjects.get(edge.source) and subjects.get(edge.target):
                    edge.map = map_id

        s = subjects.get(source_id)

        if s:
            s.map = map_id

        done_id.add(source_id)

        for edge in edges:
            if subjects.get(edge.target):
                yield edge.target

    worker(list(subjects.keys()), deal_with_node)

    maps = defaultdict(list)
    for s in subjects.values():
        maps[s.map].append(s.id)
    import tqdm

    for map_id, ids in tqdm.tqdm(maps.items(), total=len(maps.keys())):
        if len(ids) >= 300:
            print('warning, map {} size {} is too big, it contains {}'.format(map_id, len(ids), ids[:5]))
        Subject.update(map=map_id).where(Subject.id.in_(ids)).execute()

    maps = defaultdict(set)
    for source, edges in relations_from_source.items():
        s = subjects.get(source)
        if not s:
            continue
        [maps[s.map].add(x.id) for x in edges]

    for source, edges in relations_from_target.items():
        s = subjects.get(source)
        if not s:
            continue
        [maps[s.map].add(x.id) for x in edges]
    for map_id, ids in tqdm.tqdm(maps.items(), total=len(maps.keys())):
        ds = list(ids)
        if len(ids) >= 5000:
            print('warning, map {} is too big, it contains {}'.format(map_id, ds[:5]))
        CHUNK = 5000
        while ds:
            Relation.update(map=map_id).where(Relation.id.in_(ds[:CHUNK])).execute()
            ds = ds[CHUNK:]

    print('finish save to db')


def pre_remove():
    pre_remove_relation()
    nodes_need_to_remove(91493, 102098, 228714, 231982, 932, 84944, 78546)
    relations_need_to_remove([
        (91493, 8),
        (8108, 35866),
        (446, 123207),
        (123207, 27466),
        (123217, 4294),  # 高达 三国
    ])


if __name__ == '__main__':
    pre_remove()
    print(Subject.select().where(Subject.map.is_null()).count())
    print()
    Subject.update(map=None).execute()
    Relation.update(map=None).execute()
    Map.delete().execute()
    print(Subject.select().where(Subject.map.is_null()).count())
    for chunk in range(1, 270000, 5000):
        for item in Subject.select(Subject.id).where((Subject.id > chunk) & (Subject.id <= chunk + 5000)):
            if item.id % 100 == 0:
                print(len(done_id))
            add_new_subject(item.id)
    # add_new_subject(81446)
# http://localhost/subject/81446
