from flask import Flask, render_template, redirect, request
from datetime import datetime
import ast
import psycopg2 as pg
import psycopg2.extras
import json
import copy

app = Flask(__name__)

session = {'type': None,
           'did': None, 'seller_id': None, 'sid': None,
           'name': None, 'phone': None, 'local': None, 'domain': None,
           'customer': None, 'seller': None, 'delivery': None
}

db_connector = {
    'host': 'localhost',
    'user': 'postgres',
    'dbname': 'hanyang_delivery',
    'port': '5432',
    'password': 'thdqhtjr12'
}

connect_string = "host={host} user={user} dbname = {dbname} password = {password}, port={port}".format(**db_connector)

@app.route("/")
def index():
    return render_template("index.html", session=session)

@app.route("/logout")
def logout():
    session['type'] = None
    session['did'] = None
    session['seller_id'] = None
    session['sid'] = None
    session['name'] = None
    session['phone'] = None
    session['local'] = None
    session['domain'] = None
    session['customer'] = None
    session['seller'] = None
    session['delivery'] = None
    return redirect('/')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("index.html", session=session)

    email = request.form.get('email')
    local, domain = email.split('@')
    passwd = request.form.get('passwd')

    with pg.connect(connect_string) as conn:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        #사용자
        sql = f"select name, phone from customer where local='{local}' and domain='{domain}' and passwd='{passwd}'"
        cur.execute(sql)
        rows = cur.fetchall()
        if len(rows) != 1:
            pass
        else:
            session['type'] = 'customer'
            session['name'] = rows[0]['name']
            session['phone'] = rows[0]['phone']
            session['local'] = local
            session['domain'] = domain
            session['customer'] = True

        #seller
        sql = f"select name, seller_id from sellers where local='{local}' and domain='{domain}' and passwd='{passwd}'"
        cur.execute(sql)
        rows = cur.fetchall()
        if len(rows) != 1:
            pass
        else:
            session['type'] = 'seller' if session['type'] is None else 'multi'
            session['name'] = rows[0]['name']
            session['seller_id'] = rows[0]['seller_id']
            session['local'] = local
            session['domain'] = domain
            session['seller'] = True

        #delivery
        sql = f"select name, did from delivery where local='{local}' and domain='{domain}' and passwd='{passwd}'"
        cur.execute(sql)
        rows = cur.fetchall()
        if len(rows) != 1:
            pass
        else:
            session['type'] = 'delivery' if session['type'] is None else 'multi'
            session['name'] = rows[0]['name']
            session['did'] = rows[0]['did']
            session['local'] = local
            session['domain'] = domain
            session['delivery'] = True


    if session['name'] is None:
        return render_template("index.html", msg="잘못된 ID 또는 비밀번호입니다.", session = session)
    elif session['type'] == 'multi':
        return render_template("index.html", session=session)
    else:
        return redirect('/{0}'.format(session['type']))

@app.route("/select", methods=['POST'])
def typeselect():
    type = request.form.get('type')

    session['type'] = type
    return redirect(f'/{type}')

@app.route("/customer")
def coustomer():
    if request.method == 'GET':
        if session['name'] is None:
            return render_template("index.html", session=session)
        return render_template("customer.html", session=session)

@app.route("/customer/<name>/infoedit", methods=['POST', 'GET'])
def infodeit_customer(name):
    if request.method == 'GET':
        return render_template("infoedit_customer.html", session=session)

    name_changed = request.form.get("name")
    passwd = request.form.get("passwd")
    address = request.form.get("address")

    if name is None and passwd is None:
        return redirect("/customer/<name>/infoedit")
    else:
        with pg.connect(connect_string) as conn:
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            try:
                if name_changed is not None:
                    sql = f"update customer set name = '{name_changed}' where phone = '{session['phone']}' and local = '{session['local']}' and domain = '{session['domain']}'"
                    cur.execute(sql)
                    conn.commit()
                    session['name'] = name_changed
                    redirect("/customer")
                elif passwd is not None:
                    sql = f"update customer set passwd = '{passwd}' where phone = '{session['phone']}' and local = '{session['local']}' and domain = '{session['domain']}'"
                    cur.execute(sql)
                    conn.commit()
                    redirect("/customer")
                else:
                    sql = f"insert into directory values('{session['phone']}', '{session['local']}', '{session['domain']}', '{address}')"
                    cur.execute(sql)
                    conn.commit()
                    redirect("/customer")
            except Exception:
                return redirect("/customer")
    return redirect("/customer")

@app.route("/customer/<name>/orderlist", methods=['POST', 'GET'])
def order_list(name):
    if request.method == 'GET':
        status_list = ['주문접수', '주문확인', '배송중', '배송완료', '주문취소']
        with pg.connect(connect_string) as conn:
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            sql = f"select s.sname, o.menu, o.payment, o.time from stores s, orders o where o.phone = '{session['phone']}' and o.local = '{session['local']}' and o.domain = '{session['domain']}' and s.sid=o.sid and o.status>2 order by o.time desc"
            cur.execute(sql)
            list = cur.fetchall()

            sql = f"select s.sname, o.menu, o.payment, o.time, o.status, o.did from stores s, orders o where o.phone = '{session['phone']}' and o.local = '{session['local']}' and o.domain = '{session['domain']}' and s.sid=o.sid and o.status < 3 order by o.time desc"
            cur.execute(sql)
            now_list = cur.fetchall()

            sql = f"select payment from customer where phone='{session['phone']}' and local='{session['local']}' and domain='{session['domain']}'"
            cur.execute(sql)
            payment = cur.fetchall()

            sql = "select bid, name from bank"
            cur.execute(sql)
            bank = cur.fetchall()

            if type(payment[0][0]) == str:
                payment = json.loads(payment[0][0])
            else:
                payment = payment[0][0]

            header1 = ['가게', '메뉴이름', '수량', '결제수단', '주문 시간']
            header2 = ['가게', '메뉴', '수량', '결제수단', '주문 시간', '주문상태', '배달원', '주문확인']
            header3 = ['결제수단', '변경', '삭제']


            return render_template("order_list.html", session=session, status_list=status_list, header1=header1, header2=header2, header3=header3, list=list, now_list=now_list, bank=bank, payment=payment)
    else:
        values = request.form.to_dict()

        with pg.connect(connect_string) as conn:
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            sql = f"update orders set status = {values['status']} where time='{values['time']}' and phone='{values['phone']}' and local='{values['local']}' and domain='{values['domain']}'"
            cur.execute(sql)
            conn.commit()

            sql = f"update orders set did = NULL where time='{values['time']}' and phone='{values['phone']}' and local='{values['local']}' and domain='{values['domain']}' and did = {values['did']}"
            cur.execute(sql)
            conn.commit()

            sql = f"select stock from delivery where did = {values['did']}"
            cur.execute(sql)
            list=cur.fetchall()
            stock = list[0][0]
            stock -= 1

            sql = f"update delivery set stock = {stock}"
            cur.execute(sql)
            conn.commit()


        return redirect('/customer/<name>/orderlist')

@app.route("/customer/<name>/order", methods=['POST', 'GET'])
def order(name):
    if request.method == 'GET':
        return render_template("search.html", session=session)
    else:
        location=request.form.get("location")
        tag=request.form.get("tag")
        address=request.form.get("address")
        sname=request.form.get("sname")
        header = ['주소', '상호명', '가게설명', '가게입장']

        if location is not None:
            lng = request.form.get("lng")
            lat = request.form.get("lat")
            day = request.form.get("day")
            hour = request.form.get("hour")

            with pg.connect(connect_string) as conn:
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

                #위치 정보가 없으면 새로고침
                if len(lng) == 0:
                    return redirect(f"/customer/{name}/order")

                sql = f"select address, sname, info, sid, schedules, lng, lat from stores st order by abs(st.lng-{lng})+abs(st.lat-{lat}) limit 50"
                cur.execute(sql)
                stores = cur.fetchall()
                for store in stores:
                    store['schedules'] = json.loads(store['schedules'])

                store_list = copy.deepcopy(stores)
                for idx, store in enumerate(stores):
                    for item in store['schedules']:
                        if item['day'] == int(day):
                            if item['holiday'] == True:
                                store_list[idx] = None
                            elif int(item['open']) > int(hour)*100 or int(item['closed']) <= int(hour)*100:
                                store_list[idx] = None

                store_list[:] = [item for item in store_list if item is not None]

                return render_template("order.html", header=header, store_list=store_list, session=session, lng=lng, lat=lat, location=location)

        elif tag is not None:
            with pg.connect(connect_string) as conn:
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

                sql = f"select address, sname, info, sid from stores st where tag='{tag}'"
                cur.execute(sql)
                store_list = cur.fetchall()
                return render_template("order.html", header=header, store_list=store_list, session=session)
        elif address is not None:
            with pg.connect(connect_string) as conn:
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                sql = f"select address, sname, info, sid from stores st where address like '{address}%'"
                cur.execute(sql)
                store_list = cur.fetchall()
                return render_template("order.html", header=header, store_list=store_list, session=session)
        else:
            with pg.connect(connect_string) as conn:
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

                sql = f"select address, sname, info, sid from stores st where sname='{sname}'"
                cur.execute(sql)
                store_list = cur.fetchall()

                return render_template("order.html", header=header, store_list=store_list, session=session)

@app.route("/customer/<name>/order/basket", methods=['POST', 'GET'])
def basket(name):
    if request.method == 'GET':
        sid = request.args.get('sid')

        with pg.connect(connect_string) as conn:
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            sql = f"select menu from menu where sid = '{sid}'"
            cur.execute(sql)
            menu_list = cur.fetchall()

            sql = f"select payment from customer where phone = '{session['phone']}' and local = '{session['local']}' and domain = '{session['domain']}'"
            cur.execute(sql)
            payment = cur.fetchall()

            if type(payment[0][0]) == str:
                payment_list = json.loads(payment[0][0])
            else:
                payment_list = payment[0][0]

            sql = "select bid, name from bank"
            cur.execute(sql)
            bank = cur.fetchall()

            if len(payment_list) == 0:
                return render_template("order_list.html", msg="결제수단을 추가하세요.", session=session)

            sql = f"select address from directory where phone = '{session['phone']}' and local = '{session['local']}' and domain = '{session['domain']}'"
            cur.execute(sql)
            directiry_list = cur.fetchall()

            if len(directiry_list) == 0:
                return render_template("order_list.html", msg="배송지를 추가하세요.", sessio=session)

            return render_template("basket.html", sid=sid, menu_list=menu_list, payment_list=payment_list, bank = bank, directiry_list=directiry_list, session=session)
    else:
        value = request.form.to_dict()
        timestamp = datetime.now()

        address = value['directory']
        del value['directory']

        payment = value['payment']
        del value['payment']
        payment=ast.literal_eval(payment)
        payment = json.dumps(payment)

        sid = value["sid"]
        del value["sid"]

        tmp = []
        for key, item in value.items():
            if item == "0":
                tmp.append(key)
        for key in tmp:
            del value[key]

        menu = json.dumps(value)

        with pg.connect(connect_string) as conn:
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            sql = f"insert into orders (sid, menu, payment, time, phone, local, domain, status, address) values ({sid}, '{menu}', '{payment}', '{timestamp}', '{session['phone']}', '{session['local']}', '{session['domain']}', 0, '{address}')"
            cur.execute(sql)
            conn.commit()
            return redirect("/customer")

@app.route("/customer/<name>/editpay", methods=['POST', 'GET'])
def editpay(name):
    mode = request.form.get("mode")
    list = request.form

    with pg.connect(connect_string) as conn:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        if mode == "account_edit" or mode == "card_edit":
            sql = "select bid, name from bank"
            cur.execute(sql)
            bank = cur.fetchall()

            return render_template("pay_edit.html", session=session, mode=mode, bank=bank, item=ast.literal_eval(list['item']), payment=ast.literal_eval(list['payment']))

        elif mode == "edit_account" or mode == "edit_card":
            tmp = list['payment'].replace(list['item'] + ',', "")
            tmp = tmp.replace(list['item'], "")
            payment = ast.literal_eval(tmp)

            if mode == "edit_account":
                tmp = {}
                tmp['type'] = "account"
                tmp['data'] = {'bid': int(list['bid']), 'acc_num': int(list['acc_num'])}

                payment.append(tmp)
                payment = json.dumps(payment)
            else:
                tmp = {}
                tmp['type'] = "card"
                tmp['data'] = {'card_num': list['card_num']}

                payment.append(tmp)
                payment = json.dumps(payment)

            try:
                sql = f"update customer set payment='{payment}' where phone='{session['phone']}'and local='{session['local']}' and domain='{session['domain']}'"
                cur.execute(sql)
                conn.commit()
            except (Exception, psycopg2.DatabaseError) as error:
                print(error)

        elif mode == "delete":
            tmp = list['payment'].replace(list['item'] + ',', "")
            tmp = tmp.replace(list['item'], "")
            payment = ast.literal_eval(tmp)
            payment = json.dumps(payment)
            try:
                sql = f"update customer set payment='{payment}' where phone='{session['phone']}'and local='{session['local']}' and domain='{session['domain']}'"
                cur.execute(sql)
                conn.commit()
            except (Exception, psycopg2.DatabaseError) as error:
                print(error)

        elif mode == "account":
            sql = f"select payment from customer where phone = '{session['phone']}' and local = '{session['local']}' and domain = '{session['domain']}'"
            cur.execute(sql)
            payment = cur.fetchall()

            if type(payment[0][0]) == str:
                payment_list = json.loads(payment[0][0])
            else:
                payment_list = payment[0][0]

            tmp={}
            tmp['type'] = mode
            tmp['data'] = {'bid': int(list['bid']), 'acc_num': int(list['acc_num'])}

            payment_list.append(tmp)
            payment_list = json.dumps(payment_list)

            try:
                sql = f"update customer set payment='{payment_list}' where phone='{session['phone']}'and local='{session['local']}' and domain='{session['domain']}'"
                cur.execute(sql)
                conn.commit()
            except (Exception, psycopg2.DatabaseError) as error:
                print(error)

        elif mode == "card":
            sql = f"select payment from customer where phone = '{session['phone']}' and local = '{session['local']}' and domain = '{session['domain']}'"
            cur.execute(sql)
            payment = cur.fetchall()

            if type(payment[0][0]) == str:
                payment_list = json.loads(payment[0][0])
            else:
                payment_list = payment[0][0]
            tmp = {}
            tmp['type'] = mode
            tmp['data'] = {'card_num': list['card_num']}

            payment_list.append(tmp)
            payment_list = json.dumps(payment_list)
            try:
                sql = f"update customer set payment='{payment_list}' where phone='{session['phone']}'and local='{session['local']}' and domain='{session['domain']}'"
                cur.execute(sql)
                conn.commit()
            except (Exception, psycopg2.DatabaseError) as error:
                print(error)

    return redirect(f"/customer/{name}/orderlist")

@app.route("/seller", methods=['POST', 'GET'])
def seller():
    if request.method == 'GET':
        if session['name'] is None:
            return render_template("index.html", session=session)
        return render_template("seller.html", session=session)

@app.route("/seller/storelist", methods=['POST', "GET"])
def storelist():
    if request.method == 'GET':
        with pg.connect(connect_string) as conn:
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            # seller_id 가 일치하는 stores address, sname, phone_nums, schedules
            sql = f"select address, sname, sid from stores st where {session['seller_id']}=st.seller_id"
            cur.execute(sql)
            store_list = cur.fetchall()
            header = ['주소', '상호명', '가게입장']

            return render_template("storelist.html", header=header, store_list=store_list)
    else:
        sname = request.form.get("sname")
        sid = request.form.get("sid")
        session['sid'] = sid
        return redirect(f"/seller/storelist/{sname}")

@app.route("/seller/storelist/<sname>", methods=['POST', 'GET'])
def store(sname):
    if request.method == 'GET':
        with pg.connect(connect_string) as conn:
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            # seller_id 가 일치하는 stores address, sname, phone_nums, schedules
            sql = f"select sid, address, sname, phone_nums, schedules, tag, info from stores st where {session['seller_id']}=st.seller_id and st.sid = {session['sid']}"
            cur.execute(sql)
            store = cur.fetchall()

            sql = f"select menu from menu where sid = {store[0][0]}"
            cur.execute(sql)
            menu = cur.fetchall()

            header = ['주소', '상호명', '전화번호', '영업일', '태그', '가게 설명']
            nums = json.loads(store[0][3])
            schedules = json.loads((store[0][4]))
            day = ['일요일', '월요일', '화요일', '수요일', '목요일', '금요일', '토요일']

            return render_template("store.html", header=header, store=store, nums=nums, schedules=schedules, menu=menu, day_list=day)
    else:
        mode = request.form.get("mode")
        if mode == "delete":  # delete
            sid = request.form.get("sid")
            menu = request.form.get("menu")
            sname = request.form.get("sname")

            with pg.connect(connect_string) as conn:
                cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
                sql = f"delete from menu where sid = '{sid}' and menu = '{menu}'"
                cur.execute(sql)
                conn.commit()

            return redirect(f"/seller/storelist/{sname}")

        else:
            sid = request.form.get("sid")
            menu = request.form.get("menu")
            menu_change = request.form.get("menu_change")
            sname = request.form.get("sname")
            if menu is None:
                return redirect(f"/seller/storelist/{sname}")
            else:
                with pg.connect(connect_string) as conn:
                    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

                    if mode == "edit":
                        sql = f"update menu set menu = '{menu_change}' where sid = '{sid}' and menu = '{menu}'"
                        cur.execute(sql)
                        conn.commit()

                    elif mode == "insert":
                        try:
                            sql = f"insert into menu (menu, sid) values('{menu}', '{sid}')"
                            cur.execute(sql)
                            conn.commit()
                        except Exception:
                            return redirect(f"/seller/storelist/{sname}")

                return redirect(f"/seller/storelist/{sname}")

@app.route("/seller/storelist/<sname>/orders", methods=['POST', 'GET'])
def orders(sname):
    status_list = ['주문접수', '주문확인', '배송중', '배송완료', '주문취소']
    if request.method == 'GET':
        with pg.connect(connect_string) as conn:
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            sql=f"select status, menu, time, phone, address, did, local, domain from orders where sid = '{session['sid']}' and status < 3"
            cur.execute(sql)
            orders = cur.fetchall()

            header = ['주문상태', '메뉴이름', '수량', '주문시간', '고객전화번호', '고객주소', '배달원', '주문확인', '주문취소']

            return render_template("current_order.html", name=sname, session=session, orders=orders, header=header, status_list=status_list)
    else:
        values = request.form.to_dict()

        with pg.connect(connect_string) as conn:
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            sql=f"update orders set status = {values['status']} where time='{values['time']}' and phone='{values['phone']}' and local='{values['local']}' and domain='{values['domain']}'"
            cur.execute(sql)
            conn.commit()

            if(values['status'] == "1"):
                sql=f"select did, name, phone, stock as distance from delivery d, stores s where d.stock < 5 and s.sid = '{session['sid']}' order by abs(d.lng-s.lng)+abs(d.lat-s.lat) limit 5"
                cur.execute(sql)
                delivery = cur.fetchall()
                header = ['배달원 번호', '배달원 이름', '전화번호', '현재배달량']
                return render_template("delivery_list.html", name=sname, session=session, header=header, delivery=delivery, values=values)

        return redirect(f"/seller/storelist/{sname}/orders")

@app.route("/seller/storelist/<sname>/orders/delivery", methods=['POST', 'GET'])
def selection(sname):
    values = request.form.to_dict()

    with pg.connect(connect_string) as conn:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        sql = f"update orders set status = {values['status']}, did = {values['did']} where time='{values['time']}' and phone='{values['phone']}' and local='{values['local']}' and domain='{values['domain']}'"
        cur.execute(sql)
        conn.commit()

        sql = f"select stock from delivery where did = {values['did']}"
        cur.execute(sql)
        list = cur.fetchall()
        stock = list[0][0]
        stock+=1

        sql = f"update delivery set stock = {stock} where did = {values['did']}"
        cur.execute(sql)
        conn.commit()

    return redirect(f"/seller/storelist/{sname}/orders")

@app.route("/seller/infoedit", methods=['POST', 'GET'])
def infodeit_seller():
    if request.method == 'GET':
        return render_template("infoedit.html", session=session)

    name = request.form.get("name")
    passwd = request.form.get("passwd")

    if name is None and passwd is None:
        return redirect("/seller/infoedit")
    else:
        with pg.connect(connect_string) as conn:
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            try:
                if name is not None:
                    sql = f"update sellers set name = '{name}' where seller_id = '{session['seller_id']}'"
                    cur.execute(sql)
                    conn.commit()
                    session['name'] = name
                    redirect("/seller")
                else:
                    sql = f"update sellers set passwd = '{passwd}' where seller_id = '{session['seller_id']}'"
                    cur.execute(sql)
                    conn.commit()
                    redirect("/seller")

            except Exception:
                return redirect("/seller")
    return redirect("/seller")


@app.route("/delivery")
def delivery():
    with pg.connect(connect_string) as conn:
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        sql = f"select s.sname, s.address, o.menu, o.time, o.phone, o.address from orders o, stores s where o.sid=s.sid and o.did={session['did']}"
        cur.execute(sql)
        list = cur.fetchall()
        header=['가게이름', '가게주소', '메뉴이름', '수량', '주문시간', '고객번호', '고객주소']
        return render_template("delivery.html", session=session, list=list, header=header)

@app.route("/test")
def test():
    # with pg.connect(connect_string) as conn:
    #     cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    #
    #     info = ['지역 최고 맛집', '2018년 우수식당', '최고의 맛을 선사합니다.', '사랑합니다 고객님', '특별 이벤트 중', '특별한 음식을 먹고싶을 때']
    #
    #     sql = f"select * from stores"
    #     cur.execute(sql)
    #     list = cur.fetchall()
    #
    #     for store in list:
    #         sql = f"update stores set info = '{info[store['sid'] % 6]}' where sid = {store['sid']}"
    #         cur.execute(sql)
    #         conn.commit()

    return render_template("test.html")

if __name__ == "__main__":
    app.run(debug=1)
