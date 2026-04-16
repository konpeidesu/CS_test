from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse
from typing import Dict, List, Optional
import json
import asyncio
import random
import time

app = FastAPI()

TEAMS = ["A-1", "A-2", "B-1", "B-2", "C-1", "C-2"]


def default_questions() -> List[dict]:
    return [
        {"id": 1, "title": "創立年クイズ", "question": "会社の創立年は西暦何年？", "answer": "2010", "points": 2, "hint": "2000年代後半〜2010年代前半です"},
        {"id": 2, "title": "社長の好物", "question": "社長の好きな食べ物は？", "answer": "カレー", "points": 2, "hint": "スパイシーな料理です"},
        {"id": 3, "title": "オフィスの階数", "question": "本社オフィスは何階にある？", "answer": "5", "points": 2, "hint": "1桁の奇数です"},
        {"id": 4, "title": "社員数", "question": "現在の社員数は約何人？", "answer": "100", "points": 2, "hint": "3桁です"},
        {"id": 5, "title": "スローガン", "question": "会社のスローガンは？", "answer": "信頼と成長", "points": 3, "hint": "漢字4文字が2つです"},
        {"id": 6, "title": "人気イベント", "question": "昨年の社内イベントで一番人気だったのは？", "answer": "BBQ", "points": 2, "hint": "屋外で行うイベントです"},
        {"id": 7, "title": "公式キャラ", "question": "会社の公式キャラクターの名前は？", "answer": "いない", "points": 3, "hint": "ひっかけ問題かも？"},
        {"id": 8, "title": "自販機の人気", "question": "自販機で一番売れている飲み物は？", "answer": "コーヒー", "points": 2, "hint": "カフェインが入っています"},
        {"id": 9, "title": "最寄り駅", "question": "会社の最寄り駅はどこ？", "answer": "渋谷", "points": 2, "hint": "東京の主要ターミナル駅の1つです"},
        {"id": 10, "title": "最大部署", "question": "社内で一番人数が多い部署は？", "answer": "開発部", "points": 3, "hint": "エンジニアが多い部署です"},
        {"id": 11, "title": "設立月", "question": "会社が設立された月は？（数字で）", "answer": "4", "points": 2, "hint": "新年度が始まる月です"},
        {"id": 12, "title": "社名の由来", "question": "社名の由来になった言葉は？", "answer": "つながり", "points": 4, "hint": "人と人の関係を表す言葉です"},
        {"id": 13, "title": "フロアの数", "question": "オフィスは何フロアを使っている？", "answer": "2", "points": 2, "hint": "1より多く3より少ないです"},
        {"id": 14, "title": "ランチ人気店", "question": "社員に一番人気のランチスポットは？", "answer": "コンビニ", "points": 2, "hint": "どこにでもあるお店です"},
        {"id": 15, "title": "社内制度", "question": "社内で人気の福利厚生制度は？", "answer": "リモートワーク", "points": 3, "hint": "家でもできる働き方です"},
        {"id": 16, "title": "会議室の名前", "question": "一番大きい会議室の名前は？", "answer": "富士", "points": 3, "hint": "日本一高い山です"},
        {"id": 17, "title": "朝会の曜日", "question": "全社朝会は何曜日？", "answer": "月曜日", "points": 2, "hint": "週の始まりの日です"},
        {"id": 18, "title": "創業者の出身", "question": "創業者の出身都道府県は？", "answer": "大阪", "points": 4, "hint": "西日本の大都市です"},
        {"id": 19, "title": "ロゴの色", "question": "会社ロゴのメインカラーは？", "answer": "青", "points": 2, "hint": "空や海の色です"},
        {"id": 20, "title": "Slack絵文字", "question": "Slackで一番使われている絵文字は？", "answer": "👍", "points": 3, "hint": "賛同を示すジェスチャーです"},
        {"id": 21, "title": "社内部活", "question": "一番部員が多い社内部活は？", "answer": "フットサル", "points": 3, "hint": "ボールを蹴るスポーツです"},
        {"id": 22, "title": "平均年齢", "question": "社員の平均年齢は約何歳？", "answer": "32", "points": 3, "hint": "30代前半です"},
        {"id": 23, "title": "PC支給", "question": "入社時に支給されるPCのメーカーは？", "answer": "Mac", "points": 2, "hint": "リンゴのマークです"},
        {"id": 24, "title": "忘年会芸", "question": "昨年の忘年会で優勝した出し物は？", "answer": "漫才", "points": 4, "hint": "お笑いの形式の1つです"},
        {"id": 25, "title": "エレベーター", "question": "オフィスビルのエレベーターは何台？", "answer": "3", "points": 2, "hint": "奇数です"},
        {"id": 26, "title": "社内用語", "question": "社内で「レビュー」のことを何と呼ぶ？", "answer": "レビュー", "points": 2, "hint": "そのままかも？"},
        {"id": 27, "title": "最長在籍", "question": "最も在籍年数が長い社員は何年目？", "answer": "15", "points": 4, "hint": "10年以上です"},
        {"id": 28, "title": "オフィス植物", "question": "オフィスに置いてある観葉植物の名前は？", "answer": "パキラ", "points": 3, "hint": "幸運の木とも呼ばれます"},
        {"id": 29, "title": "Wi-Fiパスワード", "question": "ゲスト用Wi-Fiのパスワードのヒント：何の名前？", "answer": "会社名", "points": 2, "hint": "そのまんまです"},
        {"id": 30, "title": "最終問題", "question": "この会社で一番大切にしている価値観は？", "answer": "チームワーク", "points": 4, "hint": "みんなで協力することです"},
    ]


class QuizGame:
    def __init__(self):
        self.teams = {t: 0.0 for t in TEAMS}
        self.questions: List[dict] = default_questions()
        self.team_status: Dict[str, Dict[int, dict]] = {t: {} for t in TEAMS}
        self.first_solver: Dict[int, Optional[str]] = {}
        self.random_penalty: Dict[int, Optional[str]] = {}
        self.connections: List[WebSocket] = []
        self.admin_connections: List[WebSocket] = []
        self.game_started: bool = False

    def submit_answer(self, team, question_id, answer):
        if team not in self.teams:
            return {"success": False, "message": "無効なチームです"}
        q = next((q for q in self.questions if q["id"] == question_id), None)
        if not q:
            return {"success": False, "message": "問題が見つかりません"}
        status = self.team_status[team].get(question_id, {"solved": False, "hint_used": False, "wrong_count": 0})
        if status["solved"]:
            return {"success": False, "message": "既に正解済みです"}
        correct = answer.strip() == q["answer"].strip()
        if correct:
            status["solved"] = True
            self.teams[team] += q["points"]
            self.teams[team] = max(0, self.teams[team])
            bonus_msg = None
            penalty_msg = None
            if question_id not in self.first_solver:
                self.first_solver[question_id] = team
                self.teams[team] += 1.0
                self.teams[team] = max(0, self.teams[team])
                bonus_msg = f"{team} が最速正解ボーナス +1点！"
                penalty_target = random.choice(TEAMS)
                self.random_penalty[question_id] = penalty_target
                self.teams[penalty_target] = max(0, self.teams[penalty_target] - 1.0)
                penalty_msg = f"ランダム減点: {penalty_target} が -1点！"
            self.team_status[team][question_id] = status
            return {"success": True, "correct": True, "message": "正解！", "points_earned": q["points"], "bonus_msg": bonus_msg, "penalty_msg": penalty_msg}
        else:
            status["wrong_count"] += 1
            self.teams[team] -= 0.5
            self.teams[team] = max(0, self.teams[team])
            self.team_status[team][question_id] = status
            return {"success": True, "correct": False, "message": f"不正解... (-0.5点) 誤答回数: {status['wrong_count']}"}

    def use_hint(self, team, question_id):
        if team not in self.teams:
            return {"success": False, "message": "無効なチームです"}
        q = next((q for q in self.questions if q["id"] == question_id), None)
        if not q or not q.get("hint"):
            return {"success": False, "message": "ヒントがありません"}
        status = self.team_status[team].get(question_id, {"solved": False, "hint_used": False, "wrong_count": 0})
        hint_text = q["hint"]
        if not status["hint_used"]:
            status["hint_used"] = True
            self.teams[team] -= 0.5
            self.teams[team] = max(0, self.teams[team])
            self.team_status[team][question_id] = status
            return {"success": True, "hint": hint_text, "message": "ヒント表示 (-0.5点)", "already_used": False}
        else:
            return {"success": True, "hint": hint_text, "message": "ヒント表示済み", "already_used": True}

    def get_team_state(self, team):
        qs = []
        for q in self.questions:
            st = self.team_status[team].get(q["id"], {"solved": False, "hint_used": False, "wrong_count": 0})
            qs.append({"id": q["id"], "title": q["title"], "points": q["points"], "has_hint": bool(q.get("hint")), "solved": st.get("solved", False), "hint_used": st.get("hint_used", False), "wrong_count": st.get("wrong_count", 0)})
        return {"team": team, "score": self.teams[team], "questions": qs, "game_started": self.game_started}

    def get_question_detail(self, question_id, team):
        q = next((qn for qn in self.questions if qn["id"] == question_id), None)
        if not q:
            return None
        st = self.team_status[team].get(question_id, {"solved": False, "hint_used": False, "wrong_count": 0})
        return {"id": q["id"], "title": q["title"], "question": q["question"], "points": q["points"], "has_hint": bool(q.get("hint")), "solved": st.get("solved", False), "hint_used": st.get("hint_used", False), "wrong_count": st.get("wrong_count", 0)}

    def get_admin_state(self):
        return {"teams": {t: self.teams[t] for t in TEAMS}, "team_status": {t: {str(qid): s for qid, s in statuses.items()} for t, statuses in self.team_status.items()}, "first_solver": {str(k): v for k, v in self.first_solver.items()}, "random_penalty": {str(k): v for k, v in self.random_penalty.items()}, "questions": self.questions, "game_started": self.game_started}

    def reset(self):
        conns = self.connections
        admin_conns = self.admin_connections
        self.__init__()
        self.connections = conns
        self.admin_connections = admin_conns


game = QuizGame()


async def broadcast_scores():
    scores = {t: game.teams[t] for t in TEAMS}
    data = json.dumps({"type": "scores_update", "data": scores}, ensure_ascii=False)
    for ws in game.connections + game.admin_connections:
        try:
            await ws.send_text(data)
        except Exception:
            pass


async def broadcast_admin():
    data = json.dumps({"type": "admin_state", "data": game.get_admin_state()}, ensure_ascii=False)
    for ws in game.admin_connections:
        try:
            await ws.send_text(data)
        except Exception:
            pass


async def broadcast_event(event):
    data = json.dumps({"type": "event", "data": event}, ensure_ascii=False)
    for ws in game.connections + game.admin_connections:
        try:
            await ws.send_text(data)
        except Exception:
            pass


@app.websocket("/ws/player")
async def player_ws(websocket: WebSocket):
    await websocket.accept()
    game.connections.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            if msg["type"] == "get_state":
                state = game.get_team_state(msg["team"])
                await websocket.send_text(json.dumps({"type": "team_state", "data": state}, ensure_ascii=False))
            elif msg["type"] == "get_question":
                detail = game.get_question_detail(msg["question_id"], msg["team"])
                await websocket.send_text(json.dumps({"type": "question_detail", "data": detail}, ensure_ascii=False))
            elif msg["type"] == "answer":
                result = game.submit_answer(msg["team"], msg["question_id"], msg["answer"])
                await websocket.send_text(json.dumps({"type": "answer_result", "data": result}, ensure_ascii=False))
                if result.get("correct") and result.get("bonus_msg"):
                    await broadcast_event({"bonus_msg": result["bonus_msg"], "penalty_msg": result["penalty_msg"]})
                await broadcast_scores()
                await broadcast_admin()
                state = game.get_team_state(msg["team"])
                await websocket.send_text(json.dumps({"type": "team_state", "data": state}, ensure_ascii=False))
            elif msg["type"] == "use_hint":
                result = game.use_hint(msg["team"], msg["question_id"])
                await websocket.send_text(json.dumps({"type": "hint_result", "data": result}, ensure_ascii=False))
                await broadcast_scores()
                await broadcast_admin()
    except WebSocketDisconnect:
        if websocket in game.connections:
            game.connections.remove(websocket)


@app.websocket("/ws/admin")
async def admin_ws(websocket: WebSocket):
    await websocket.accept()
    game.admin_connections.append(websocket)
    await websocket.send_text(json.dumps({"type": "admin_state", "data": game.get_admin_state()}, ensure_ascii=False))
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            if msg["type"] == "start_game":
                game.game_started = True
                await broadcast_event({"message": "ゲームが開始されました！"})
                await broadcast_admin()
                for ws in game.connections:
                    try:
                        await ws.send_text(json.dumps({"type": "game_started"}, ensure_ascii=False))
                    except Exception:
                        pass
            elif msg["type"] == "stop_game":
                game.game_started = False
                await broadcast_admin()
            elif msg["type"] == "reset":
                game.reset()
                await broadcast_admin()
                await broadcast_scores()
                for ws in game.connections:
                    try:
                        await ws.send_text(json.dumps({"type": "game_reset"}, ensure_ascii=False))
                    except Exception:
                        pass
            elif msg["type"] == "get_state":
                await websocket.send_text(json.dumps({"type": "admin_state", "data": game.get_admin_state()}, ensure_ascii=False))
    except WebSocketDisconnect:
        if websocket in game.admin_connections:
            game.admin_connections.remove(websocket)


@app.get("/", response_class=HTMLResponse)
async def index():
    return FileResponse("static/player.html")


@app.get("/admin", response_class=HTMLResponse)
async def admin():
    return FileResponse("static/admin.html")


@app.get("/screen", response_class=HTMLResponse)
async def screen():
    return FileResponse("static/screen.html")
