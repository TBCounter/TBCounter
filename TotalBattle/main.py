from fastapi import FastAPI, Depends, HTTPException, Request, WebSocket, WebSocketDisconnect, BackgroundTasks
import uvicorn
import asyncio
from typing import Union, List
from sqlalchemy import func
from fastapi.responses import FileResponse, HTMLResponse
import jwt
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
from models import init_db, SessionLocal, User, Account, Chest, Report, ChestRule, ClanPlayer, IdealChestName, IdealChestType, Queue  # noqa
from fastapi.security import OAuth2PasswordBearer
import yaml
from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash
from robot import Robot, OCR_reader, robo_killer, RobotCookie, FILE_PATH
import json
import shutil
import os
import re
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
init_db()

app = FastAPI()

SECRET_KEY = os.getenv("SECRET_KEY")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


@app.middleware("http")
async def add_cors_headers(request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    return response


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(token: str = Depends(oauth2_scheme),  db: Session = Depends(get_db)):
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user = db.query(User).filter_by(email=data['sub']).first()
        if not user:
            raise HTTPException(
                status_code=401,
                detail="User not found",
                headers={"WWW-Authenticate": "Basic"},
            )
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="User not found",
            headers={"WWW-Authenticate": "Basic"},
        )
    except (jwt.InvalidTokenError, Exception) as e:
        print(e)

        raise HTTPException(
            status_code=500,
            detail="jwt error",
            headers={"WWW-Authenticate": "Basic"},
        )


@app.get('/privacy-policy')
def privacyPolicy():
    with open('PrivacyPolicy.html') as file:
        return HTMLResponse(file.read())


@app.options("/{path:path}")
async def options_handler(path: str):
    return {
        "allowed_methods": ["OPTIONS", "POST"]
    }


@app.post('/register/')
async def register(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    user = User(**data)
    db.add(user)
    db.commit()
    return user.to_dict()


@app.post('/login/')
async def login(request: Request,  db: Session = Depends(get_db)):
    data = await request.json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return None

    user = db.query(User).filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
        return None

    token = jwt.encode({
        'sub': user.email,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(days=7)},
        SECRET_KEY, algorithm="HS256")
    return {'token': token, 'userName': user.email, 'userID': user.id}


@app.get('/info/')
def get_account_info(user: str = Depends(get_current_user),  db: Session = Depends(get_db)):
    accounts = db.query(Account).filter_by(user_id=user.id).all()
    response = []
    for account in accounts:
        acc_info = account.to_dict()
        chest_count = db.query(Chest).filter_by(account_id=account.id).filter(
            func.date(Chest.opened_in) == (datetime.now().date()-timedelta(hours=3))).count()
        acc_info['chest_count'] = chest_count
        response.append(acc_info)

    return response


@app.get('/changelog/')
def changelog():
    with open('changelog.yaml', encoding='utf8') as f:
        templates = yaml.safe_load(f)
        return templates


'''==================================='''


@app.get('/avatars/{name}')
def get_image(name):
    return FileResponse("avatars/"+name)


@app.get('/true_images/names/{name}')
def get_true_image(name):
    return FileResponse("true_images/names/"+name)


@app.get('/current_state/')
def get_current_state(request: Request, user: str = Depends(get_current_user)):
    account_id = request.query_params.get('account_id')
    return FileResponse(FILE_PATH + "temp_images/"+str(account_id)+"_screenshot.png")


@app.get('/temp_images/full_chests/{name}')
def get_chest_full_image(name):
    return FileResponse(FILE_PATH + "temp_images/full_chests/"+name)


@app.get('/temp_images/all_chests/{name}')
def get_chest_all_image(name):
    return FileResponse(FILE_PATH + "temp_images/all_chests/"+name)


@app.get('/chest-types/')
def getChestTypes(db: Session = Depends(get_db)):
    chests = [value for value in db.query(Chest.chest_type).distinct()]
    result = []
    for chest in chests:
        result.append(
            {
                "label": chest[0],
                "value": chest[0]
            }
        )

    return result


@app.get('/chest-names/')
def getChestNames(db: Session = Depends(get_db)):
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

    return final_result


@app.get('/scores-rules/')
def getScoresRules(request: Request, user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    account_id = request.query_params.get('account_id')
    rules = db.query(ChestRule).filter_by(account_id=account_id).all()

    return [{"group": rule.group, "scores": rule.scores, "ideal_chest_name": rule.ideal_chest_name,  "ideal_chest_type": rule.ideal_chest_type} for rule in rules]


@app.post('/scores-rules/')
async def postScoresRules(request: Request, user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    data = await request.json()
    account_id = data['account_id']
    new_rules = data['rules']
    db.query(ChestRule).filter_by(account_id=account_id).delete()

    for rule in new_rules:
        db.add(ChestRule(account_id,
                         rule.get('group'), float(rule.get('scores').replace(',', '.')) if type(rule.get('scores')) == str else rule.get('scores'), rule.get('ideal_chest_name'), rule.get('ideal_chest_type')))
    db.commit()
    print('ok???')
    rules = db.query(ChestRule).filter_by(account_id=account_id).all()
    return [{"group": rule.group, "scores": rule.scores, "ideal_chest_name": rule.ideal_chest_name,  "ideal_chest_type": rule.ideal_chest_type} for rule in rules]


@app.get('/my-login/')
async def get_my_login(request: Request, user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    id = request.query_params.get('id')
    account = db.query(Account).filter_by(id=int(id), user_id=user.id).first()
    return account.login


@app.delete('/info/')
async def delete_account(request: Request, user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    data = await request.json()
    id = data.get('id')
    db.query(Account).filter_by(id=id, user_id=user.id).delete()
    db.commit()
    return {}


@app.patch('/info/')
async def save_account_settings(request: Request, user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    data = await request.json()
    login = data.get('login')
    account = db.query(Account).filter_by(login=login, user_id=user.id).first()

    password = data.get('password')
    name = data.get('name')
    clan = data.get('clan')
    isTriumph = data.get('isTriumph')

    if(password):
        secure_password = jwt.encode(
            {'password': password}, SECRET_KEY, algorithm="HS256")
        account.password = secure_password
    account.name = name
    account.clan = clan
    account.isTriumph = isTriumph
    db.commit()
    return {}


@app.post('/info/')
async def add_account(request: Request, user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    data = await request.json()
    login = data.get('login')
    password = data.get('password')
    name = data.get('name')
    clan = data.get('clan')
    isTriumph = data.get('isTriumph')

    if(password):
        secure_password = jwt.encode(
            {'password': password}, SECRET_KEY, algorithm="HS256")
        try:
            my_robot = Robot(
                {"login": login, "password": secure_password, "isTriumph": isTriumph})
            my_robot.start()
        except:
            return {'message': "wrong login or password"}, 401

        avatar_path, name_text, clan_text = my_robot.info()
        new_account = Account(login, secure_password, user,
                              name_text, clan_text, avatar_path, isTriumph)
        db.add(new_account)
        db.commit()
        return {"ava": avatar_path, "name": name_text, "clan": clan_text}
    else:
        shutil.copy2('./avatars/EMPTY.png', './avatars/'+login+".png")
        new_ava = './avatars/'+login+".png"

        new_account = Account(login, "", user,
                              name, clan, new_ava, isTriumph)
        db.add(new_account)
        db.commit()
        return {"ava": new_ava, "name": name, 'clan': clan}


@app.get('/list/')
def get_chests_list(request: Request, user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    account_id = request.query_params.get('account_id')
    order_by = request.query_params.get('sort')

    direction = order_by[:1]
    order_by = order_by[1:]

    page = int(request.query_params.get('page'))

    if(direction == '+'):
        chests = db.query(Chest).filter_by(account_id=account_id).order_by(
            Chest.__table__.c[order_by].asc()).limit(25).offset((page-1)*25)
        # .paginate(page=page, per_page=25, error_out=False)
    else:
        chests = db.query(Chest).filter_by(account_id=account_id).order_by(
            Chest.__table__.c[order_by].desc()).limit(25).offset((page-1)*25)
    total = db.query(Chest).filter_by(account_id=account_id).count()
    return {"total": total,
            "total_pages": total/25,
            "page": page,
            "items": [chest.to_dict() for chest in chests]}  # return player name from another table


@app.post('/list/')
async def get_file_list(request: Request, user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    data = await request.json()
    account_id = data.get('account_id')
    from_date = data.get('from')
    to_date = data.get('to')

    from_time = data.get('from_time')
    to_time = data.get('to_time')

    query = db.query(Chest).filter_by(account_id=account_id)

    if from_date:
        from_datetime = datetime.strptime(
            from_date+' '+from_time, '%Y-%m-%d %H:%M')
        query = query.filter(Chest.opened_in
                             >= from_datetime)
    if to_date:
        to_datetime = datetime.strptime(
            to_date + ' ' + to_time, '%Y-%m-%d %H:%M')
        query = query.filter(Chest.opened_in
                             <= to_datetime)
    df = pd.read_sql(query.statement, query.session.bind, index_col='id')
    df.drop(['account_id', 'chest_type_id',
            'chest_name_id', 'player_id', 'path'], axis=1, inplace=True)

    filename = f"report_{account_id}_{from_date}_{to_date}_.xlsx"
    df.to_excel(filename)

    return FileResponse(path=filename)


@app.post('/save-report/')
async def save_chests_report(request: Request, user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    data = await request.json()

    rep = Report(json.dumps(data), data.get('account_id'))
    db.add(rep)
    db.commit()
    return rep.hash


@app.post('/save-chest/')
async def save_chest(request: Request, user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    data = await request.json()

    chest_id = data.get('chest_id')

    chest = db.query(Chest).filter_by(id=chest_id).first()
    chest.check_needed = ''
    db.commit()
    return {"Ok?": True}


@app.post('/delete-chest/')
async def delete_chest(request: Request, user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    data = await request.json()

    chest_id = data.get('chest_id')
    db.query(Chest).filter_by(id=chest_id).delete()
    db.commit()
    return {"Ok?": True}


def prepare_report(query, players_query, chest_rules, from_date, to_date, from_time, to_time, db):
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
               "headerFilter": "input", "frozen": True, "cssClass": "report-table__column--name"}]

    schema.append({
        'title': 'Очки',
        'field': 'scores',
        "minWidth": "60px",
        "headerFilter": "number",
        "headerFilterPlaceholder": "at least...",
        "headerFilterFunc": ">=",
        "cssClass": "report-table__column--scores"
    })
    schema.append({
        'title': 'Сумма',
        'field': 'sum',
        "minWidth": "60px",
        "headerFilter": "number",
        "headerFilterPlaceholder": "at least...",
        "headerFilterFunc": ">=",
        "cssClass": "report-table__column--sum"
    })
    added_types = []
    col_index = 0
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

            col_index += 1
            resulting = {
                'title': global_type,
                "cssClass": "report-table__column--index"+str(col_index),
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
                        "headerFilterFunc": ">=",
                        "cssClass": "report-table__column--index"+str(col_index),
                    }
                )

            schema.append(resulting)
        else:
            col_index += 1
            schema.append({
                'title': current_title,
                'field': current_title,
                "minWidth": "60px",
                "headerVertical": "flip",
                "headerFilter": "number",
                "headerFilterPlaceholder": "at least...",
                "headerFilterFunc": ">=",
                "cssClass": "report-table__column--index"+str(col_index),

            })

    # df.to_csv('pre-report.csv') from_date, to_date

    return {"result": tables, "schema": schema, 'from': from_date, 'to': to_date}


@app.post('/report/')
async def get_chests_report(request: Request, user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    data = await request.json()
    account_id = data.get('account_id')
    from_date = data.get('from')
    to_date = data.get('to')
    chest_query = db.query(Chest).filter_by(account_id=account_id)
    players_query = db.query(ClanPlayer).filter_by(account_id=account_id)

    from_time = data.get('from_time')
    to_time = data.get('to_time')

    if from_date:
        from_datetime = datetime.strptime(
            from_date+' '+from_time, '%Y-%m-%d %H:%M')
        chest_query = chest_query.filter(Chest.opened_in
                                         >= from_datetime)
    if to_date:
        to_datetime = datetime.strptime(
            to_date + ' ' + to_time, '%Y-%m-%d %H:%M')
        chest_query = chest_query.filter(Chest.opened_in
                                         <= to_datetime)
    if len(chest_query.all()) < 1:
        return 'no data'

    # put here all chests
    rules_list = [rule.to_dict() for rule in db.query(ChestRule).filter_by(
        account_id=account_id).all()]
    return prepare_report(chest_query, players_query, rules_list, from_date, to_date, from_time, to_time, db)


@app.get('/clan-report/')
def clan_report(request: Request, db: Session = Depends(get_db)):
    hash = request.query_params.get('hash')
    report_query = db.query(Report).filter_by(hash=hash).first().get_query()

    account_id = report_query.get('account_id')
    from_date = report_query.get('from')
    to_date = report_query.get('to')

    from_time = report_query.get('from_time')
    to_time = report_query.get('to_time')

    chest_query = db.query(Chest).filter_by(account_id=account_id)
    players_query = db.query(ClanPlayer).filter_by(account_id=account_id)

    if from_date:
        from_datetime = datetime.strptime(
            from_date+' '+from_time, '%Y-%m-%d %H:%M')
        chest_query = chest_query.filter(Chest.opened_in
                                         >= from_datetime)
    if to_date:
        to_datetime = datetime.strptime(
            to_date + ' ' + to_time, '%Y-%m-%d %H:%M')
        chest_query = chest_query.filter(Chest.opened_in
                                         <= to_datetime)
    if len(chest_query.all()) < 1:
        return 'no data'

    rules_list = [rule.to_dict() for rule in db.query(ChestRule).filter_by(
        account_id=account_id).all()]
    return prepare_report(chest_query, players_query, rules_list, from_date, to_date, from_time, to_time, db)


def check_chest(name_path, chestname_path, chesttype_path, account_id, reader, ttl, full_path, db):

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
                current_name = new_player_name
                player_id = new_player.id
        else:
            shutil.copy2(name_path, solid_path)
            new_player = ClanPlayer(account_id, solid_path, new_player_name)
            db.add(new_player)
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
                current_chestname = new_chest_name_text
                chest_name_id = new_chest_name.id
        else:
            shutil.copy2(chestname_path, solid_path)
            new_chest_name = IdealChestName(solid_path, new_chest_name_text)
            db.add(new_chest_name)
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
                current_chesttype = new_chest_type_text
                chest_type_id = new_chest_type.id

        else:
            shutil.copy2(chesttype_path, solid_path)
            new_chest_type = IdealChestType(solid_path, new_chest_type_text)
            db.add(new_chest_type)
            current_chesttype = new_chest_type_text
            chest_type_id = new_chest_type.id
    db.commit()

    # chest_time

    # time_text = reader.read_image(ttl, True).replace('O', '0').replace('О', '0').replace(
    #     'З', '3').replace('б', '6').replace('Б', '5').replace('S', '5').replace('l', '1').replace('-', '')
    # timelist = list(filter(len, re.findall(r'\d*', time_text)))
    # if (len(timelist) == 2):
    #     hour, minute = timelist
    #     get_on = datetime.now() - \
    #         timedelta(hours=19-int(hour), minutes=60 -
    #                   int(minute))-timedelta(hours=3)
    # elif (len(timelist) == 3):
    #     hour, thrash, minute = timelist
    #     get_on = datetime.now() - \
    #         timedelta(hours=19-int(hour), minutes=60 -
    #                   int(minute))-timedelta(hours=3)
    # elif (len(timelist) == 1) | (len(timelist) == 0) | (len(timelist) > 3):
    #     get_on = datetime.now()-timedelta(hours=3)
    get_on = datetime.now()
    return Chest(account_id, current_chesttype, current_name, current_chestname, get_on, full_path,  chest_type_id, chest_name_id, player_id)


@ app.get('/clan-players/')
def clanPlayersGet(request: Request, user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    account_id = request.query_params.get('account_id')
    players = db.query(ClanPlayer).filter_by(account_id=account_id)

    return [{"name": player.name, "path": player.path, "level": player.level, "id": player.id} for player in players]


@ app.get('/clan-player-bounded-chests/')
def clanPlayerBoundedChest(request: Request,  user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    player_id = request.query_params.get('player_id')
    player = db.query(ClanPlayer).get(player_id)
    chests_count = db.query(Chest).filter_by(player_id=player_id).count()
    return {"name": player.name, "chests_count": chests_count}


@ app.post('/clan-players-delete/')
async def clanPlayersDelete(request: Request, user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    data = await request.json()

    account_id = data.get('account_id')
    player_id = data.get('player_id')
    with_chests = data.get('with_chests')

    db.query(ClanPlayer).filter_by(
        account_id=account_id, id=player_id).delete()

    db.commit()
    players = db.query(ClanPlayer).filter_by(account_id=account_id)

    return [{"name": player.name, "path": player.path, "level": player.level, "id": player.id} for player in players]


@ app.post('/clan-players-merge/')
async def clanPlayersMerge(request: Request, user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    data = await request.json()

    account_id = data.get('account_id')
    player_id = data.get('player_id')
    player_merge_id = data.get('player_merge_id')

    player_merge = db.query(ClanPlayer).filter_by(id=player_merge_id).first()
    db.query(Chest).filter_by(account_id=account_id, player_id=player_id).update(
        {'player_id': player_merge_id, 'player': player_merge.name})

    db.commit()
    players = db.query(ClanPlayer).filter_by(account_id=account_id)

    return [{"name": player.name, "path": player.path, "level": player.level, "id": player.id} for player in players]


@ app.post('/clan-players-edit/')
async def clanPlayersEdit(request: Request, user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    data = await request.json()

    account_id = data.get('account_id')
    player_id = data.get('player_id')
    player_name = data.get('name')

    player = db.query(ClanPlayer).filter_by(
        account_id=account_id, id=player_id).first()
    player.name = player_name

    db.commit()
    players = db.query(ClanPlayer).filter_by(account_id=account_id)

    return [{"name": player.name, "path": player.path, "level": player.level, "id": player.id} for player in players]


@app.post('/clan-players-level/')
async def clanPlayersChangeLevel(request: Request, user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    data = await request.json()

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

    return [{"name": player.name, "path": player.path, "level": player.level, "id": player.id} for player in players]


def check_chest_and_save(player_name, chest_name, chest_type, account_id, reader, ttl, full_chest_image, check_needed, db):
    new_chest = check_chest(
        player_name, chest_name, chest_type, account_id, reader, ttl, full_chest_image, db)
    new_chest.check_needed = check_needed
    db.add(new_chest)
    db.commit()
    pass


def process_pipeline(reader, my_robot, account_id, db):
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
                    print('identical! click')
                    check_needed = current_image

            current_image = all_chests_image
            check_chest_and_save(
                player_name, chest_name, chest_type, account_id, reader, ttl, full_chest_image, check_needed, db)
            my_robot.click_open_button()

    except Exception as e:
        my_robot.create_checking_screenshot()
        print(e)
    print('ended pipeline')


def lock_account(account, robot, db):
    account.is_locked = True
    account.selenium_url = robot.url
    account.selenium_session_id = robot.session_id
    db.commit()


def unlock_account(account, db):
    try:
        robo_killer(account.selenium_url,
                    account.selenium_session_id, account.id)
    except Exception as e:
        account.is_locked = False
        db.commit()
        return str(e)
    account.is_locked = False
    account.selenium_url = None
    account.selenium_session_id = None
    db.commit()
    return True


@app.post('/kill_process/')
async def kill_process(request: Request, user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    data = await request.json()
    account_id = data['account_id']
    account = db.query(Account).filter_by(
        user_id=user.id, id=account_id).first()
    result = unlock_account(account, db)
    return {"Ok?": result}


# @app.post('/add_account_cookie/')
# async def add_account(request: Request, user: str = Depends(get_current_user), db: Session = Depends(get_db)):
#     data = await request.json()
#     cookies = data.get('cookies')
#     url = data.get('url')

#     try:
#         my_robot = RobotCookie(
#             {"login": login, "password": secure_password, "isTriumph": isTriumph})
#         my_robot.start()
#     except:
#         return {'message': "wrong login or password"}, 401

#     avatar_path, name_text, clan_text = my_robot.info()
#     new_account = Account(avatar=avatar_path, login=name_text)
#     db.add(new_account)
#     db.commit()
#     return {"ava": avatar_path, "name": name_text, "clan": clan_text}

def run_from_queue(db):
    has_in_queue = db.query(Queue).filter_by(
        done=False).order_by(Queue.timestamp.asc()).first()

    if not has_in_queue:
        print('queue is empty')
        return
    print('run from queue')

    cookies = json.loads(has_in_queue.cookies)
    url = has_in_queue.url
    account_id = has_in_queue.account_id

    account = db.query(Account).filter_by(id=account_id).first()

    locked = db.query(Account).filter_by(is_locked=True).first()
    if locked:
        return

    if not account:
        return

    chests_query = db.query(Chest).filter_by(account_id=account_id)
    chest_count = chests_query.filter(
        func.date(Chest.opened_in) == (datetime.now().date()-timedelta(hours=3))).count()

    if (chest_count > 600 and account.vip == False):
        has_in_queue.done = True
        raise HTTPException(
            status_code=402,
            detail="day limit",
        )

    account.is_locked = True
    has_in_queue.active = True
    db.commit()

    my_robot = RobotCookie(account.to_login(), url, cookies)

    try:
        lock_account(account, my_robot, db)
        my_robot.start()
    except Exception as e:
        my_robot.create_checking_screenshot()
        unlock_account(account, db)
        print(e)
        has_in_queue.done = True
        raise HTTPException(
            status_code=401,
            detail="wrong login or password",
        )
    my_robot.open_gifts_page()

    reader = OCR_reader()
    my_robot.banks()
    process_pipeline(reader, my_robot, account_id, db)
    my_robot.un_banks()
    process_pipeline(reader, my_robot, account_id, db)

    my_robot.create_checking_screenshot()
    unlock_account(account, db)
    has_in_queue.done = True
    db.commit()
    run_from_queue(db)
    return


@app.post('/process_cookie/')
async def process_cookie(request: Request, user: str = Depends(get_current_user), db: Session = Depends(get_db), back_tasks=BackgroundTasks):

    # check if anyone in queue
    # run_from_queue(db, back_tasks=back_tasks)

    data = await request.json()
    cookies = data.get('cookies')
    print(cookies)
    url = data.get('url')
    account_id = data.get('account_id')
    account = db.query(Account).filter_by(
        user_id=user.id, id=account_id).first()

    account_id = account.id

    # chests

    chests_query = db.query(Chest).filter_by(account_id=account_id)
    chest_count = chests_query.filter(
        func.date(Chest.opened_in) == (datetime.now().date()-timedelta(hours=3))).count()

    if (chest_count > 600 and account.vip == False):
        raise HTTPException(
            status_code=402,
            detail="day limit",
        )

    # lock
    locked = db.query(Account).filter_by(is_locked=True).first()
    if locked:
        has_in_queue = db.query(Queue).filter_by(
            done=False, account_id=account_id).first()
        if not has_in_queue:
            new_process = Queue(
                url=url, account_id=account_id, cookies=json.dumps(cookies))
            db.add(new_process)
            print('was locked, added')
            db.commit()
        print('was locked, so locked')
        raise HTTPException(
            status_code=409,
            detail="already locked",
        )
    if not account:
        raise HTTPException(
            status_code=404,
            detail="account not found",
        )
    account.is_locked = True
    db.commit()

    my_robot = RobotCookie(account.to_login(), url, cookies)

    try:
        lock_account(account, my_robot, db)
        my_robot.start()
    except Exception as e:
        my_robot.create_checking_screenshot()
        unlock_account(account, db)
        print(e)
        raise HTTPException(
            status_code=401,
            detail="wrong login or password",
        )

    # можно запустить без очереди ?
    # chests_count, banks_count = my_robot.count_chests_banks()

    my_robot.open_gifts_page()

    reader = OCR_reader()
    my_robot.banks()
    process_pipeline(reader, my_robot, account_id, db)
    my_robot.un_banks()
    process_pipeline(reader, my_robot, account_id, db)

    my_robot.create_checking_screenshot()
    unlock_account(account, db)
    run_from_queue(db)
    return {"Ok?": True}


@app.post('/process/')
async def process(request: Request, user: str = Depends(get_current_user), db: Session = Depends(get_db)):

    data = await request.json()
    account_id = data['account_id']
    account = db.query(Account).filter_by(
        user_id=user.id, id=account_id).first()
    # id=5).first()

    account_id = account.id

    locked = db.query(Account).filter_by(is_locked=True).first()
    if locked:
        raise HTTPException(
            status_code=409,
            detail="already locked",
        )
    if not account:
        raise HTTPException(
            status_code=404,
            detail="account not found",
        )
    account.is_locked = True
    db.commit()
    my_robot = Robot(account.to_login())
    try:
        lock_account(account, my_robot, db)
        my_robot.start()
    except Exception as e:
        my_robot.create_checking_screenshot()
        unlock_account(account, db)
        print(e)
        raise HTTPException(
            status_code=401,
            detail="wrong login or password",
        )

    # можно запустить без очереди ?
    # chests_count, banks_count = my_robot.count_chests_banks()

    my_robot.open_gifts_page()

    reader = OCR_reader()
    my_robot.banks()
    process_pipeline(reader, my_robot, account_id, db)
    my_robot.un_banks()
    process_pipeline(reader, my_robot, account_id, db)

    my_robot.create_checking_screenshot()
    unlock_account(account, db)
    return {"Ok?": True}


'''==================================='''


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def send_personal_data(self, message: str, websocket: WebSocket):
        await websocket.send_text(json.dumps(message, default=str, ensure_ascii=False))

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.websocket("/chests/{account_id}")
async def websocket_endpoint_chests(websocket: WebSocket, account_id: int, db: Session = Depends(get_db)):
    await manager.connect(websocket)
    try:
        while True:
            chests_query = db.query(Chest).filter_by(account_id=account_id)
            total = chests_query.count()
            chests = chests_query.order_by(
                Chest.__table__.c['opened_in'].desc()).limit(25)

            chest_count = chests_query.filter(
                func.date(Chest.opened_in) == (datetime.now().date()-timedelta(hours=3))).count()
            await manager.send_personal_data({
                "chests": [chest.to_dict() for chest in chests],
                "page": 1,
                "total": total,
                "total_pages": total/25,
                "today_chests": chest_count
            }, websocket)
            await asyncio.sleep(6)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        # await manager.broadcast(f"Client #{account_id} left the chat")
    except:
        manager.disconnect(websocket)


@app.websocket("/info/{user_id}")
async def websocket_endpoint_info(websocket: WebSocket, user_id: int, db: Session = Depends(get_db)):
    await manager.connect(websocket)
    try:
        while True:
            accounts = db.query(Account).filter_by(user_id=user_id).all()
            unavailable = db.query(Account).filter_by(is_locked=True).all()
            response = []
            for account in accounts:
                acc = account.to_dict()
                if len(unavailable) > 0:
                    acc['unavailable'] = True
                response.append(acc)

            await manager.send_personal_data(response, websocket)
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        # await manager.broadcast(f"Client #{account_id} left the chat")
    except:
        manager.disconnect(websocket)


@app.websocket("/queue")
async def websocket_endpoint_queue(websocket: WebSocket,  db: Session = Depends(get_db)):
    await manager.connect(websocket)
    try:
        while True:
            queue = db.query(Queue).filter_by(done=False).all()

            await manager.send_personal_data([q.to_dict() for q in queue], websocket)
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        # await manager.broadcast(f"Client #{account_id} left the chat")
    except:
        manager.disconnect(websocket)


if __name__ == "__main__":
    uvicorn.run("main:app", host='0.0.0.0', port=5000, workers=3)
