from flask import Flask,render_template,jsonify,request,session,redirect,url_for
from models import *
from werkzeug.security import generate_password_hash,check_password_hash
from flask_migrate import Migrate
from flask_msearch import Search
from jieba.analyse import ChineseAnalyzer
import random


class Config(object):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///buaa.db';
    SQLALCHEMY_TRACK_MODIFICATIONS = False;
    MSEARCH_BACKEND = 'whoosh';
    MSERACH_ENABLE = True;


app = Flask(__name__)
app.secret_key = "d2035615-674e-4b0a-93e8-89a974f9b94e"
app.config.from_object(Config)
db.init_app(app)

search = Search(app,db)
migrate = Migrate(app,db,ChineseAnalyzer())


def dump_q(q:SQ):
    d = {"id":q.id,"question":q.QUESTION,"A":q.A,"B":q.B,"C":q.C,"D":q.D,"answer":q.ANSWER,"chapter":q.CHAPTER,"type":q.TYPE}
    if q.IMAGENUM:d["image"] = "/static/pics/n" + q.IMAGENUM[:-3]+'png'
    return d


@app.route("/login_front")
def login_front():
    return render_template("login.html")


@app.route('/')
def index():
    is_art = request.args.get("is_art")
    print(is_art,type(is_art))
    if is_art is None:
        return "",404
    if is_art == '1':
        is_art = 1
    elif is_art == '0':
        is_art = 0
    return render_template("navbar-static-top.html",is_art=is_art)


@app.route("/index")
def new_index():
    username = session.get("username")
    return render_template("index.html",username=username,login_url=url_for('login_front'))


@app.route("/search")
def search_front():
    return render_template("search.html")


# rest
@app.route("/get_question_by_id",methods=["POST","GET"])
def get_question_by_id():
    qid = request.args.get("qid")
    is_art = request.args.get("is_art")
    if is_art is None:
        return jsonify({"msg":"No is_art."}),400
    if qid is None:
        return jsonify({"msg":"No qid."}),400
    if is_art == '1':
        Q = AQ
    elif is_art == '0':
        Q = SQ
    try:
        qid = int(qid)
        q = Q.query.get(qid);
        if q is None: raise Exception;
        return jsonify(dump_q(q))
    except Exception as e:
        print(e)
        return jsonify({"msg":"try again."}),400


@app.route("/login",methods=["POST","GET"])
def login():
    name = request.args.get("name")
    print("name:",name)
    pwd = request.args.get("pwd")
    print("pwd:",pwd)
    if name and pwd:
        u = User.query.filter_by(name=name).all()
        print(u)
        if len(u)==1:
            u = u[0]
            if check_password_hash(u.pwd_hash,pwd):
                session["login"] = True;
                session["username"] = u.name;
                session["uid"] = u.id;
            else:
                return redirect(url_for('new_index'))
        else:
            u = User(name=name,pwd_hash=generate_password_hash(pwd))
            try:
                db.session.add(u)
                db.session.commit()
                session["login"] = True;
                session["username"] = u.name;
                session["uid"] = u.id;
                return redirect(url_for('new_index'))
            except Exception as e:
                print(e)
                return redirect(url_for('new_index'))
    return redirect(url_for("new_index"))


@app.route("/search_api",methods=["POST","GET"])
def search_api():
    kw = request.args.get("kw")
    if kw is None:return "",404
    q = SQ.query.msearch(kw).all()
    q.extend(AQ.query.msearch(kw).all())
    q = [dump_q_for_search(i) for i in q]
    return jsonify(q)


def dump_q_for_search(q):
    d = dump_q(q)
    if type(q) is SQ:
        d["is_art"] = False
    if type(q) is AQ:
        d["is_art"] = True
    return d


@app.route("/wrong")
def wrong_review():
    is_art = request.args.get("is_art")
    if is_art is None:
        return "",404
    u_id = session.get("uid")
    if u_id is None:
        return "您没有登录!",403
    u = User.query.get(u_id)
    if is_art == "1":
        q = u.art_wrong
    elif is_art == '0':
        q = u.sci_wrong
    q = [dump_q(i) for i in q]
    q.sort(key=lambda q:q['id'])
    return render_template("wrong.html", is_art=int(is_art),username=u.name,questions=q)


@app.route("/wrong_api")
def wrong_api():
    is_art = request.args.get("is_art")
    if is_art is None:
        return jsonify({"code":400})
    if is_art == '1':
        Q = AQ
    elif is_art == '0':
        Q = SQ
    else:
        return jsonify({"code":400})
    wrongs = request.args.get("wrongs")
    print(wrongs)
    if wrongs is None: return jsonify({"code":400})
    if session.get("uid") is None: return jsonify({"code":403})
    u_id = session.get("uid")
    u = User.query.get(int(u_id))
    wrongs = [Q.query.get(int(i)) for i in wrongs.split(',')]
    try:
        if is_art == '1':
            # u.art_wrong.extend(wrongs)
            for i in wrongs:
                if i not in u.art_wrong:
                    u.art_wrong.append(i)
        elif is_art == '0':
            # u.sci_wrong.extend(wrongs)
            for i in wrongs:
                if i not in u.sci_wrong:
                    u.sci_wrong.append(i)
        db.session.commit()
        return jsonify({"code":200})
    except Exception as e:
        print(e)
        return jsonify({"code":500})


@app.route("/test",methods=["POST","GET"])
def test_front():
    is_art = request.args.get("is_art")
    return render_template("test.html",is_art=is_art)


@app.route("/test_set",methods=["POST","GET"])
def test_set():
    is_art = request.args.get("is_art")
    if is_art is None:
        return "",404
    if is_art == '1':
        Q = AQ;
    elif is_art == '0':
        Q = SQ;
    else:
        return "",404
    single = Q.query.filter_by(TYPE=1).all();
    mul = Q.query.filter_by(TYPE=2).all();
    ps = random.choices(single,k=70)
    ps.extend(random.choices(mul,k=15))
    ps = [dump_q(i) for i in ps]
    return jsonify(ps);


@app.route("/wrong_clear")
def wrong_clear():
    is_art = request.args.get("is_art")
    if is_art is None:
        return  "",404
    u_id = session.get("uid")
    if u_id is None:
        return "",404
    u = User.query.get(int(u_id))
    if is_art == "1":
        u.art_wrong.clear()
    if is_art == '0':
        u.sci_wrong.clear()
    try:
        db.session.commit()
        return jsonify({"code":200})
    except Exception as e:
        print(e)
        return jsonify({"code":500})


@app.route("/wrong_remove")
def wrong_remove():
    is_art = request.args.get("is_art")
    if is_art is None: return "",404
    qid = request.args.get("qid")
    if qid is None: return "", 403
    qid = int(qid)
    if is_art == '1':
        Q = AQ
    elif is_art == '0':
        Q = SQ
    else:
        return "",403
    q = Q.query.get(qid)
    if q is None:
        return "",403
    uid = session.get("uid")
    if uid is None:
        return "",403
    u = User.query.get(uid)
    try:
        if is_art == '1':
            if q in u.art_wrong:
                u.art_wrong.remove(q)
            else:
                return "",200
        elif is_art == '0':
            if q in u.sci_wrong:
                u.sci_wrong.remove(q)
            else:
                return "",200
        db.session.commit()
        return jsonify({"code":200})
    except Exception as e:
        print(e)
        return "",500


if __name__ == '__main__':
    app.run(debug=1)
