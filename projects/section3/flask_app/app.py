def hello():
    from flask import Flask, render_template, jsonify, request, json
    app = Flask(__name__)
    @app.route('/hello')
    def index():
        import jwt
        import time

        METABASE_SITE_URL = "http://127.0.0.1:3000"
        METABASE_SECRET_KEY = "..."

        payload = {
        "resource": {"dashboard": 1},
        "params": {
            
        },
        "exp": round(time.time()) + (60 * 10) # 10 minute expiration
        }
        token = jwt.encode(payload, METABASE_SECRET_KEY, algorithm="HS256")

        iframeUrl = METABASE_SITE_URL + "/embed/dashboard/" + token + "#bordered=true&titled=true"
        return render_template('test.html', iframeUrl = iframeUrl)
    return app


def create_app():
    from flask import Flask, render_template, jsonify, request, json
    from flask_mysqldb import MySQL
    import pymysql

    app = Flask(__name__)
    

    @app.route('/')
    def index():
        return render_template("get_data.html")

    
    @app.route('/db_test')
    def db_test():
        import pandas as pd
        import pickle
        from category_encoders import TargetEncoder

        conn = pymysql.connect(host = '...', db = '...',user = 'root', passwd='...')
        cur =  conn.cursor(pymysql.cursors.DictCursor)
        X_train = cur.execute("SELECT * FROM  X_train_fw")
        X_train = cur.fetchall()
        X_train_fw = pd.DataFrame(X_train)
        #print(X_train_fw.head())
        te = TargetEncoder(smoothing = 1000)
        X_train_fw_te = te.fit_transform(X_train_fw)
        #print(X_train_fw_te.head())
        return jsonify(X_train)

    @app.route('/position_input')
    def fw_info(position = None):

        conn = pymysql.connect(host = '...', db = '...',user = 'root', passwd='...')   
        position = request.args.get("position")
        cur = conn.cursor(pymysql.cursors.DictCursor)
        get_name = "SELECT DISTINCT name  FROM fw_df_final"
        cur.execute(get_name)
        name_list = cur.fetchall()
        
        get_team = "SELECT DISTINCT team FROM fw_df_final"
        cur.execute(get_team)
        team_list = cur.fetchall() 

        get_country = "SELECT DISTINCT country FROM fw_df_final"
        cur.execute(get_country)
        country_list = cur.fetchall()
        return render_template("position_output.html", position = position,name_list = name_list,team_list = team_list,country_list = country_list)
       
                  
    @app.route('/fw_output')
    def show_results(name = None, height = None, country = None,
            age = None, league = None, team = None, detailed_position = 'FW',
            games = None, mins = None, goals = None, assists = None,
            key_passes = None, rating = None):
        conn = pymysql.connect(host = '...', db = '...',user = 'root', passwd='...')
        name = request.args.get("name")
        height = request.args.get("height")
        country = request.args.get("country")
        age = request.args.get("age")
        league = request.args.get("league")
        team = request.args.get("team")
        detailed_position = request.args.get("detailed_position")
        games = request.args.get("games")
        mins = request.args.get("mins")
        goals = request.args.get("goals")
        assists = request.args.get("assists")
        key_passes = request.args.get("key_passes")
        rating = request.args.get("rating")
        fw_list = [name, height, country, age, league, team, detailed_position,
                games, mins, goals, assists, key_passes, rating]
        title_list = ['이름', '신장', '국적', '나이', '리그', '팀', '포지션',
                '경기수', '뛴시간(분)', '골', '어시스트', '키패스', '평점']
        cur =  conn.cursor(pymysql.cursors.DictCursor)
        image = cur.execute("SELECT img_source from images where name=%s",name)
        image = cur.fetchone()['img_source']
        import pandas as pd
        import pickle
        from category_encoders import TargetEncoder
        X_train = cur.execute("SELECT * FROM  X_train_fw")
        X_train = cur.fetchall()
        X_train_fw = pd.DataFrame(X_train)
        X_test_fw = pd.DataFrame([fw_list],columns = ['name', 'height' , 'country', 'age', 'league', 'team', 'position', 'games', 'mins', 'goals', 'assists', 'key_passes', 'rating'])
        y_train = cur.execute("SELECT * FROM  y_train_fw") 
        y_train = cur.fetchall()
        y_train_fw = pd.DataFrame(y_train)
        te = TargetEncoder(smoothing=1000)
        X_train_fw_te = te.fit_transform(X_train_fw, y_train_fw)
        #print(X_train_fw_te.head())
        X_test_fw_te = te.transform(X_test_fw)
        #print(X_test_fw_te.head())

        with open('fw_model.pkl','rb') as pickle_file:
            model = pickle.load(pickle_file)
        results = model.predict(X_test_fw_te)
        
        insert_table = "INSERT INTO fw_records(name, country,age, league, team, position,games, mins, goals, assists, key_passes, ratings, market_values)  VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cur.execute(insert_table, (name,country, int(age), league, team, detailed_position, int(games), int(mins), int(goals), int(assists), float(key_passes), float(rating), round(results[0],2)))
        conn.commit()
        return render_template("fw_output.html", fw_list = fw_list,title_list= title_list, results = str(round(results[0],2)),image = image)
    
    @app.route('/player_results')
    def show_report():
        # You'll need to install PyJWT via pip 'pip install PyJWT' or your project packages file

        import jwt
        import time

        METABASE_SITE_URL = "http://127.0.0.1:3000"
        METABASE_SECRET_KEY = "..."

        payload = {
        "resource": {"dashboard": 2},
        "params": {
            
        },
        "exp": round(time.time()) + (60 * 10) # 10 minute expiration
        }
        token = jwt.encode(payload, METABASE_SECRET_KEY, algorithm="HS256")

        iframeUrl = METABASE_SITE_URL + "/embed/dashboard/" + token + "#bordered=true&titled=true"

        return render_template('metabase_report.html', iframeUrl = iframeUrl)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, threaded=True)
    
