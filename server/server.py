from flask import request
from functools import lru_cache

from flask import Flask, redirect, render_template, url_for, jsonify
from peewee import DoesNotExist, fn
from playhouse.shortcuts import model_to_dict

from bgm.models import Subject, Relation

app = Flask(__name__)


def format_data(data):
    m = {}
    for index, item in enumerate(data['nodes']):
        item['subject_id'] = item['id']
        if item.get('image'):
            # lain.bgm.tv/pic/cover/g/e8/20/935_dOCPc.jpg
            item['image'] = 'https:' + '//' + item['image']
        else:
            item['image'] = 'https://lain.bgm.tv/img/no_icon_subject.png'
        m[item['id']] = index
    edges = []
    for edge in data['edges']:
        if edge['source'] in m and edge['target'] in m:
            edge['source'] = m[edge['source']]
            edge['target'] = m[edge['target']]
            edges.append(edge)
    for index, item in enumerate(data['nodes']):
        item['id'] = index
    data['edges'] = edges
    return data


def get_map_dict(map_id, included_type):
    pass


@app.route('/map/<map_id>.json')
# @lru_cache(1024)
def return_map_json(map_id):
    if (not str.isdecimal(map_id)) or (map_id == '0'):
        return '', 400
    not_type = ["Music", ]
    for key, value in request.args.items():
        key = key.capitalize()
        if key in ["Book", "Anime", "Game", "Real"]:
            if value and value == 'false':
                not_type.append(key)
    subjects = Subject \
        .select(Subject.id, Subject.map, Subject.name, Subject.image, Subject.name_cn) \
        .where((Subject.map == map_id) & (Subject.subject_type.not_in(not_type)))
    relations = Relation.select().where(Relation.map == map_id)
    data = format_data({
        'edges': [model_to_dict(x) for x in relations],
        'nodes': [{'id': x.id, 'name': x.name, 'image': x.image, 'name_cn': x.name_cn} for x in subjects],
    })
    return jsonify(data)


@app.route('/')
def index():
    return render_template('search.html')


from urllib.parse import quote, urlencode


@app.route('/map/<map_id>')
def map_(map_id):
    if (not str.isdecimal(map_id)) or (map_id == '0'):
        return '不是合法的链接'
    p = {}
    for key, value in request.args.items():
        key = key.capitalize()
        if key in ["Book", "Anime", "Game", "Real"]:
            if value and value == 'false':
                p[key] = value
    query_string = urlencode(p)
    return render_template('subject.html', map_id=map_id, qs=query_string)


@app.route('/map_list/<words>')
def map_list_fate(words):
    maps = Subject.select(
        Subject.map,
        fn.COUNT('*').alias('count')
    ).where(Subject.name_cn.contains(words) & (Subject.locked == 0)) \
        .group_by(Subject.map).alias('count') \
        .order_by(-fn.COUNT('*').alias('count')).limit(50)
    return jsonify([{
        'link'       : "http://localhost/map/{}".format(x.map),
        'remote_link': "https://bgm-ip-viewer.trim21.cn/map/{}".format(x.map),
        'map_id'     : x.map,
        'count'      : int(x.count)
    } for x in maps])


@app.route('/map_list')
def map_list():
    maps = Subject.select(
        Subject.map,
        fn.COUNT('*').alias('count')
    ).where(Subject.locked == 0).group_by(Subject.map).alias('count') \
        .order_by(-fn.COUNT('*').alias('count')).limit(50)
    return jsonify([{
        'link'       : "http://localhost/map/{}".format(x.map),
        'remote_link': "https://bgm-ip-viewer.trim21.cn/map/{}".format(x.map),
        'map_id'     : x.map,
        'count'      : int(x.count)
    } for x in maps])


@app.route('/meta_info/subject/<int:subject_id>')
def meta_info_subject(subject_id):
    try:
        s = Subject.get_by_id(subject_id)
    except DoesNotExist:
        return '没找到', 404
    relations = Relation.select().where((Relation.source == s.id)
                                        | (Relation.target == s.id))
    subjects = Subject.select().where(Subject.id.in_([x.source for x in relations] + [x.target for x in relations]))
    # relations=Relation.select().where(Relation.map == map_id)
    data = format_data({
        'edges': [model_to_dict(x) for x in relations],
        'nodes': [{'id': x.id, 'name': x.name, 'image': x.image, 'name_cn': x.name_cn} for x in subjects],
    })
    return render_template('subject-direct-include-data.html', data=data)


@app.route('/subject/<int:subject_id>.json')
def subject_json(subject_id):
    try:
        s = Subject.get_by_id(subject_id)
        if not s.map:
            if s.subject_type == 'Music':
                raise DoesNotExist
            raise DoesNotExist
            # if subject_id not in started_work:
            #     add_new_subject(subject_id)
            # return '还没生成对应的关系图, 过会再来看吧'
        return redirect(url_for('return_map_json', map_id=str(Subject.get_by_id(subject_id).map)))
        # return redirect(url_for('return_map_json', map_id=))
    except DoesNotExist:
        return '没找到', 404
    # return render_template('subject.html', subject=subject)
    # return ''


@app.route('/search')
def search():
    q = request.args.get('q')
    if not q:
        return redirect('/')
    if len(q) > 20:
        return '搜索语句太长'
    s = list(Subject.select().where(Subject.name_cn.contains(q) & Subject.map.is_null(False)).order_by().limit(1))
    if s:
        return redirect(url_for('map_', map_id=s[0].map))
    return '没找到'


@app.route('/subject/<int:subject_id>')
def subject(subject_id):
    try:
        s = Subject.get_by_id(subject_id)
        if not s.map:
            if s.subject_type == 'Music':
                raise DoesNotExist
            raise DoesNotExist
        return redirect(
            url_for('map_', map_id=str(Subject.get_by_id(subject_id).map)) + "?" + request.query_string.decode())
    except DoesNotExist:
        return '没找到', 404


print('server finish initialization')
if __name__ == "__main__":
    app.run(debug=True, port=80, host='0.0.0.0')
