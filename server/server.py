from flask import request

from flask import Flask, render_template, jsonify
from peewee import DoesNotExist
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


@app.route('/map/<map_id>.json')
def return_map_json(map_id):
    if (not str.isdecimal(map_id)) or (map_id == '0'):
        return '', 400
    not_type = [
        "Music",
    ]
    for key, value in request.args.items():
        key = key.capitalize()
        if key in ["Book", "Anime", "Game", "Real"]:
            if value and value == 'false':
                not_type.append(key)
    subjects = Subject.select(
        Subject.id, Subject.map, Subject.name, Subject.image, Subject.name_cn,
        Subject.info, Subject.subject_type
    ).where((Subject.map == map_id) & (Subject.subject_type.not_in(not_type)))
    relations = Relation.select().where(Relation.map == map_id)
    data = format_data({
        'edges': [model_to_dict(x) for x in relations],
        'nodes': [{
            'id': x.id,
            'name': x.name,
            'image': x.image,
            'name_cn': x.name_cn,
            'begin': x.info.get("放送开始", [x.info.get('发售日', [None])[0]])[0],
            'subject_type': x.subject_type.lower(),
        } for x in subjects],
    })
    return jsonify(data)


@app.route('/')
def index():
    return render_template('search.html')


@app.route('/subject/<int:subject_id>.json')
def subject_json(subject_id):
    try:
        s = Subject.get_by_id(subject_id)
        if not s.map:
            if s.subject_type == 'Music':
                raise DoesNotExist
            raise DoesNotExist
        return return_map_json(map_id=str(Subject.get_by_id(subject_id).map))
    except DoesNotExist:
        return '没找到', 404


@app.route('/subject/<int:subject_id>')
def subject(subject_id):
    return render_template('subject.html', subject_id=subject_id)


print('server finish initialization')
if __name__ == "__main__":
    app.run(debug=True, port=80, host='0.0.0.0')
