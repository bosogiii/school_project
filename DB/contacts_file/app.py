from flask import Flask, render_template, redirect, request
import csv
import collections

app = Flask(__name__)
session = { 'sid': None, 'sname': None }

@app.route("/")
def index():
    return render_template("index.html", session=session)

@app.route("/mailbox")
def mailbox():
    return redirect("/")

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
    else:
        with open('students.csv', mode='r') as infile:
            reader = csv.reader(infile)
            print(reader)
            for row in reader:
                print(row)
                print(sid)
                print(passwd)
                if sid == row[0].strip():
                    if passwd == row[1].strip():
                        session['sid'] = sid
                        session['sname'] = row[2]
                        return redirect("/")
                    else:
                        return render_template('login.html', msg="Wrong PW")

            return render_template('login.html', msg="Invalid ID")
    return redirect("/")

@app.route("/logout")
def logout():
    session['sid'] = None
    session['sname'] = None
    return redirect('/')

@app.route("/admin/hyucontacts")
def hyucontacts():
    if session['sid'] != "admin":
        return redirect('/')

    with open('contacts.csv', 'r') as contactsfile, open('students.csv', 'r') as studentsfile:
        contactsf = csv.DictReader(contactsfile)
        studentsf = csv.DictReader(studentsfile)

        contacts_list = [row for row in contactsf]
        students_list = [row for row in studentsf]

        hyu_header = ["name", "sid", "phone", "email"]
        hyu_contacts = []
        tmp_list =[]

        if(len(contacts_list[0].keys()) == 4):
            for c in contacts_list:
                for s in students_list:
                    if c['sid'] == s['sid']:
                        tmp_list.append(s['sname'])
                        tmp_list.extend(list(map(str.strip, c.values())))
                        email = tmp_list[3] + "@" + tmp_list[4]
                        tmp_list[3:5] = []
                        tmp_list.append(email)
                        hyu_contacts.append(tmp_list)
                        tmp_list = []
                        break
        else:
            for c in contacts_list:
                for s in students_list:
                    if c['sid'] == s['sid']:
                        tmp_list.append(s['sname'])
                        tmp_list.extend(list(map(str.strip, c.values())))
                        hyu_contacts.append(tmp_list)
                        tmp_list = []
                        break

    with open('personal_contacts.csv', 'r') as contactsfile:
        contactsf = csv.DictReader(contactsfile)

        contacts_list = [row for row in contactsf]

        header = ["owner", "name", "phone", "email", "position"]
        contacts = []
        tmp_list = []

        for c in contacts_list:
            tmp_list.extend(list(map(str.strip, c.values())))
            contacts.append(tmp_list)
            tmp_list = []

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

            with open('contacts.csv', 'r', newline="") as contactsfile:
                contactsf = csv.DictReader(contactsfile)
                contacts_list = [row for row in contactsf]

                for row in contacts_list:
                    if sid == row['sid'].strip():
                        contacts_list.remove(row)
                        break
                if len(contacts_list[0].keys()) == 3:
                    header = ['sid', 'phone', 'email']
                else:
                    header = ['sid', 'phone', 'local_part', 'domain_part']

            with open('contacts.csv', 'w', newline="") as contactsfile:
                writer = csv.DictWriter(contactsfile, header)
                writer.writeheader()
                for item in contacts_list:
                    writer.writerow(item)

            return redirect("/admin/hyucontacts")

        else:
            print("edit")
            sid = request.form.get("sid")
            sid = "{0:<15}".format(sid)
            phone = request.form.get("phone")
            phone = "{0:<11}".format(phone)
            email, domain = request.form.get("email").split("@")

            print(sid, phone, email, domain)

            if len(sid) == 0 and len(phone) == 0 and len(email) == 0:
                return redirect("/admin/hyucontacts")
            else:
                with open('contacts.csv', 'r') as contactsfile, open('students.csv', 'r') as studentsfile:
                    contactsf = csv.DictReader(contactsfile)
                    studentsf = csv.DictReader(studentsfile)

                    contacts_list = [row for row in contactsf]
                    students_list = [row for row in studentsf]
                    exist = False

                for row in contacts_list:
                    if sid == row['sid']:
                        exist = True
                if len(contacts_list[0].keys()) == 4:
                    header = ['sid', 'phone', 'local_part', 'domain_part']

                    if(mode == "edit"):
                        for item in contacts_list:
                            if item['sid'] == sid:
                                item['phone'] = phone
                                item['local_part'] = f"{email}"
                                item['domain_part'] = f"{domain}"
                                break

                    elif(mode == "add"):
                        for row in students_list:
                            if sid == row['sid'] and not exist:
                                # insert
                                tmp_dic = collections.OrderedDict()
                                tmp_dic['sid'] = f"{sid}"
                                tmp_dic['phone'] = f"{phone}"
                                tmp_dic['local_part'] = f"{email}"
                                tmp_dic['domain_part'] = f"{domain}"
                                contacts_list.append(tmp_dic)

                else:
                    header = ['sid', 'phone', 'email']

                    if (mode == "edit"):
                        for item in contacts_list:
                            if item['sid'] == sid:
                                item['phone'] = f"{phone}"
                                item['email'] = f"{email}@{domain}"
                                break

                    elif (mode == "add"):
                        for row in students_list:
                            if sid == row['sid'] and not exist:
                                # insert
                                tmp_dic = collections.OrderedDict()
                                tmp_dic['sid'] = f"{sid}"
                                tmp_dic['phone'] = f"{phone}"
                                tmp_dic['email'] = f"{email}@{domain}"
                                contacts_list.append(tmp_dic)

                with open('contacts.csv', 'w', newline="") as contactsfile:
                    print(contacts_list)
                    writer = csv.DictWriter(contactsfile, header)
                    writer.writeheader()
                    for item in contacts_list:
                        writer.writerow(item)

                return redirect("/admin/hyucontacts")

@app.route("/admin/statistics")
def statistics():
    if session['sid'] != "admin":
        return redirect('/')

    with open("contacts.csv", 'r') as contactsfile:
        contactsf = csv.DictReader(contactsfile)
        contacts_list = [row for row in contactsf]


    if(len(contacts_list[0].keys()) == 4):
        pass
    else:
        with open('contacts.csv', 'r') as contactsfile:
            contactsf = csv.DictReader(contactsfile)
            contacts_list = [row for row in contactsf]
            contacts = []
            tmp_dic = {}
            for row in contacts_list:
                tmp_dic['sid'] = row['sid']
                tmp_dic['phone'] = row['phone']
                tmp_dic['local_part'] = row['email'].split("@")[0]
                tmp_dic['domain_part'] = row['email'].split("@")[1]
                contacts.append(tmp_dic)
                print(tmp_dic)
                tmp_dic = {}

        header = ['sid', 'phone', 'local_part', 'domain_part']

        contacts_list = []
        with open('contacts.csv', 'w', newline="") as contactsfile:
            for row in contacts:
                tmp_dic = collections.OrderedDict()
                tmp_dic['sid'] = row['sid']
                tmp_dic['phone'] = row['phone']
                tmp_dic['local_part'] = row['local_part']
                tmp_dic['domain_part'] = row['domain_part']
                print(tmp_dic)
                contacts_list.append(tmp_dic)

            writer = csv.DictWriter(contactsfile, header)
            writer.writeheader()
            for item in contacts_list:
                writer.writerow(item)

    with open("contacts.csv", 'r') as contactsfile:
        contactsf = csv.DictReader(contactsfile)
        contacts_list = [row for row in contactsf]

        email_list =[item['domain_part'] for item in contacts_list]
        email_dic = {}
        cnt = 0

        for item in email_list:
            for items in email_list:
                if(item == items):
                    cnt += 1
            email_dic[item] = cnt
            cnt = 0

        print(email_dic)

        return render_template('statistics.html', email=email_dic)


@app.route("/admin/useradd", methods=["GET", "POST"])
def useradd():
    if session['sid'] != "admin":
        return redirect('/')

    if request.method == "GET":
        return render_template("useradd.html")
    else:

        sid = request.form.get("sid")
        sid = "{0:<15}".format(sid)
        passwd = request.form.get("passwd")
        passwd = "{0:<15}".format(sid)
        sname = request.form.get("sname")
        sex = request.form.get("sex")
        sex = "{0:<6}".format(sex)
        major_id = request.form.get("major_id")
        tutor_id = request.form.get("tutor_id")
        tutor_id = "{0:<15}".format(tutor_id)
        grade = request.form.get("grade")
        print(sid, passwd, sname, sex)
        with open('students.csv', 'r') as studentsfile:
            studentsf = csv.DictReader(studentsfile)

            students_list = [row for row in studentsf]

            for row in students_list:
                print(row['sid'], sid)
                if row['sid'] == sid:
                    return render_template("useradd.html", session=session, msg="same student is in the list")

        with open('students.csv', 'a', newline="") as studentsfile:
            writer = csv.writer(studentsfile)
            writer.writerow(
                [f"{sid}", f"{passwd}", f"{sname}", f"{sex}", f"{major_id}", f"{tutor_id}", f"{grade}"]
            )

        return redirect("/")

@app.route("/contacts")
def contacts():
    if session['sid'] == None:
        return redirect('/')

    with open('contacts.csv', 'r') as contactsfile, open('students.csv', 'r') as studentsfile:
        contactsf = csv.DictReader(contactsfile)
        studentsf = csv.DictReader(studentsfile)

        contacts_list = [row for row in contactsf]
        students_list = [row for row in studentsf]

        hyu_header = ["name", "sid", "phone", "email"]
        hyu_contacts = []
        tmp_list =[]

        if(len(contacts_list[0].keys()) == 4):
            for c in contacts_list:
                for s in students_list:
                    if c['sid'] == s['sid']:
                        tmp_list.append(s['sname'])
                        tmp_list.extend(list(map(str.strip, c.values())))
                        email = tmp_list[3] + "@" + tmp_list[4]
                        tmp_list[3:5] = []
                        tmp_list.append(email)
                        hyu_contacts.append(tmp_list)
                        tmp_list = []
                        break
        else:
            for c in contacts_list:
                for s in students_list:
                    if c['sid'] == s['sid']:
                        tmp_list.append(s['sname'])
                        tmp_list.extend(list(map(str.strip, c.values())))
                        hyu_contacts.append(tmp_list)
                        tmp_list = []
                        break

    with open('personal_contacts.csv', 'r') as contactsfile:
        contactsf = csv.DictReader(contactsfile)

        contacts_list = [row for row in contactsf]

        header = ["name", "phone", "email", "position"]
        contacts = []
        tmp_list =[]

        for c in contacts_list:
             if c['sid'].strip() == session['sid']:
                tmp_list.extend(list(map(str.strip, c.values())))
                tmp_list.pop(0)
                contacts.append(tmp_list)
                tmp_list = []


        #return render_template('hyucontacts.html', header=header, contacts=reader, session=session)
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
            phone = "{0:<11}".format(phone)

            with open('personal_contacts.csv', 'r') as contactsfile:
                contactsf = csv.DictReader(contactsfile)
                contacts_list = [row for row in contactsf]

                for row in contacts_list:
                    print(row)
                    if phone == row['phone']:
                        print(row)
                        contacts_list.remove(row)
                        break
                header = ['sid', 'name', 'phone', 'email', 'position']

            with open('personal_contacts.csv', 'w', newline="") as contactsfile:
                writer = csv.DictWriter(contactsfile, header)
                writer.writeheader()
                for item in contacts_list:
                    writer.writerow(item)

            return redirect("/contacts")

        else:
            print("edit")
            name = request.form.get("name")
            phone = request.form.get("phone")
            phone = "{0:<11}".format(phone)
            email = request.form.get("email")
            position = request.form.get("position")

            print(name, phone, email, position)

            if len(name) == 0 and len(phone) == 0 and len(email) == 0 and len(position) == 0:
                return redirect("/contacts")
            else:
                with open('personal_contacts.csv', 'r') as contactsfile:
                    contactsf = csv.DictReader(contactsfile)

                    contacts_list = [row for row in contactsf]
                    exist = False

                    header = ['sid', 'name', 'phone', 'email', 'position']

                    for row in contacts_list:
                        if phone == row['phone'] and session['sid'] == row['sid']:
                            exist = True

                with open('personal_contacts.csv', 'w', newline="") as contactsfile:
                    if mode == 'edit' :
                        if exist:
                            for item in contacts_list:
                                if item['phone'] == phone:
                                    item['name'] = name
                                    item['email'] = email
                                    item['position'] = position
                                    break

                    elif mode == "add":
                        if not exist:
                            # insert
                            tmp_dic = collections.OrderedDict()
                            tmp_dic['sid'] = session['sid']
                            tmp_dic['name'] = f"{name}"
                            tmp_dic['phone'] = f"{phone}"
                            tmp_dic['email'] = f"{email}"
                            tmp_dic['position'] = f"{position}"
                            print(tmp_dic)
                            contacts_list.append(tmp_dic)

                    print(contacts_list)
                    writer = csv.DictWriter(contactsfile, header)
                    writer.writeheader()
                    for item in contacts_list:
                        writer.writerow(item)

                    return redirect("/contacts")

if __name__ == "__main__":
    app.run(debug=1)