from flask import Flask, render_template, redirect, request
import csv
import collections
import psycopg2 as pg
import psycopg2.extras

app = Flask(__name__)

session = { 'sid': None, 'sname': None }

db_connector = {
    'host': 'localhost',
    'user': 'postgres',
    'dbname': 'dbapp',
    'port': '5432',
    'password': 'thdqhtjr12'
}

connect_string = "host={host} user={user} dbname = {dbname} password = {password}, port={port}".format(**db_connector)

@app.route("/")
def index():
    #print(session)
    return render_template("index.html", session=session)

@app.route("/mailbox")
def mailbox():
    return redirect("/")

@app.route("/logout")
def logout():
    session['sid'] = None
    session['sname'] = None
    return redirect('/')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")

    sid = request.form.get('sid')
    passwd = request.form.get('passwd')

    if sid == 'admin':
        if passwd == 'admin':
            session['sid'] = sid
            session['sname'] = sid
        else:
            return render_template('login.html', msg="Wrong PW")

        return redirect('/')
    else:
        with pg.connect(connect_string) as conn:
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            sql = f"select sid, sname from students where sid='{sid}' and password='{passwd}'"

            cur.execute(sql)
            rows = cur.fetchall()
            if len(rows) != 1:
                return render_template('login.html', msg="Wrong ID or Wrong Password")
            print(rows[0])

        session['sid'] = rows[0]['sid']
        session['sname'] = rows[0]['sname']
        return redirect('/')

@app.route("/admin/hyucontacts")
def hyucontacts():
    if session['sid'] != "admin":
        return redirect('/')

    with pg.connect(connect_string) as conn:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        sql = f"select s.sname, c.* from hyu_contacts c, students s where c.sid = s.sid"

        cur.execute(sql)
        contacts_list = cur.fetchall()

        hyu_header = ["name", "sid", "phone", "email"]
        hyu_contacts = []

        print(contacts_list)

        if(len(contacts_list[0]) == 5):
            for c in contacts_list:
                tmp_list = c[0:3]
                email = c['local_part'] + "@" + c['domain_part']
                tmp_list.append(email)
                print(tmp_list)
                hyu_contacts.append(tmp_list)
        else:
            hyu_contacts = contacts_list

        header = ["owner", "name", "phone", "email", "position"]
        sql = f"select * from personal_contacts"
        cur.execute(sql)
        contacts = cur.fetchall()

    return render_template('hyucontacts.html', hyu_header = hyu_header, header=header, hyu_contacts=hyu_contacts, contacts = contacts, session=session)


@app.route("/admin/hyucontacts/edit", methods=["GET", "POST"])
def hyucontacts_edit():
    if session['sid'] != "admin":
        return redirect('/')

    if request.method == 'GET':
        info = request.args
        return render_template("edit.html", info=info)
    else:
        mode = request.form.get("mode")

        if mode == "delete": #delete
            print("delete")
            sid = request.form.get("sid")

            with pg.connect(connect_string) as conn:
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                sql = f"delete from hyu_contacts where sid = '{sid}'"
                cur.execute(sql)
                conn.commit()

            return redirect("/admin/hyucontacts")

        else:
            print("edit")
            sid = request.form.get("sid")
            phone = request.form.get("phone")
            email = request.form.get("email")
            #local_part, domain_part = request.form.get("email").split("@")

            print(sid, phone, email)

            if len(sid) == 0 and len(phone) == 0 and len(email) == 0:
                return redirect("/admin/hyucontacts")
            else:
                with pg.connect(connect_string) as conn:
                    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                    sql = "select * from hyu_contacts"
                    cur.execute(sql)
                    contacts_list = cur.fetchall()


                    if len(contacts_list[0]) == 4:
                        if mode == "edit":
                            sql = "update hyu_contacts set phone = '{0}', local_part = '{1}', domain_part = '{2}' where sid = '{3}'".format(phone, email.split("@")[0], email.split("@")[1], sid)
                            cur.execute(sql)
                            conn.commit()

                        elif mode == "add":
                            try:
                                sql = "insert into hyu_contacts select '{0}', '{1}', '{2}', '{3}' where exists (select * from students where sid = '{4}')".format(sid, phone, email.split("@")[0], email.split("@")[1], sid)
                                cur.execute(sql)
                                conn.commit()
                            except:
                                return redirect("/admin/hyucontacts")

                    else:
                        if mode == "edit":
                            sql = f"update hyu_contacts set phone = '{phone}', email = '{email}' where sid = '{sid}'"
                            cur.execute(sql)
                            conn.commit()

                        elif mode == "add":
                            try:
                                sql = f"insert into hyu_contacts select '{sid}', '{phone}', '{email}' where exists (select * from students where sid = '{sid}')"
                                cur.execute(sql)
                                conn.commit()
                            except Exception:
                                return redirect("/admin/hyucontacts")

                return redirect("/admin/hyucontacts")


@app.route("/admin/statistics")
def statistics():
    if session['sid'] != "admin":
        return redirect('/')

    with pg.connect(connect_string) as conn:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        sql = f"select c.* from hyu_contacts c"

        cur.execute(sql)
        contacts_list = cur.fetchall()

    print(contacts_list)
    if(len(contacts_list[0]) == 4):
        pass
    else:
        sql = "alter table hyu_contacts drop column email"
        cur.execute(sql)
        sql = "alter table hyu_contacts add column local_part varchar, add column domain_part varchar"
        cur.execute(sql)
        conn.commit()

        for row in contacts_list:
            sql = "update hyu_contacts set local_part = '{0}', domain_part = '{1}' where sid = '{2}'".format(row['email'].split("@")[0], row['email'].split("@")[1], row['sid'])
            cur.execute(sql)

        conn.commit()

    sql = "select domain_part, count(*) from hyu_contacts group by domain_part"
    cur.execute(sql)
    email = cur.fetchall()

    return render_template('statistics.html', email=email)


@app.route("/admin/useradd", methods=["GET", "POST"])
def useradd():
    if session['sid'] != "admin":
        return redirect('/')

    if request.method == "GET":
        return render_template("useradd.html")
    else:
        with pg.connect(connect_string) as conn:
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            sid = request.form.get("sid")
            passwd = request.form.get("passwd")
            sname = request.form.get("sname")
            sex = request.form.get("sex")
            major_id = request.form.get("major_id")
            tutor_id = request.form.get("tutor_id")
            grade = request.form.get("grade")
            print(sid, passwd, sname, sex)

            sql = "select * from students"
            cur.execute(sql)
            students_list = cur.fetchall()

            for row in students_list:
                print(row['sid'], sid)
                if row['sid'] == sid:
                    return render_template("useradd.html", session=session, msg="same student is in the list")

            sql = f"insert into students (sid, password, sname, sex, major_id, tutor_id, grade) values ('{sid}', '{passwd}', '{sname}', '{sex}', '{major_id}', '{tutor_id}', '{grade}')"
            cur.execute(sql)
            conn.commit()

        return redirect("/")

@app.route("/contacts")
def contacts():
    if session['sid'] == None:
        return redirect('/')

    with pg.connect(connect_string) as conn:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        sql = f"select s.sname, c.* from hyu_contacts c, students s where c.sid = s.sid"

        cur.execute(sql)
        contacts_list = cur.fetchall()

        hyu_header = ["name", "sid", "phone", "email"]
        hyu_contacts = []

        print(contacts_list)

        if (len(contacts_list[0]) == 5):
            for c in contacts_list:
                tmp_list = c[0:3]
                email = c['local_part'] + "@" + c['domain_part']
                tmp_list.append(email)
                print(tmp_list)
                hyu_contacts.append(tmp_list)
        else:
            hyu_contacts = contacts_list

        header = ["name", "phone", "email", "position"]
        sql = f"select name, phone, email, position from personal_contacts c where c.sid = '{session['sid']}'"
        cur.execute(sql)
        contacts = cur.fetchall()

    return render_template('personal_contacts.html', hyu_header = hyu_header, header = header, hyu_contacts = hyu_contacts, contacts=contacts, session=session)

@app.route("/contacts/edit", methods=["GET", "POST"])
def contacts_edit():
    if session['sid'] == None:
        return redirect('/')

    if request.method == 'GET':
        info = request.args
        return render_template("personal_edit.html", info=info)
    else:
        mode = request.form.get("mode")

        if mode == "delete": #delete
            print("delete")
            phone = request.form.get("phone")

            with pg.connect(connect_string) as conn:
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                sql = f"delete from personal_contacts where phone = '{phone}'"
                cur.execute(sql)
                conn.commit()

            return redirect("/contacts")

        else:
            print("edit")
            name = request.form.get("name")
            phone = request.form.get("phone")
            email = request.form.get("email")
            position = request.form.get("position")
            #local_part, domain_part = request.form.get("email").split("@")

            print(name, phone, email, position)

            if len(name) == 0 and len(phone) == 0 and len(email) == 0 and len(position) == 0:
                return redirect("/contacts")
            else:
                with pg.connect(connect_string) as conn:
                    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                    sql = "select * from personal_contacts"
                    cur.execute(sql)
                    contacts_list = cur.fetchall()

                    if mode == "edit":
                        sql = f"update personal_contacts set name = '{name}', email = '{email}', position = '{position}' where phone = '{phone}'"
                        cur.execute(sql)
                        conn.commit()

                    elif mode == "add":
                        try:
                            sql = f"insert into personal_contacts values ('{session['sid']}', '{name}', '{phone}', '{email}', '{position}')"
                            cur.execute(sql)
                            conn.commit()
                        except:
                            return redirect("/contacts")

                return redirect("/contacts")


if __name__ == "__main__":
    app.run(debug=1)