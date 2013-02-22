import types
from flask import jsonify, request, make_response, render_template
from Constants import app, entities, actions, Session
from Models import Entity, Contact, IPRange, Department, Equipment, Institution, Keyword, Protocol
from Errors import APIError, ModelError
from sqlalchemy.exc import IntegrityError, StatementError

def build(classname):
    if classname in globals():
        return globals()[classname]
    raise APIError(Entity.UNKNOWN_ENTITY % classname.lower())

def get_count():
    try:
        count = int(request.args.get('count', 20))
        if count < 0:
            raise ValueError
        return count
    except ValueError:
        raise APIError(Entity.INVALID_COUNT)

def get_offset():
    try:
        offset = int(request.args.get('from', 0))
        if offset < 0:
            raise ValueError
        return offset
    except ValueError:
        raise APIError(Entity.INVALID_FROM)

def get_q(entity):
    q = request.args.get('q')
    if q == None:
        raise APIError(Entity.NO_QUERY % entity)
    return q

def change_labels(json):
    for entity in ['contact','department','institution']:
        if entity in json:
            json['%s_id' % entity] = json[entity]
            del(json[entity])
    return json

def find_keywords(session, json):
    if 'keywords' in json:
        keys = []
        for word in json['keywords']:
            if isinstance(word, basestring):
                k = Keyword(keyword=word)
                session.add(k)
                keys.append(k)
            elif isinstance(word, int):
                k = session.query(Keyword).get(word)
                if k == None:
                    raise APIError("No keyword with id %d" % word)
                keys.append(k)
        json['keywords'] = keys
    return json

def find_ipranges(session, json):
    if 'ipranges' in json:
        ipranges = []
        for iprange in json['ipranges']:
            ipr = IPRange(start=iprange['start'], finish=iprange['finish'])
            session.add(ipr)
            ipranges.append(ipr)
        json['ipranges'] = ipranges
    return json

def get_json():
    if request.json:
        return request.json
    raise APIError('You must send JSON data with a "Content-Type: application/json" header')

@app.route('/api/')
def api_no_entity():
    #return jsonify(error=Entity.NO_ENTITY), 400
    return render_template("api_help.html")

@app.route('/api/<entity>/', methods=['GET'])
def api_no_action(entity):
    return jsonify(error=Entity.NO_ACTION % entity), 400

@app.route('/api/<entity>/', methods=['POST'])
def api_create(entity):
    E = build(entity.title())
    j = get_json()
    try:
        E.validate(j)
        j = change_labels(j)
        session = Session()
        j = find_keywords(session, j)
        j = find_ipranges(session, j)
        e = E(**j)
        session.add(e)
        session.commit()
        response = make_response(jsonify(success="/api/%s/%d/" % (entity, e.id)), 201)
        response.headers['Location'] = "/api/%s/%d/" % (entity, e.id)
        return response
    except ModelError as me:
        return jsonify(error=me.reason), 400
    except IntegrityError as ie: 
        return jsonify(error="Integrity error", e=ie), 400

@app.route('/api/<entity>/<int:id>/', methods=['GET'])
def api_lookup(entity, id):
    E = build(entity.title())
    lookup = Session().query(E).get(id)
    if lookup == None:
        return jsonify(error=Entity.NO_ENTITY_WITH_ID % entity), 404
    return jsonify(result=lookup.to_dict(compact=False))

@app.route('/api/<entity>/<int:id>/', methods=['PUT'])
def api_update(entity, id):
    E = build(entity.title())
    j = get_json()
    try:
        E.validate(j)
        j = change_labels(j)
        session = Session()
        j = find_keywords(session, j)
        j = find_ipranges(session, j)
        altered = session.query(E).get(id)
        if altered == None:
            return jsonify(error=Entity.NO_ENTITY_WITH_ID % entity), 404
        altered.update(j)
        session.commit()
        return jsonify(success=altered.to_dict(compact=False)), 200
    except ModelError as me:
        return jsonify(error=me.reason), 400

@app.route('/api/<entity>/<int:id>/', methods=['DELETE'])
def api_delete(entity, id):
    E = build(entity.title())
    e = Session().query(E).filter(E.id==id).delete()
    return jsonify(success="Deleted"), 200

@app.route('/api/<entity>/list/', methods=['GET'])
def api_list(entity):
    E = build(entity.title())
    count = get_count()
    offset = get_offset()
    return jsonify(result=[r.to_dict(compact=True) for r in Session().query(E).limit(count).offset(offset).all()])

@app.route('/api/<entity>/search/', methods=['GET'])
def api_search(entity):
    E = build(entity.title())
    count = get_count()
    offset = get_offset()
    q = get_q(entity)
    return jsonify(result=[r.to_dict(compact=True) for r in Session().query(E).filter(E.search(q)).limit(count).offset(offset)])

@app.route('/api/<entity>/<action>/', methods=['GET'])
def bad_action(entity, action):
    return jsonify(error=Entity.UNKNOWN_ACTION % entity)

@app.after_request
def after_request(response):
    if request.url[0:5] == '/api/':
        response.mimetype = 'application/json'
    return response

@app.errorhandler(APIError)
def api_error_handler(error):
    return jsonify(error=error.reason), 400