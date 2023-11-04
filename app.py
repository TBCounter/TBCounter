from flask import Flask, jsonify, request, current_app, send_file
from flask_cors import CORS
from sqlalchemy import func
from flask_migrate import Migrate
from config import Config
from datetime import datetime, timedelta
import yaml
from functools import wraps
import jwt
from robot import Robot, OCR_reader, robo_killer
import json
import shutil
import os
import re
from werkzeug.security import generate_password_hash, check_password_hash

from waitress import serve

import pandas as pd
import numpy as np

from models import init_db, SessionLocal, User, Account, Chest, Report, ChestRule, ClanPlayer, IdealChestName, IdealChestType  # noqa

app = Flask(__name__)
app.config.from_object(Config)
# db.init_app(app)
# migrate = Migrate(app, db, render_as_batch=True)
app.config['JSON_AS_ASCII'] = False
# enable CORS
CORS(app)
init_db()

db = SessionLocal()


@app.route('/register/', methods=('POST',))
def register():
    data = request.get_json()
    user = User(**data)
    db.add(user)
    db.commit()
    return jsonify(user.to_dict()), 201


@app.route('/changelog/', methods=('GET',))
def changelog():
    with open('changelog.yaml', encoding='utf8') as f:
        templates = yaml.safe_load(f)
        return jsonify(templates), 201


@app.route('/login/', methods=('POST',))
def login():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return None

    user = db.query(User).filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return None

    if not user:
        return jsonify({'message': 'Invalid credentials', 'authenticated': False}), 401

    token = jwt.encode({
        'sub': user.email,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(minutes=130)},
        current_app.config['SECRET_KEY'], algorithm="HS256")
    return jsonify({'token': token, 'userName': user.email})


def token_required(f):
    @wraps(f)
    def _verify(*args, **kwargs):
        auth_headers = request.headers.get('Authorization', '').split()

        invalid_msg = {
            'message': 'Invalid token. Registration and / or authentication required',
            'authenticated': False
        }
        expired_msg = {
            'message': 'Expired token. Re authentication required.',
            'authenticated': False
        }

        if len(auth_headers) != 2:
            return jsonify(invalid_msg), 401

        try:
            token = auth_headers[1]
            data = jwt.decode(
                token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            user = db.query(User).filter_by(email=data['sub']).first()
            if not user:
                raise RuntimeError('User not found')
            return f(user, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            # 401 is Unauthorized HTTP status code
            return jsonify(expired_msg), 401
        except (jwt.InvalidTokenError, Exception) as e:
            print(e)

            return jsonify(invalid_msg), 401

    return _verify


@app.route('/avatars/<name>')
def get_image(name):
    return send_file("avatars/"+name)


@app.route('/true_images/names/<name>')
def get_true_image(name):
    return send_file("true_images/names/"+name)


@app.route('/current_state/')
@token_required
def get_current_state(user):
    account_id = request.args.get('account_id')
    return send_file("temp_images/"+str(account_id)+"_screenshot.png")


@app.route('/temp_images/full_chests/<name>')
def get_chest_full_image(name):
    return send_file("temp_images/full_chests/"+name)


@app.route('/temp_images/all_chests/<name>')
def get_chest_all_image(name):
    return send_file("temp_images/all_chests/"+name)


@app.route('/chest-types/', methods=["GET"])
def getChestTypes():
    chests = [value for value in db.query(Chest.chest_type).distinct()]
    result = []
    for chest in chests:
        result.append(
            {
                "label": chest[0],
                "value": chest[0]
            }
        )

    return jsonify(result)


@app.route('/chest-names/', methods=["GET"])
def getChestNames():
    types = [value for value in db.query(Chest.chest_type).distinct()]
    final_result = {}
    for type_chest in types:
        chests = [value for value in db.query(Chest.chest_name).where(
            Chest.chest_type == type_chest[0]).distinct()]
        result = [{
            "label": "Любое имя",
            "value": "all"
        }]
        for chest in chests:
            result.append(
                {
                    "label": chest[0],
                    "value": chest[0]
                }
            )
        final_result[type_chest[0]] = result

    return jsonify(final_result)


@app.route('/scores-rules/', methods=['GET'])
@token_required
def getScoresRules(user):
    account_id = request.args.get('account_id')
    rules = db.query(ChestRule).filter_by(account_id=account_id).all()

    return jsonify([{"group": rule.group, "scores": rule.scores, "ideal_chest_name": rule.ideal_chest_name,  "ideal_chest_type": rule.ideal_chest_type} for rule in rules])


@app.route('/scores-rules/', methods=['POST'])
@token_required
def postScoresRules(user):
    data = request.get_json()
    account_id = data['account_id']
    new_rules = data['rules']
    db.query(ChestRule).filter_by(account_id=account_id).delete()

    for rule in new_rules:
        db.add(ChestRule(account_id,
                         rule.get('group'), float(rule.get('scores').replace(',', '.')) if type(rule.get('scores')) == str else rule.get('scores'), rule.get('ideal_chest_name'), rule.get('ideal_chest_type')))
    db.commit()
    print('ok???')
    rules = db.query(ChestRule).filter_by(account_id=account_id).all()
    return jsonify([{"group": rule.group, "scores": rule.scores, "ideal_chest_name": rule.ideal_chest_name,  "ideal_chest_type": rule.ideal_chest_type} for rule in rules])


@app.route('/info/', methods=['POST'])
@token_required
def add_account(user):
    data = request.get_json()
    login = data['login']
    password = data['password']
    isTriumph = data['isTriumph']
    try:
        my_robot = Robot(
            {"login": login, "password": password, "isTriumph": isTriumph})
        my_robot.start()
    except:
        return jsonify({'message': "wrong login or password"}), 401

    avatar_path, name_text, clan_text = my_robot.info()
    new_account = Account(login, password, user,
                          name_text, clan_text, avatar_path, isTriumph)
    db.add(new_account)
    db.commit()
    return jsonify({"ava": avatar_path, "name": name_text, "clan": clan_text})


@app.route('/info/', methods=['GET'])
@token_required
def get_account_info(user):
    accounts = db.query(Account).filter_by(user_id=user.id).all()
    response = []
    for account in accounts:
        acc_info = account.to_dict()
        chest_count = db.query(Chest).filter_by(account_id=account.id).filter(
            func.date(Chest.opened_in) == datetime.now().date()).count()
        acc_info['chest_count'] = chest_count
        response.append(acc_info)

    return jsonify(response)


@app.route('/list/', methods=['GET'])
@token_required
def get_chests_list(user):
    account_id = request.args.get('account_id')
    order_by = request.args.get('sort')

    direction = order_by[:1]
    order_by = order_by[1:]

    page = request.args.get('page', 1, int)

    if(direction == '+'):
        chests = db.query(Chest).filter_by(account_id=account_id).order_by(
            Chest.__table__.c[order_by].asc()).limit(25).offset((page-1)*25)
        # .paginate(page=page, per_page=25, error_out=False)
    else:
        chests = db.query(Chest).filter_by(account_id=account_id).order_by(
            Chest.__table__.c[order_by].desc()).limit(25).offset((page-1)*25)
    total = db.query(Chest).filter_by(account_id=account_id).count()
    return jsonify({"total": total,
                    "total_pages": total/25,
                    "page": page,
                    "items": [chest.to_dict() for chest in chests]})  # return player name from another table


@app.route('/list/', methods=['POST'])
@token_required
def get_file_list(user):
    data = request.get_json()
    account_id = data.get('account_id')
    from_date = data.get('from')
    to_date = data.get('to')

    query = db.query(Chest).filter_by(account_id=account_id)

    if from_date:
        query = query.filter(func.date(Chest.opened_in) >= from_date)
    if to_date:
        query = query.filter(func.date(Chest.opened_in) <= to_date)
    df = pd.read_sql(query.statement, query.session.bind, index_col='id')
    df.drop(['account_id', 'chest_type_id',
            'chest_name_id', 'player_id', 'path'], axis=1, inplace=True)

    filename = f"report_{account_id}_{from_date}_{to_date}.xlsx"
    df.to_excel(filename)

    return send_file(filename, as_attachment=True,
                     mimetype='application/vnd.ms-excel',
                     attachment_filename="test.xlsx")


@app.route('/save-report/', methods=['POST'])
@token_required
def save_chests_report(user):
    data = request.get_json()

    rep = Report(json.dumps(data), user.id)
    db.add(rep)
    db.commit()
    return jsonify(rep.hash)


@app.route('/save-chest/', methods=['POST'])
@token_required
def save_chest(user):
    data = request.get_json()

    chest_id = data.get('chest_id')

    chest = db.query(Chest).filter_by(id=chest_id).first()
    chest.check_needed = ''
    db.commit()
    return jsonify({"Ok?": True})


@app.route('/delete-chest/', methods=['POST'])
@token_required
def delete_chest(user):
    data = request.get_json()

    chest_id = data.get('chest_id')
    db.query(Chest).filter_by(id=chest_id).delete()
    db.commit()
    return jsonify({"Ok?": True})


def prepare_report(query, players_query, chest_rules, from_date, to_date):
    # chests
    df = pd.read_sql(query.statement, query.session.bind, index_col='id')
    df.drop(['player', 'chest_type', 'chest_name', 'opened_in',
            'got_at', 'account_id', 'path'], axis=1, inplace=True)
    df.dropna(subset='player_id', inplace=True)
    # players
    players = pd.read_sql(players_query.statement,
                          players_query.session.bind, index_col='id')
    players['player_id'] = players.index

    players.drop(['path', 'hash'], axis=1, inplace=True)

    df = df.merge(players, on='player_id', how='outer')
    # chest_names
    chest_names = db.query(IdealChestName)
    chest_names_df = pd.read_sql(
        chest_names.statement, chest_names.session.bind, index_col='id')
    chest_names_df.drop(['path', 'hash'], axis=1, inplace=True)
    chest_names_df['chest_name_id'] = chest_names_df.index
    df = df.merge(chest_names_df, on='chest_name_id', how='outer')
    # chest_types
    chest_types = db.query(IdealChestType)
    chest_types_df = pd.read_sql(
        chest_types.statement, chest_types.session.bind, index_col='id')
    chest_types_df.drop(['path', 'hash'], axis=1, inplace=True)
    chest_types_df['chest_type_id'] = chest_types_df.index
    df = df.merge(chest_types_df, on='chest_type_id', how='outer')

    # tables
    df.dropna(subset='level', inplace=True)
    levels = df.level.unique()

    tables = []

    for lvl in levels:
        dataframe = df[df.level == lvl]
        full_crosstable = pd.crosstab(dataframe.name,
                                      [dataframe.text_y, dataframe.text_x])
        crosstable = pd.crosstab(dataframe.name,
                                 dataframe.text_y)

        filtered_rules = list(filter(lambda item: (
            item['group'] == int(lvl)) | (item['group'] == 99), chest_rules))

        def scores_function(*args):
            score = 0
            current_serie = args[0].items()
            for index, value in current_serie:
                if type(value) == int:
                    weight = next((rule['scores'] for rule in filtered_rules if (
                        rule["ideal_chest_type"] == index[0]) &
                        ((rule["ideal_chest_name"] == index[1]) | (rule["ideal_chest_name"] == 'all'))),
                        1)
                    current_value = value * weight
                    score += current_value
            return score

        crosstable['scores'] = full_crosstable.apply(scores_function, axis=1)
        crosstable['sum'] = full_crosstable.apply(sum, axis=1)

        tables.append({'data': crosstable.to_json(
            orient="table"), 'level': lvl})

    df.dropna(subset='text_y', inplace=True)
    all_types = df.text_y.unique()
    schema = [{'title': 'name', 'field': 'name',
               "headerFilter": "input", "frozen": True}]
    added_types = []
    for current_title in all_types:
        if (current_title in added_types):
            continue

        if ('уровня' in current_title):
            global_type = re.split(r'\d+', current_title)[0]
            all_levels = list(
                filter(lambda x: x.startswith(global_type), all_types))

            added_types.extend(all_levels)

            def sorting_by_level(text):
                level_number = re.search(r'\d+', text).group(0)
                return int(level_number)

            all_levels.sort(key=lambda x: sorting_by_level(x))

            resulting = {
                'title': global_type,
                'columns': []
            }

            for level in all_levels:
                level_number = re.search(r'\d+', level).group(0)
                resulting.get('columns').append(
                    {
                        'title': level_number,
                        'field': level,
                        "minWidth": "60px",
                        "headerFilter": "number",
                        "headerFilterPlaceholder": "at least...",
                        "headerFilterFunc": ">="
                    }
                )

            schema.append(resulting)
        else:
            schema.append({
                'title': current_title,
                'field': current_title,
                "minWidth": "60px",
                "headerVertical": "flip",
                "headerFilter": "number",
                "headerFilterPlaceholder": "at least...",
                "headerFilterFunc": ">="
            })
    schema.append({
        'title': 'Очки',
        'field': 'scores',
        "minWidth": "60px",
        "headerFilter": "number",
        "headerFilterPlaceholder": "at least...",
        "headerFilterFunc": ">="
    })
    schema.append({
        'title': 'Сумма',
        'field': 'sum',
        "minWidth": "60px",
        "headerFilter": "number",
        "headerFilterPlaceholder": "at least...",
        "headerFilterFunc": ">="
    })
    # df.to_csv('pre-report.csv') from_date, to_date

    return {"result": tables, "schema": schema, 'from': from_date, 'to': to_date}


@ app.route('/report/', methods=['POST'])
@ token_required
def get_chests_report(user):
    data = request.get_json()
    account_id = data.get('account_id')
    from_date = data.get('from')
    to_date = data.get('to')
    chest_query = db.query(Chest).filter_by(account_id=account_id)
    players_query = db.query(ClanPlayer).filter_by(account_id=account_id)

    if from_date:
        chest_query = chest_query.filter(
            func.date(Chest.opened_in) >= from_date)
    if to_date:
        chest_query = chest_query.filter(func.date(Chest.opened_in) <= to_date)
    if len(chest_query.all()) < 1:
        return jsonify('no data')

    # put here all chests
    rules_list = [rule.to_dict() for rule in db.query(ChestRule).filter_by(
        account_id=account_id).all()]
    return jsonify(prepare_report(chest_query, players_query, rules_list, from_date, to_date))


@ app.route('/clan-report/', methods=['GET'])
def clan_report():
    hash = request.args.get('hash')
    report_query = db.query(Report).filter_by(hash=hash).first().get_query()

    account_id = report_query.get('account_id')
    from_date = report_query.get('from')
    to_date = report_query.get('to')
    chest_query = db.query(Chest).filter_by(account_id=account_id)
    players_query = db.query(ClanPlayer).filter_by(account_id=account_id)

    if from_date:
        chest_query = chest_query.filter(
            func.date(Chest.opened_in) >= from_date)
    if to_date:
        chest_query = chest_query.filter(func.date(Chest.opened_in) <= to_date)
    if len(chest_query.all()) < 1:
        return jsonify('no data')

    rules_list = [rule.to_dict() for rule in db.query(ChestRule).filter_by(
        account_id=account_id).all()]
    return jsonify(prepare_report(chest_query, players_query, rules_list, from_date, to_date))


def check_chest(name_path, chestname_path, chesttype_path, account_id, reader, ttl, full_path):

    current_name = ''
    current_chestname = ''
    current_chesttype = ''

    # player name
    all_players = db.query(ClanPlayer).filter_by(account_id=account_id).all()
    non_unique_players = list(
        filter(lambda player: player.difference(name_path) < 10, all_players))
    if (non_unique_players):
        current_name = non_unique_players[0].name
        player_id = non_unique_players[0].id
    else:
        new_player_name = reader.read_image(name_path)
        # read only here
        solid_path = f'true_images/names/{account_id}_{new_player_name}.png'

        if (os.path.exists(solid_path)):
            this_player = db.query(ClanPlayer).filter_by(
                path=solid_path).first()
            if(this_player):
                print('oh my player!')
                shutil.copy2(name_path, solid_path+'_copy.png')

                current_name = this_player.name
                player_id = this_player.id
            else:
                shutil.copy2(name_path, solid_path)
                new_player = ClanPlayer(
                    account_id, solid_path, new_player_name)
                db.add(new_player)
                db.commit()
                current_name = new_player_name
                player_id = new_player.id
        else:
            shutil.copy2(name_path, solid_path)
            new_player = ClanPlayer(account_id, solid_path, new_player_name)
            db.add(new_player)
            db.commit()
            current_name = new_player_name
            player_id = new_player.id

    # chest_name
    all_chestsnames = db.query(IdealChestName).all()
    non_unique_chestnames = list(
        filter(lambda chest: chest.difference(chestname_path) < 10, all_chestsnames))
    if (non_unique_chestnames):
        current_chestname = non_unique_chestnames[0].text
        chest_name_id = non_unique_chestnames[0].id
    else:
        new_chest_name_text = reader.read_image(chestname_path)
        solid_path = f'true_images/chest_names/{new_chest_name_text}.png'
        if (os.path.exists(solid_path)):
            this_chest = db.query(IdealChestName).filter_by(
                path=solid_path).first()
            print('oh my name!')
            if(this_chest):
                current_chestname = this_chest.text
                chest_name_id = this_chest.id
            else:
                shutil.copy2(chestname_path, solid_path)
                new_chest_name = IdealChestName(
                    solid_path, new_chest_name_text)
                db.add(new_chest_name)
                db.commit()
                current_chestname = new_chest_name_text
                chest_name_id = new_chest_name.id
        else:
            shutil.copy2(chestname_path, solid_path)
            new_chest_name = IdealChestName(solid_path, new_chest_name_text)
            db.add(new_chest_name)
            db.commit()
            current_chestname = new_chest_name_text
            chest_name_id = new_chest_name.id

    # chest_type
    all_cheststype = db.query(IdealChestType).all()
    non_unique_chesttypes = list(
        filter(lambda chest: chest.difference(chesttype_path) < 4, all_cheststype))
    if (non_unique_chesttypes):
        current_chesttype = non_unique_chesttypes[0].text
        chest_type_id = non_unique_chesttypes[0].id
    else:
        new_chest_type_text = reader.read_image(chesttype_path)
        solid_path = f'true_images/types/{new_chest_type_text}.png'
        if (os.path.exists(solid_path)):
            this_chest_type = db.query(IdealChestType).filter_by(
                path=solid_path).first()
            print('oh my type!')
            if(this_chest_type):
                current_chesttype = this_chest_type.text
                chest_type_id = this_chest_type.id
            else:
                shutil.copy2(chesttype_path, solid_path)
                new_chest_type = IdealChestType(
                    solid_path, new_chest_type_text)
                db.add(new_chest_type)
                db.commit()
                current_chesttype = new_chest_type_text
                chest_type_id = new_chest_type.id

        else:
            shutil.copy2(chesttype_path, solid_path)
            new_chest_type = IdealChestType(solid_path, new_chest_type_text)
            db.add(new_chest_type)
            db.commit()
            current_chesttype = new_chest_type_text
            chest_type_id = new_chest_type.id

    # chest_time

    time_text = reader.read_image(ttl, True).replace('O', '0').replace('О', '0').replace(
        'З', '3').replace('б', '6').replace('Б', '5').replace('S', '5').replace('l', '1').replace('-', '')
    timelist = list(filter(len, re.findall(r'\d*', time_text)))
    if (len(timelist) == 2):
        hour, minute = timelist
        get_on = datetime.now() - \
            timedelta(hours=19-int(hour), minutes=60 -
                      int(minute))-timedelta(hours=3)
    elif (len(timelist) == 3):
        hour, thrash, minute = timelist
        get_on = datetime.now() - \
            timedelta(hours=19-int(hour), minutes=60 -
                      int(minute))-timedelta(hours=3)
    elif (len(timelist) == 1) | (len(timelist) == 0) | (len(timelist) > 3):
        get_on = datetime.now()-timedelta(hours=3)

    return Chest(account_id, current_chesttype, current_name, current_chestname, get_on, full_path,  chest_type_id, chest_name_id, player_id)


@ app.route('/clan-players/', methods=['GET'])
@ token_required
def clanPlayersGet(user):
    account_id = request.args.get('account_id')
    players = db.query(ClanPlayer).filter_by(account_id=account_id)

    return jsonify([{"name": player.name, "path": player.path, "level": player.level, "id": player.id} for player in players])


@ app.route('/clan-player-bounded-chests/', methods=['GET'])
@ token_required
def clanPlayerBoundedChest(user):
    player_id = request.args.get('player_id')
    player = db.query(ClanPlayer).get(player_id)
    chests_count = db.query(Chest).filter_by(player_id=player_id).count()
    return jsonify({"name": player.name, "chests_count": chests_count})


@ app.route('/clan-players-delete/', methods=['POST'])
@ token_required
def clanPlayersDelete(user):
    data = request.get_json()

    account_id = data.get('account_id')
    player_id = data.get('player_id')
    with_chests = data.get('with_chests')

    db.query(ClanPlayer).filter_by(
        account_id=account_id, id=player_id).delete()

    db.commit()
    players = db.query(ClanPlayer).filter_by(account_id=account_id)

    return jsonify([{"name": player.name, "path": player.path, "level": player.level, "id": player.id} for player in players])


@ app.route('/clan-players-merge/', methods=['POST'])
@ token_required
def clanPlayersMerge(user):
    data = request.get_json()

    account_id = data.get('account_id')
    player_id = data.get('player_id')
    player_merge_id = data.get('player_merge_id')

    player_merge = db.query(ClanPlayer).filter_by(id=player_merge_id).first()
    db.query(Chest).filter_by(account_id=account_id, player_id=player_id).update(
        {'player_id': player_merge_id, 'player': player_merge.name})

    db.commit()
    players = db.query(ClanPlayer).filter_by(account_id=account_id)

    return jsonify([{"name": player.name, "path": player.path, "level": player.level, "id": player.id} for player in players])


@ app.route('/clan-players-edit/', methods=['POST'])
@ token_required
def clanPlayersEdit(user):
    data = request.get_json()

    account_id = data.get('account_id')
    player_id = data.get('player_id')
    player_name = data.get('name')

    player = db.query(ClanPlayer).filter_by(
        account_id=account_id, id=player_id).first()
    player.name = player_name

    db.commit()
    players = db.query(ClanPlayer).filter_by(account_id=account_id)

    return jsonify([{"name": player.name, "path": player.path, "level": player.level, "id": player.id} for player in players])


@ app.route('/clan-players-level/', methods=['POST'])
@ token_required
def clanPlayersChangeLevel(user):
    data = request.get_json()

    account_id = data.get('account_id')
    player_id = data.get('player_id')
    action = data.get('action')

    player = db.query(ClanPlayer).filter_by(
        account_id=account_id, id=player_id).first()

    if (player.level == None):
        player.level = 0

    if (action == "add"):
        player.level = player.level + 1
    if (action == "remove") & (player.level > 1):
        player.level = player.level - 1

    db.commit()
    players = db.query(ClanPlayer).filter_by(account_id=account_id)

    return jsonify([{"name": player.name, "path": player.path, "level": player.level, "id": player.id} for player in players])


def check_chest_and_save(player_name, chest_name, chest_type, account_id, reader, ttl, full_chest_image, check_needed):
    new_chest = check_chest(
        player_name, chest_name, chest_type, account_id, reader, ttl, full_chest_image)
    new_chest.check_needed = check_needed
    db.add(new_chest)
    db.commit()
    pass


def process_pipeline(reader, my_robot, account_id):
    print('started pipeline')
    current_image = None
    try:
        while (reader.is_button(my_robot.show_open_button())):
            check_needed = ''
            player_name, chest_type, chest_name, ttl, full_chest_image, all_chests_image = my_robot.get_chest_info()
            if(current_image != None):
                is_old_chest = reader.are_images_identical(
                    all_chests_image, current_image, False)
                if(is_old_chest):
                    # my_robot.click_open_button()
                    print('identical! click')
                    # shutil.copy2(all_chests_image,
                    #              'temp_images/check/_copy.png')
                    # shutil.copy2(
                    #     current_image, 'temp_images/check/old_copy.png')
                    # continue
                    check_needed = current_image

            current_image = all_chests_image
            check_chest_and_save(
                player_name, chest_name, chest_type, account_id, reader, ttl, full_chest_image, check_needed)
            my_robot.click_open_button()

    except Exception as e:
        my_robot.create_checking_screenshot()
        print(e)
    print('ended pipeline')


def lock_account(account, robot):
    account.is_locked = True
    account.selenium_url = robot.url
    account.selenium_session_id = robot.session_id
    db.commit()


def unlock_account(account):
    try:
        robo_killer(account.selenium_url,
                    account.selenium_session_id, account.id)
    except:
        return
    account.is_locked = False
    account.selenium_url = None
    account.selenium_session_id = None
    db.commit()


@app.route('/kill_process/', methods=['POST'])
@token_required
def kill_process(user):
    data = request.get_json()
    account_id = data['account_id']
    account = db.query(Account).filter_by(
        user_id=user.id, id=account_id).first()
    unlock_account(account)
    return jsonify({"Ok?": True})


@ app.route('/process/', methods=['POST'])
@ token_required
def process(user):

    data = request.get_json()
    account_id = data['account_id']
    account = db.query(Account).filter_by(
        user_id=user.id, id=account_id).first()
    # id=5).first()

    account_id = account.id

    locked = db.query(Account).filter_by(is_locked=True).first()
    if locked:
        return jsonify('already locked'), 409
    if not account:
        return jsonify('account not found'), 404
    account.is_locked = True
    db.commit()
    try:
        my_robot = Robot(account.to_login())
        lock_account(account, my_robot)
        my_robot.start()
    except Exception as e:
        my_robot.create_checking_screenshot()
        unlock_account(account)
        print(e)
        return jsonify({'message': "wrong login or password"}), 401

    # можно запустить без очереди ?
    # chests_count, banks_count = my_robot.count_chests_banks()

    my_robot.open_gifts_page()

    reader = OCR_reader()
    my_robot.banks()
    process_pipeline(reader, my_robot, account_id)
    my_robot.un_banks()
    process_pipeline(reader, my_robot, account_id)

    my_robot.create_checking_screenshot()
    unlock_account(account)
    return jsonify({"Ok?": True})


if __name__ == "__main__":
    # app.run('0.0.0.0',port=server_port)
    serve(app, host='0.0.0.0', port=5000, threads=16)
