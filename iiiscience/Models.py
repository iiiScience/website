from Constants import entities, actions
from sqlalchemy.orm import relationship, backref
import sqlalchemy.types as types
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, or_, and_, Table
from sqlalchemy.ext.declarative import declarative_base
from Errors import ModelError

Base = declarative_base()

protocol_keywords = Table('protocolkeywords', Base.metadata,
    Column('protocol_id', Integer, ForeignKey('protocol.id', ondelete="CASCADE")),
    Column('keyword_id', Integer, ForeignKey('keyword.id', ondelete="CASCADE"))
)

equipment_keywords = Table('equipmentkeywords', Base.metadata,
    Column('equipment_id', Integer, ForeignKey('equipment.id', ondelete="CASCADE")),
    Column('keyword_id', Integer, ForeignKey('keyword.id', ondelete="CASCADE"))
)

institution_iprange = Table('institutioniprange', Base.metadata,
    Column('institution_id', Integer, ForeignKey('institution.id', ondelete="CASCADE")),
    Column('iprange_id', Integer, ForeignKey('iprange.id', ondelete="CASCADE"))
)

class Entity():
    NO_ENTITY = 'No entity provided. Try using something like this: /api/<entity:%s>/<action:%s>|<id>/' % ('|'.join(entities), '|'.join(actions))
    UNKNOWN_ENTITY = 'Unknown entity; %s. Try using something like this: /api/<entity:%s>/<action:%s>|<id>/' % ('%s', '|'.join(entities), '|'.join(actions))
    NO_ACTION = 'No action provided. Try using something like this: /api/%s/<action:%s>|<id>/' % ('%s', '|'.join(actions))
    UNKNOWN_ACTION = 'Unknown action. Try using something like this: /api/%s/<action:%s>|<id>/' % ('%s', '|'.join(actions))

    BAD_METHOD = "You cannot %s here"

    INVALID_COUNT = 'A count value must be a non-negative integer, the default is 20. A count value controls how many results are sent. Try something like: /api/%s/%s/?count=10'
    INVALID_FROM = 'A from value must be a non-negative integer, the default is 0. A from value controls the offset from the first result. Try something like: /api/%s/%s/?from=2'

    NO_QUERY = 'You haven\'t provided a search query. Try something like: /api/%s/search/?q=<query>'

    NO_ENTITY_WITH_ID = 'There is no entity with that id. Try searching or listing to discover the correct id: /api/%s/search|list/[?q=<query>]'

    @classmethod
    def validate_id(E, args, key, optional = False):
        try:
            id = args[key]
            if isinstance(id, bool) or not isinstance(id, int) or id < 0:
                raise ModelError("%s.%s must be a non-negative integer" % (E.__name__, key))
        except KeyError:
            if not optional:
                raise ModelError("%s must have a %s field" % (E.__name__, key))

    @classmethod
    def validate_boolean(E, args, key, optional = False):
        try:
            boolean = args[key]
            if not isinstance(boolean, bool):
                raise ModelError("%s.%s must be a boolean value" % (E.__name__, key))
        except KeyError:
            if not optional:
                raise ModelError("%s must have a %s field" % (E.__name__, key))

    @classmethod
    def validate_string(E, args, key, optional = False):
        try:
            value = args[key]
            if not isinstance(value, basestring):
                raise ModelError("%s.%s must be a string" % (E.__name__, key))
            max_length = getattr(E, key).property.columns[0].type.length
            if len(value) > max_length:
                raise ModelError("%s.%s cannot be longer than %d characters" % (E.__name__, key, max_length))
        except KeyError:
            if not optional:
                raise ModelError("%s must have a %s field" % (E.__name__, key))

    @classmethod
    def validate_keywords(E, args):
        try:
            keywords = args['keywords']
            if not isinstance(keywords, list):
                raise ModelError("%s.keywords must be a list of keywords or keyword ids" % (E.__name__,))
            for id_or_word in keywords:
                try:
                    int(id_or_word)
                except (ValueError, TypeError):
                    if not isinstance(id_or_word, basestring):
                        raise ModelError("Each %s.keywords must be a string or keyword id" % (E.__name__,))
                    max_length = getattr(Keyword, 'keyword').property.columns[0].type.length
                    if len(id_or_word) > max_length:
                        raise ModelError("Each %s.keywords cannot be longer than %d characters" % (E.__name__, max_length))
        except KeyError:
            raise ModelError("%s must have a list of keywords: ['microscope',...]" % (E.__name__,))

    @classmethod
    def validate_ipranges(E, args):
        try:
            ipranges = args['ipranges']
            if not isinstance(ipranges, list):
                raise ModelError("%s.ipranges must be a list of IP ranges: [{'start:'192.168.0.1', 'finish':'192.168.0.10'},...]" % (E.__name__,))
            for iprange in ipranges:
                if not isinstance(iprange, dict):
                    raise ModelError("%s.ipranges.iprange must be a dictionary containing start and finish IP addresses: {'start:'192.168.0.1', 'finish':'192.168.0.10'}" % (E.__name__,))
                try:
                    start = IP.aton(iprange['start'])
                    finish = IP.aton(iprange['finish'])
                    if start > finish:
                        raise ModelError("%s.ipranges.iprange.start must be less than finish: {'start:'192.168.0.1', 'finish':'192.168.0.10'}" % (E.__name__,))
                except KeyError:
                    raise ModelError("%s.ipranges.iprange must be a dictionary containing start and finish IP addresses: {'start:'192.168.0.1', 'finish':'192.168.0.10'}" % (E.__name__,))
                except (AttributeError, ValueError):
                    raise ModelError("%s.ipranges.iprange.start|finish must be a valid IPv4 address: '192.168.0.1'" % (E.__name__,))
        except KeyError:
            raise ModelError("%s must have a list of ipranges: [{'start:'192.168.0.1', 'finish':'192.168.0.10'},...]" % (E.__name__,))

class IP(types.TypeDecorator):

    @staticmethod
    def aton(address):
        return reduce(lambda x,y: (x<<8) + y, [ int(x) for x in address.split('.') ])

    @staticmethod
    def ntoa(number):
        return "%d.%d.%d.%d" % (number >> 24,(number & 0xffffff) >> 16,(number & 0xffff) >> 8,(number & 0xff))

    impl = types.Integer

    def process_bind_param(self, value, dialect):
        return IP.aton(value)
        
    def process_result_value(self, value, dialect):
        return IP.ntoa(value)

class IPRange(Entity, Base):
    __tablename__ = "iprange"

    id = Column(Integer, primary_key=True)
    start = Column(IP, nullable=False)
    finish = Column(IP, nullable=False)

    def __repr__(self):
        return "<Institution id=%d start=%s finish=%s>" % (self.id, self.start, self.finish)

class Keyword(Entity, Base):
    __tablename__ = "keyword"

    id = Column(Integer, primary_key=True)
    keyword = Column(String(64), nullable=False)

    def update(self, details):
        self.keyword = details['keyword']

    def to_dict(self, compact = True):
        return dict(keyword=dict(id=self.id, keyword=self.keyword))

    def __repr__(self):
        return "<Keyword id=%d %s>" % (self.id, self.keyword)

    def get_search_fields(self):
        return ["keyword"]

    @staticmethod
    def validate(args):
        try:
            Keyword.validate_id(args, "id")
        except ModelError:
            Keyword.validate_id(args, "id", optional = True)
            Keyword.validate_string(args, "keyword")

    @staticmethod
    def search(q):
        return Keyword.keyword.like('%' + q + '%')

class Contact(Entity, Base):
    __tablename__ = "contact"

    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    email = Column(String(256))

    def update(self, details):
        try:
            self.name = details['name']
        except KeyError:
            self.name = None
        try:
            self.email = details['email']
        except KeyError:
            self.email = None

    def get_search_fields(self):
        return ["name", "email"]

    def to_dict(self, compact = True):
        d = dict(id=self.id)
        if self.name:
            d['name'] = self.name
        if self.email:
            d['email'] = self.email
        return dict(contact=d)

    def __repr__(self):
        return "<Contact id=%d name=%s email=%s>" % (self.id, self.name, self.email)

    @staticmethod
    def validate(args):
        try:
            Contact.validate_id(args, "id")
        except ModelError:
            Contact.validate_id(args, "id", optional = True)
            try:
                Contact.validate_string(args, "name")
            except ModelError:
                Contact.validate_string(args, "name", optional=True)
                Contact.validate_string(args, "email", optional=True)

    @staticmethod
    def search(q):
        return or_(Contact.name.like('%' + q + '%'), Contact.email.like('%' + q + '%'))

class Institution(Entity, Base):
    __tablename__ = "institution"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    ipranges = relationship("IPRange", secondary=institution_iprange, backref='institution')
    university = Column(Boolean, nullable=False)

    def update(self, details):
        self.name = details['name']
        if 'ipranges' in details:
            self.ipranges = details['ipranges']
        else:
            self.ipranges = []
        self.university = details['university']

    def get_search_fields(self):
        return ["name"]

    def to_dict(self, compact = True):
        d = dict(id=self.id, name=self.name)
        if not compact:
            d['ipranges'] = [{'start': ipr.start, 'finish':ipr.finish} for ipr in self.ipranges]
            d['university'] = self.university
        return dict(institution=d)

    def __repr__(self):
        return "<Institution id=%d name=%s>" % (self.id, self.name)

    @staticmethod
    def validate(args):
        try:
            Institution.validate_id(args, "id")
        except ModelError:
            Institution.validate_id(args, "id", optional = True)
            Institution.validate_string(args, "name")
            Institution.validate_ipranges(args)
            Institution.validate_boolean(args,"university")

    @staticmethod
    def validate_ip(args, key):
        try:
            ip = args[key]
            parts = ip.split(".")

            if isinstance(id, bool) or not isinstance(id, int) or id < 0:
                raise ModelError("%s.%s must be a non-negative integer" % (E.__name__, key))
        except KeyError:
            if not optional:
                raise ModelError("Institution must have a %s IP" % (key,))  

    @staticmethod
    def search(q):
        return Institution.name.like('%' + q + '%')

class Department(Entity, Base):
    __tablename__ = "department"

    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    institution_id = Column(Integer, ForeignKey('institution.id'), nullable=False)
    institution = relationship(Institution)

    def update(self, details):
        self.name = details['name']
        self.institution_id = details['institution_id']

    def get_search_fields(self):
        return ["name"]

    def to_dict(self, compact = True):
        if compact:
            return dict(department=dict(id=self.id, name=self.name, institution=self.institution_id))
        else:
            return dict(department=dict(id=self.id, name=self.name, institution=self.institution.to_dict()['institution']))

    def __repr__(self):
        return "<Department id=%d name=%s institution=%d>" % (self.id, self.name, self.institution_id)

    @staticmethod
    def validate(args):
        try:
            Department.validate_id(args, "id")
        except ModelError:
            Department.validate_id(args, "id", optional = True)
            Department.validate_string(args, "name")
            Department.validate_id(args, "institution")

    @staticmethod
    def search(q):
        return Department.name.like('%' + q + '%')

class Equipment(Entity, Base):
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    details = Column(String(1024), nullable=False)
    department_id = Column(Integer, ForeignKey('department.id'), nullable=False)
    department = relationship(Department, backref='equipment')
    contact_id = Column(Integer, ForeignKey('contact.id'), nullable=False)
    contact = relationship(Contact, backref='equipment')
    keywords = relationship("Keyword", secondary=equipment_keywords, backref='equipment')

    def update(self, details):
        self.name = details['name']
        self.details = details['details']
        self.department_id = details['department_id']
        self.contact_id = details['contact_id']
        self.keywords = details['keywords']

    def get_search_fields(self):
        return ["name", "details"]

    def to_dict(self, compact = True):
        if compact:
            return dict(equipment=dict(id=self.id, name=self.name, details=self.details, department=self.department_id, contact=self.contact_id))
        else:
            return dict(equipment=dict(id=self.id, 
                        name=self.name, 
                        details=self.details, 
                        department=self.department.to_dict(compact=False)['department'], 
                        contact=self.contact.to_dict()['contact'], 
                        keywords=[k.keyword for k in self.keywords]))

    def __repr__(self):
        return "<Equipment id=%d name=%s>" % (self.id, self.name)

    @staticmethod
    def validate(args):
        try:
            Equipment.validate_id(args, "id")
        except ModelError:
            Equipment.validate_id(args, "id", optional = True)
            Equipment.validate_string(args, "name")
            Equipment.validate_string(args, "details")
            Equipment.validate_id(args, "department")
            Equipment.validate_id(args, "contact")
            Equipment.validate_keywords(args)

    @staticmethod
    def search(q):
        return or_(Equipment.name.like('%' + q + '%'), Equipment.details.like('%' + q + '%'), Equipment.keywords.any(Keyword.keyword.like("%" + q + "%")))

class Protocol(Entity, Base):
    __tablename__ = "protocol"

    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    details = Column(String(1024), nullable=False)
    url = Column(String(1024), nullable=False)
    department_id = Column(Integer, ForeignKey('department.id'), nullable=False)
    department = relationship(Department, backref='protocols')
    contact_id = Column(Integer, ForeignKey('contact.id'), nullable=False)
    contact = relationship(Contact, backref='protocols')
    keywords = relationship("Keyword", secondary=protocol_keywords, backref='protocols')

    def get_search_fields(self):
        return ["name", "details"]

    def to_dict(self, compact = True):
        if compact:
            return dict(protocol=dict(id=self.id, name=self.name, details=self.details, url=self.url, department=self.department_id, contact=self.contact_id))
        else:
            return dict(protocol=dict(id=self.id, 
                        name=self.name, 
                        details=self.details, 
                        url=self.url, 
                        department=self.department.to_dict(compact=False)['department'], 
                        contact=self.contact.to_dict()['contact'],
                        keywords=[k.keyword for k in self.keywords]))

    def __repr__(self):
        return "<Protocol id=%d name=%s>" % (self.id, self.name)

    def update(self, details):
        self.name = details['name']
        self.details = details['details']
        self.url = details['url']
        self.department_id = details['department_id']
        self.contact_id = details['contact_id']
        self.keywords = details['keywords']

    @staticmethod
    def validate(args):
        try:
            Protocol.validate_id(args, "id")
        except ModelError:
            Protocol.validate_id(args, "id", optional = True)
            Protocol.validate_string(args, "name")
            Protocol.validate_string(args, "details")
            Protocol.validate_string(args, "url")
            Protocol.validate_id(args, "department")
            Protocol.validate_id(args, "contact")
            Protocol.validate_keywords(args)

    @staticmethod
    def search(q):
        return or_(Protocol.name.like('%' + q + '%'), Protocol.details.like('%' + q + '%'), Protocol.keywords.any(Keyword.keyword.like("%" + q + "%")))

if __name__ == "__main__":
    from Constants import _engine, Session
    
    Base.metadata.bind = _engine
    Base.metadata.drop_all()
    Base.metadata.create_all(_engine)

    session = Session()

    k1 = Keyword(keyword="alpha")
    k2 = Keyword(keyword="beta")
    ip1 = IPRange(start='0.0.0.0', finish='1.1.1.1')
    ip2 = IPRange(start='2.2.2.2', finish='3.3.3.3')
    ip3 = IPRange(start='4.4.4.4', finish='5.5.5.5')
    c1 = Contact(name="Billy", email="william@iiiscience.com")
    c2 = Contact(name="Toby", email="toby@iiiscience.com")
    i1 = Institution(name="University College London",ipranges=[ip1], university=True)
    i2 = Institution(name="EPSRC",ipranges=[ip2,ip3], university=False)
    d1 = Department(name="Computer Science", institution=i1)
    d2 = Department(name="Materials", institution=i2)
    e1 = Equipment(name="Scanning Electron Microscope", details= "Sees small things using electrons that scan", department=d1, contact=c1, keywords=[k1,k2])
    e2 = Equipment(name="Gold Sputterer", details= "Sputters gold, duh", department=d2, contact=c2, keywords=[k1,k2])
    p1 = Protocol(name="Scanning Electron Microscope Guide", details= "Sees small things using electrons that scan", url= "http://www.example.com", department=d2, contact=c2, keywords=[k1,k2])
    p2 = Protocol(name="Gold Sputterer", details= "Sputters gold, duh", url= "http://www.example.co.uk", department=d2, contact=c2, keywords=[k1])
    session.add(k1)
    session.add(k2)
    session.add(ip1)
    session.add(ip2)
    session.add(ip3)
    session.add(c1)
    session.add(c2)
    session.add(i1)
    session.add(i2)
    session.add(d1)
    session.add(d2)
    session.add(e1)
    session.add(e2)
    session.add(p1)
    session.add(p2)
    session.commit()
