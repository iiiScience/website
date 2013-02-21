import unittest
import json
from iiiscience import Constants
from sqlalchemy import event
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import eagerload

Constants._engine = create_engine('sqlite:///:memory:')
Constants.Session = sessionmaker(bind=Constants._engine)

def _fk_pragma_on_connect(dbapi_con, con_record):
    dbapi_con.execute('pragma foreign_keys=ON')
event.listen(Constants._engine, 'connect', _fk_pragma_on_connect)

from iiiscience import Controller
from iiiscience import APIController
from iiiscience.Models import Entity, IPRange, Contact, Department, Equipment, Institution, Keyword, Protocol, Base

class ControllerTest(unittest.TestCase):

    VALID_ARGS = {
        "contact": [{"name":"Toby", "email":"toby@iiiscience.com"},
                    {"name":"Toby"},
                    {"email":"toby@iiiscience.com"}],
        "institution": [{"name":"University College London","ipranges":[], "university":True},
                        {"name":"University College London","ipranges":[], "university":True},
                        {"name":"University College London","ipranges":[{"start":"0.0.0.0","finish":"1.1.1.1"}], "university":True},
                        {"name":"University College London","ipranges":[{"start":"0.0.0.0","finish":"1.1.1.1"}, {"start":"2.2.2.2","finish":"3.3.3.3"}], "university":True},
                        {"name":"University College London","ipranges":[{"start":"0.0.0.0","finish":"1.1.1.1"}], "university":True},
                        {"name":"Charity College London","ipranges":[{"start":"0.0.0.0","finish":"1.1.1.1"}], "university":False}],
        "keyword": [{"keyword":"beta"}],
        "department": [{"name":"Department of Materials", "institution":1}],
        "equipment": [{"name":"SEM", "details":"details", "department":1, "contact":1, "keywords":["keyword"]},
                      {"name":"SEM", "details":"details", "department":1, "contact":1, "keywords":["keyword1","keyword2"]},
                      {"name":"SEM", "details":"details", "department":1, "contact":1, "keywords":[1]},
                      {"name":"SEM", "details":"details", "department":1, "contact":1, "keywords":[]}],
        "protocol": [{"name":"SEM", "details":"details", "url":"http://example.com", "department":1, "contact":1, "keywords":["keyword"]},
                     {"name":"SEM", "details":"details", "url":"http://example.com", "department":1, "contact":1, "keywords":["keyword1","keyword2"]},
                     {"name":"SEM", "details":"details", "url":"http://example.com", "department":1, "contact":1, "keywords":[1]},
                     {"name":"SEM", "details":"details", "url":"http://example.com", "department":1, "contact":1, "keywords":[]}]
    }

    INVALID_ARGS = {
        "contact": [{"name":"n"*129},
                        {"email":"e"*257},
                        {},
                        {"name":1337},
                        {"name":["name"]},
                        {"name":{"name":"name"}},
                        {"name":True},
                        {"name":None}],
        "institution": [{"name":"n"*65, "university":True,"ipranges":[]},
                        {"university":True,"ipranges":[]},
                        {"name":"name","ipranges":[]},
                        {},
                        {"ipranges":[{"start":"0.0.0.0","finish":"1.1.1.1"}], "university":True},
                        {"name":1337, "university":True,"ipranges":[]},
                        {"name":"name", "university":True},
                        {"name":["name"], "university":True,"ipranges":[]},
                        {"name":{"name":"name"}, "university":True,"ipranges":[]},
                        {"name":True, "university":True,"ipranges":[]},
                        {"name":None, "university":True,"ipranges":[]},
                        {"name":"name","university":1337,"ipranges":[]},
                        {"name":"name","university":[True],"ipranges":[]},
                        {"name":"name","university":{"name":True},"ipranges":[]},
                        {"name":"name","university":"True","ipranges":[]},
                        {"name":"name","university":None,"ipranges":[]},
                        {"name":"name","ipranges":1337, "university":True},
                        {"name":"name","ipranges":"guess", "university":True},
                        {"name":"name","ipranges":True, "university":True},
                        {"name":"name","ipranges":{"start":"0.0.0.0","finish":"1.1.1.1"}, "university":True},
                        {"name":"name","ipranges":[{"start":1,"finish":"1.1.1.1"}], "university":True},
                        {"name":"name","ipranges":[{"start":"0.0.0.0","finish":1}], "university":True},
                        {"name":"name","ipranges":[{"start":"a","finish":"1.1.1.1"}], "university":True},
                        {"name":"name","ipranges":[{"start":"0.0.0.0","finish":"a"}], "university":True},
                        {"name":"name","ipranges":[{"start":True,"finish":"1.1.1.1"}], "university":True},
                        {"name":"name","ipranges":[{"start":"0.0.0.0","finish":True}], "university":True},
                        {"name":"name","ipranges":[{"start":None,"finish":"1.1.1.1"}], "university":True},
                        {"name":"name","ipranges":[{"start":"0.0.0.0","finish":None}], "university":True},
                        {"name":"name","ipranges":[{"start":["0.0.0.0"],"finish":"1.1.1.1"}], "university":True},
                        {"name":"name","ipranges":[{"start":"0.0.0.0","finish":["0.0.0.0"]}], "university":True},
                        {"name":"name","ipranges":[{"start":{"start":"0.0.0.0", "university":True},"finish":"1.1.1.1"}], "university":True},
                        {"name":"name","ipranges":[{"start":"0.0.0.0","finish":{"start":"0.0.0.0"}}], "university":True},
                        {"name":"name","ipranges":[{"start":"1.1.1.1","finish":"0.0.0.0"}], "university":True}],
        "keyword": [{"keyword":"k"*65},
                        {}],
        "department": [{"name":"n"*129, "institution":1},
                        {"institution":1},
                        {"name":"name"},
                        {"name":"name", "institution":"institution"},
                        {"name":"name", "institution":["institution"]},
                        {"name":"name", "institution":{"institution":"institution"}},
                        {"name":"name", "institution":True},
                        {"name":"name", "institution":None},
                        {"name":"Department of Materials", "institution":10000}],
        "equipment": [{"name":"n"*129, "details":"details", "department":1, "contact":1, "keywords":["keyword"]},
                        {"name":"SEM", "details":"details", "department":1, "contact":1},
                        {"name":"SEM", "details":"d"*1025, "department":1, "contact":1, "keywords":["keyword"]},
                        {"details":"details", "department":1, "contact":1, "keywords":["keyword"]},
                        {"name":"SEM", "department":1, "contact":1, "keywords":["keyword"]},
                        {"name":"SEM", "details":"details", "contact":1, "keywords":["keyword"]},
                        {"name":"SEM", "details":"details", "department":1, "keywords":["keyword"]},
                        {"name":"SEM", "details":"details", "department":1, "contact":1, "keywords":"keyword"},
                        {"name":"SEM", "details":"details", "department":1, "contact":1, "keywords":{"keyword":"keyword"}},
                        {"name":"SEM", "details":"details", "department":1, "contact":1, "keywords":1},
                        {"name":"SEM", "details":"details", "department":1, "contact":1, "keywords":True},
                        {"name":"SEM", "details":"details", "department":1, "contact":1, "keywords":None},
                        {"name":"SEM", "details":"details", "department":1, "contact":1, "keywords":[True]},
                        {"name":"SEM", "details":"details", "department":1, "contact":1, "keywords":[None]},
                        {"name":"SEM", "details":"details", "department":1, "contact":1, "keywords":[["keyword"]]},
                        {"name":"SEM", "details":"details", "department":1, "contact":1, "keywords":[{"keyword":"keyword"}]},
                        {"name":"SEM", "details":"details", "department":10000, "contact":1, "keywords":["keyword"]},
                        {"name":"SEM", "details":"details", "department":1, "contact":10000, "keywords":["keyword"]}],
        "protocol": [{"name":"n"*129, "details":"details", "url":"http://example.com", "department":1, "contact":1, "keywords":["keyword"]},
                        {"name":"SEM", "details":"details", "url":"http://example.com", "department":1, "contact":1},
                        {"name":"SEM", "details":"d"*1025, "url":"http://example.com", "department":1, "contact":1, "keywords":["keyword"]},
                        {"name":"SEM", "details":"details", "url":"u"*1025, "department":1, "contact":1, "keywords":["keyword"]},
                        {"name":"SEM", "details":"details", "department":1, "contact":1, "keywords":["k"*65]},
                        {"details":"details", "url":"http://example.com", "department":1, "contact":1, "keywords":["keyword"]},
                        {"name":"SEM", "url":"http://example.com", "department":1, "contact":1, "keywords":["keyword"]},
                        {"name":"SEM", "details":"details", "department":1, "contact":1, "keywords":["keyword"]},
                        {"name":"SEM", "details":"details", "url":"http://example.com", "contact":1, "keywords":["keyword"]},
                        {"name":"SEM", "details":"details", "url":"http://example.com", "department":1, "keywords":["keyword"]},
                        {"name":"SEM", "details":"details", "url":"http://example.com", "department":10000, "contact":1, "keywords":["keyword"]},
                        {"name":"SEM", "details":"details", "url":"http://example.com", "department":1, "contact":10000, "keywords":["keyword"]}]
    }

    def make_contact(self, name="Billy", email="william@iiiscience.com"):
        c = Contact(name=name, email=email)
        self.session.add(c)
        return c

    iprange_count = 0
    def make_iprange(self, start=None, finish=None):
        if start == None or finish == None:
            start = ".".join(["%d" % self.iprange_count for i in range(0,4)])
            self.iprange_count = self.iprange_count + 1
            finish = ".".join(["%d" % self.iprange_count for i in range(0,4)])
        ipr = IPRange(start=start, finish=finish)
        self.session.add(ipr)
        return ipr

    def make_institution(self, name="Imperial College London", ipranges=None, university=True):
        if ipranges == None:
            ipranges = [self.make_iprange(),self.make_iprange()]
        i = Institution(name=name, ipranges=ipranges, university=university)
        self.session.add(i)
        return i

    keyword_count = 0
    def make_keyword(self, keyword="alpha"):
        if keyword == "alpha":
            keyword = "alpha%d" % self.keyword_count
            self.keyword_count = self.keyword_count + 1
        k = Keyword(keyword=keyword)
        self.session.add(k)
        return k

    def make_department(self, name="Department of Computer Science", institution=None):
        if institution == None:
            institution = self.make_institution()
        d = Department(name=name, institution=institution)
        self.session.add(d)
        return d

    def make_equipment(self, name="Gold Sputterer", details="Custom thin film sputterer for graphene growth.", department=None, contact=None, keywords=None):
        if department == None:
            department = self.make_department()
        if contact == None:
            contact = self.make_contact()
        if keywords == None:
            keywords = [self.make_keyword(), self.make_keyword()]
        e = Equipment(name=name, details=details, department=department, contact=contact, keywords=keywords)
        self.session.add(e)
        return e

    def make_protocol(self, name="Gold Sputterer Instructions", details="How to use a GS.", url="http://www.example.com", department=None, contact=None, keywords=None):
        if department == None:
            department = self.make_department()
        if contact == None:
            contact = self.make_contact()
        if keywords == None:
            keywords = [self.make_keyword(), self.make_keyword()]
        p = Protocol(name=name, details=details, department=department, contact=contact, keywords=keywords, url=url)
        self.session.add(p)
        return p

    def fill(self, entity):
        try:
            entity.contact
        except AttributeError:
            pass
        try:
            entity.institution
        except AttributeError:
            pass
        try:
            for k in entity.keywords:
                pass
        except AttributeError:
            pass
        try:
            for ipr in entity.ipranges:
                pass
        except AttributeError:
            pass
        try:
            entity.department
        except AttributeError:
            pass
        return entity

    def setUp(self):
        Constants.app.config['TESTING'] = True
        self.app = Constants.app.test_client()
        Base.metadata.create_all(Constants._engine)
        self.session = Constants.Session()

    def tearDown(self):
        self.session.rollback()
        Base.metadata.bind = Constants._engine
        Base.metadata.drop_all()
        
    def get_json(self, url):
        return json.loads(self.app.get(url).data)

    def populate(self, entityname, count = 20):
        for x in xrange(0,count):
            getattr(self, "make_%s" % entityname)()
        self.session.commit()

    def test_api_noentity(self):
        # removed whilst /api points to html page
        #self.assertEquals(self.get_json('/api/'), {'error':Entity.NO_ENTITY})
        pass

    def test_api_badentity(self):
        for a in Constants.actions:
            self.assertEquals(self.get_json('/api/badbadbad/%s/' % a), {'error':Entity.UNKNOWN_ENTITY % 'badbadbad'})

    def test_api_entity_noaction(self):
        for e in Constants.entities:
            self.assertEquals(self.get_json('/api/%s/' % e), {'error':Entity.NO_ACTION % e})

    def test_api_entity_badaction(self):
        for e in Constants.entities:
            self.assertEquals(self.get_json('/api/%s/badbadbad/' % e), {'error':Entity.UNKNOWN_ACTION % e})

    def test_api_entity_list_empty(self):
        for e in Constants.entities:
            r = self.get_json('/api/%s/list/' % e)
            self.assertTrue('result' in r)
            self.assertEquals(len(r['result']), 0)

    def test_api_entity_list_full(self):
        for e in Constants.entities:
            self.populate(e, 20)
            r = self.get_json('/api/%s/list/' % e)
            self.assertTrue('result' in r)
            self.assertEquals(len(r['result']), 20)

    def test_api_entity_list_count0(self):
        for e in Constants.entities:
            self.populate(e, 20)
            r = self.get_json('/api/%s/list/?count=0' % e)
            self.assertTrue('result' in r)
            self.assertEquals(len(r['result']), 0)

    def test_api_entity_list_count10(self):
        for e in Constants.entities:
            self.populate(e, 20)
            r = self.get_json('/api/%s/list/?count=10' % e)
            self.assertTrue('result' in r)
            self.assertEquals(len(r['result']), 10)

    def test_api_entity_list_countdefault(self):
        for e in Constants.entities:
            self.populate(e, 30)
            r = self.get_json('/api/%s/list/' % e)
            self.assertTrue('result' in r)
            self.assertEquals(len(r['result']), 20)

    def test_api_entity_list_count30(self):
        for e in Constants.entities:
            self.populate(e, 20)
            r = self.get_json('/api/%s/list/?count=30' % e)
            self.assertTrue('result' in r)
            self.assertEquals(len(r['result']), 20)

    def test_api_entity_list_countnegative(self):
        for e in Constants.entities:
            self.populate(e, 5)
            r = self.get_json('/api/%s/list/?count=-1' % e)
            self.assertTrue('error' in r)
            self.assertEquals(r['error'], Entity.INVALID_COUNT)

    def test_api_entity_list_countnonnumber(self):
        for e in Constants.entities:
            self.populate(e, 5)
            r = self.get_json('/api/%s/list/?count=foo' % e)
            self.assertTrue('error' in r)
            self.assertEquals(r['error'], Entity.INVALID_COUNT)

    def test_api_entity_list_from_default(self):
        for e in Constants.entities:
            self.populate(e, 5)
            f0c1 = self.get_json('/api/%s/list/?from=0&count=1' % e)
            c1 = self.get_json('/api/%s/list/?count=1' % e)
            self.assertEqual(f0c1['result'], c1['result'])

    def test_api_entity_list_from_different(self):
        for e in Constants.entities:
            self.populate(e, 5)
            r0 = self.get_json('/api/%s/list/?from=0&count=1' % e)
            self.assertTrue('result' in r0)
            r1 = self.get_json('/api/%s/list/?from=1&count=1' % e)
            self.assertTrue('result' in r1)
            self.assertNotEqual(r0['result'], r1['result'])

    def test_api_entity_list_from_inorder(self):
        for e in Constants.entities:
            self.populate(e, 5)
            f0c2 = self.get_json('/api/%s/list/?from=0&count=2' % e)
            f0c1 = self.get_json('/api/%s/list/?from=0&count=1' % e)
            f1c1 = self.get_json('/api/%s/list/?from=1&count=1' % e)
            self.assertEqual(f0c2['result'][0], f0c1['result'][0])
            self.assertEqual(f0c2['result'][1], f1c1['result'][0])

    def test_api_entity_list_from_toobig(self):
        for e in Constants.entities:
            self.populate(e, 1)
            f0 = self.get_json('/api/%s/list/?from=0' % e)
            f1 = self.get_json('/api/%s/list/?from=1' % e)
            f2 = self.get_json('/api/%s/list/?from=2' % e)
            self.assertEqual(len(f0['result']), 1)
            self.assertEqual(len(f1['result']), 0)
            self.assertEqual(len(f2['result']), 0)

    def test_api_entity_search_noquery(self):
        for e in Constants.entities:
            r = self.get_json('/api/%s/search/' % e)
            self.assertEquals(r['error'], Entity.NO_QUERY % e)

    def test_api_entity_search_empty(self):
        for e in Constants.entities:
            r = self.get_json('/api/%s/search/?q=a' % e)
            self.assertTrue('result' in r)
            self.assertEquals(len(r['result']), 0)

    def test_api_entity_search_findsomething(self):
        for e in Constants.entities:
            entity = getattr(self, "make_%s" % e)()
            self.populate(e, 5)
            args = {}
            for field in entity.get_search_fields():
                args[field] = "test search"
                entity = getattr(self, "make_%s" % e)(**args)
                self.session.commit()
                dentity = entity.to_dict()
                r = self.get_json('/api/%s/search/?q=t+s' % e)
                found = False
                for result in r['result']:
                    if dentity == result:
                        found = True
                        break
                self.assertTrue(found)

    def test_api_entity_search_count0(self):
        for e in Constants.entities:
            self.populate(e, 20)
            r = self.get_json('/api/%s/search/?q=a&count=0' % e)
            self.assertTrue('result' in r)
            self.assertEquals(len(r['result']), 0)

    def test_api_entity_search_count10(self):
        for e in Constants.entities:
            self.populate(e, 20)
            r = self.get_json('/api/%s/search/?q=a&count=10' % e)
            self.assertTrue('result' in r)
            self.assertEquals(len(r['result']), 10)

    def test_api_entity_search_countdefault(self):
        for e in Constants.entities:
            self.populate(e, 30)
            r = self.get_json('/api/%s/search/?q=a' % e)
            self.assertTrue('result' in r)
            self.assertEquals(len(r['result']), 20)

    def test_api_entity_search_count30(self):
        for e in Constants.entities:
            self.populate(e, 20)
            r = self.get_json('/api/%s/search/?q=a&count=30' % e)
            self.assertTrue('result' in r)
            self.assertNotEqual(len(r['result']), 30)

    def test_api_entity_search_countnegative(self):
        for e in Constants.entities:
            self.populate(e, 5)
            r = self.get_json('/api/%s/search/?q=a&count=-1' % e)
            self.assertTrue('error' in r)
            self.assertEquals(r['error'], Entity.INVALID_COUNT)

    def test_api_entity_search_countnonnumber(self):
        for e in Constants.entities:
            self.populate(e, 5)
            r = self.get_json('/api/%s/search/?q=a&count=foo' % e)
            self.assertTrue('error' in r)
            self.assertEquals(r['error'], Entity.INVALID_COUNT)

    def test_api_entity_search_from_default(self):
        for e in Constants.entities:
            self.populate(e, 5)
            f0c1 = self.get_json('/api/%s/search/?q=a&from=0&count=1' % e)
            c1 = self.get_json('/api/%s/search/?q=a&count=1' % e)
            self.assertEqual(f0c1['result'], c1['result'])

    def test_api_entity_search_from_different(self):
        for e in Constants.entities:
            self.populate(e, 5)
            r0 = self.get_json('/api/%s/search/?q=a&from=0&count=1' % e)
            self.assertTrue('result' in r0)
            r1 = self.get_json('/api/%s/search/?q=a&from=1&count=1' % e)
            self.assertTrue('result' in r1)
            self.assertNotEqual(r0['result'], r1['result'])

    def test_api_entity_search_from_inorder(self):
        for e in Constants.entities:
            self.populate(e, 5)
            f0c2 = self.get_json('/api/%s/search/?q=a&from=0&count=2' % e)
            f0c1 = self.get_json('/api/%s/search/?q=a&from=0&count=1' % e)
            f1c1 = self.get_json('/api/%s/search/?q=a&from=1&count=1' % e)
            self.assertEqual(f0c2['result'][0], f0c1['result'][0])
            self.assertEqual(f0c2['result'][1], f1c1['result'][0])

    def test_api_entity_search_from_toobig(self):
        for e in Constants.entities:
            self.populate(e, 1)
            f0 = self.get_json('/api/%s/search/?q=a&from=0' % e)
            f1 = self.get_json('/api/%s/search/?q=a&from=1' % e)
            f2 = self.get_json('/api/%s/search/?q=a&from=2' % e)
            self.assertEqual(len(f0['result']), 1)
            self.assertEqual(len(f1['result']), 0)
            self.assertEqual(len(f2['result']), 0)

    def test_api_equipment_and_protocol_search_bykeyword(self):
        for e in ['equipment', 'protocol']:
            self.populate(e, 1)
            salpha = self.get_json('/api/%s/search/?q=alpha' % e)
            self.assertEqual(len(salpha['result']), 1)
            self.assertEqual(salpha['result'][0][e]['id'], 1, salpha['result'])

    def test_api_entity_lookup(self):
        for e in Constants.entities:
            self.populate(e, 5)
            listed = self.get_json('/api/%s/list/' % e)
            for entity in listed['result']:
                id = entity[e]['id']
                lookup = self.get_json('/api/%s/%d/' % (e, id))['result'][e]
                get = self.session.query(APIController.build(e.title())).get(id)
                self.assertEquals(get.to_dict(compact=False)[e], lookup)

    def test_api_entity_lookup_noid(self):
        for e in Constants.entities:
            self.populate(e, 1)
            lookup = self.get_json('/api/%s/10/' % e)
            self.assertEquals(lookup['error'], Entity.NO_ENTITY_WITH_ID % e)

    def find_differences(self, one, two):
        difference = []
        for e1 in one:
            found = False
            for e2 in two:
                if e1['id'] == e2['id']:
                    found = True
            if not found:
                difference.append(e1)
        for e1 in two:
            found = False
            for e2 in one:
                if e1['id'] == e2['id']:
                    found = True
            if not found:
                if e1 not in difference:
                    difference.append(e1)
        return difference

    def are_equal(self, one, two):
        equal = True
        try: equal = one.id == two.id
        except: pass
        try: equal = one.name == two.name
        except: pass    
        try: equal = one.details == two.details
        except: pass
        try: equal = one.url == two.url
        except: pass
        try: equal = one.email == two.email
        except: pass
        try: equal = one.keyword == two.keyword
        except: pass
        try: equal = one.contact == two.contact
        except: pass
        try: equal = one.institution == two.institution
        except: pass
        try: equal = one.department == two.department
        except: pass
        return equal
    
    def test_api_entity_create_valid(self):
        for etype in self.VALID_ARGS:
            self.populate(etype, 1)
            for valid in self.VALID_ARGS[etype]:
                json_data = json.dumps(valid)
                before = self.get_json('/api/%s/list/' % etype)
                r = self.app.post('/api/%s/' % etype, content_type='application/json', data=json_data)
                after = self.get_json('/api/%s/list/' % etype)
                difference = self.find_differences([b[etype] for b in before['result']], [a[etype] for a in after['result']])
                self.assertEquals(len(difference), 1, (json_data, r.data))
                self.assertEqual(r.status_code, 201)
                self.assertTrue(self.are_equal(difference[0], valid))

    def test_api_entity_create_invalid(self):
        for etype in self.INVALID_ARGS:
            for invalid in self.INVALID_ARGS[etype]:
                json_data = json.dumps(invalid)
                r = self.app.post('/api/%s/' % etype, content_type='application/json', data=json_data)
                r.json = json.loads(r.data)
                self.assertTrue('error' in r.json, (json_data, r.json))
                self.assertEqual(r.status_code, 400)

    def test_api_entity_update_valid(self):
        for e in Constants.entities:
            self.populate(e, 2)
            orig = self.get_json('/api/%s/list/' % e)['result'][0][e]
            for altered in self.VALID_ARGS[e]:
                url = '/api/%s/%d/' % (e, orig['id'])
                r = self.app.put(url, data=json.dumps(altered), content_type='application/json')
                get = self.get_json(url)
                get = get['result'][e]
                for subentity in [se for se in Constants.entities if se != "keyword"]:
                    if subentity in get.keys():
                        get[subentity] = get[subentity]['id']
                altered['id'] = orig['id']
                if 'keywords' in altered:
                    keywords = []
                    for k in altered['keywords']:
                        if isinstance(k, int):
                            k = self.get_json("/api/keyword/%d/" % k)['result']['keyword']['keyword']
                        keywords.append(k)
                    altered['keywords'] = keywords
                self.assertEqual(r.status_code, 200, (altered, r.data))
                self.assertEqual(altered, get)

    def test_api_entity_update_invalid(self):
        for e in Constants.entities:
            self.populate(e,2)
            orig = self.get_json('/api/%s/list/' % e)['result'][0][e]
            altered = self.INVALID_ARGS[e][0]
            r = self.app.put('/api/%s/%d/' % (e, orig['id']), data=json.dumps(altered), content_type='application/json')
            self.assertEqual(r.status_code, 400, (altered, r.data))
            j = json.loads(r.data)
            self.assertTrue('error' in j)

    def test_api_entity_update_noid(self):
        for e in Constants.entities:
            altered = self.VALID_ARGS[e][0]
            r = self.app.put('/api/%s/1/' % e, data=json.dumps(altered), content_type='application/json')
            self.assertEqual(r.status_code, 404, (altered, r.data))
            j = json.loads(r.data)
            self.assertTrue('error' in j)            

    def test_api_entity_delete_missing(self):
        for e in Constants.entities:
            self.populate(e,2)
            orig = self.get_json('/api/%s/list/' % e)['result']
            r = self.app.delete('/api/%s/%d/' % (e, orig[0][e]['id']))
            altered = self.get_json('/api/%s/list/' % e)['result']
            self.assertNotEqual(len(orig),len(altered))
            self.assertNotEqual(altered[0][e]['id'],orig[0][e]['id'])

    def test_api_entity_delete_notid(self): 
        for e in Constants.entities:
            r = self.app.delete('/api/%s/1/')
            j = json.loads(r.data)
            self.assertTrue('error' in j)

