from Constants import app, Session
from flask import render_template, request
from Models import Equipment, Protocol, Institution, IPRange, Keyword, Department

def get_count():
    default = 20
    try:
        count = int(request.args.get('count', default))
        if count < 0:
            raise ValueError
        return count
    except ValueError:
        return default

def get_offset():
    default = 0
    try:
        offset = int(request.args.get('from', default))
        if offset < 0:
            raise ValueError
        return offset
    except ValueError:
        return default

def get_ip():
    ip = request.remote_addr
    return request.args.get('ip', ip)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/aboutus/")
def aboutus():
    return render_template("aboutus.html")

@app.route("/search/")
def search():
    try:
        q = request.args['q']
        count = get_count()
        offset = get_offset()
        s = Session()
        equipment = s.query(Equipment).filter(Equipment.search(q)).limit(count).offset(offset).all()
        protocols = s.query(Protocol).filter(Protocol.search(q)).limit(count).offset(offset).all()
        return render_template("results.html", equipment=equipment, protocols=protocols, q=q)
    except KeyError:
        return render_template("search.html")

@app.route("/upload/")
def upload():
    session = Session()
    ip = get_ip()
    ipr = session.query(IPRange).filter(IPRange.start <= ip).filter(IPRange.finish >= ip).first()
    institution = None
    if ipr:
        institution = session.query(Institution).filter(Institution.ipranges.contains(ipr)).first()
    institutions = session.query(Institution).filter(Institution.university == True)
    companies = session.query(Institution).filter(Institution.university == False)
    if not institution:
        return render_template("no_institution.html", universities=institutions, companies=companies)
    keywords = session.query(Keyword).all()
    departments = session.query(Department).filter(Department.institution == institution)
    return render_template("upload.html", institution=institution, universities=institutions, companies=companies, keywords=keywords, departments=departments)

@app.route("/upload/thankyou/")
def upload_thankyou():
    return render_template("thankyou.html")

@app.route("/help/")
def help():
    return render_template("help.html")

@app.route("/contactus/")
def contactus():
    return render_template("contactus.html")

@app.route("/terms/")
def terms():
    return render_template("terms.html")

@app.route("/tutorial/")
def tutorial():
    return render_template("tutorial.html")