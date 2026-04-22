from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse
from typing import Dict, List, Optional
import json
import asyncio
import random
import time
import math

app = FastAPI()

TEAMS = ["A-1", "A-2", "B-1", "B-2", "C-1", "C-2", "EDL"]
EDL_TEAM = "EDL"


def default_questions() -> List[dict]:
    return [
        {"id": 1, "title": "川合航平さんの犬", "question": "川合航平さんの飼っている犬の名前は？", "answer": "ぽんさん", "choices": ["ぽんさん", "ぷんさん", "ぺんさん"], "points": 3, "hint": "コバナシ"},
        {"id": 2, "title": "出退勤システム", "question": "出退勤をWEBで行うシステムの名称は？", "answer": "TimePro-VG", "choices": ["TimePro-VG", "TimePro-XG", "TimePro-YG"], "points": 2, "hint": ""},
        {"id": 3, "title": "大脇ジュリオ駿平さん", "question": "大脇ジュリオ駿平さんはどこのハーフ？", "answer": "ブラジル", "choices": ["ブラジル", "日本", "アメリカ"], "points": 4, "hint": "聞いてみよう"},
        {"id": 4, "title": "ポータルサイト", "question": "MNCのポータルサイトの名称は？", "answer": "マクネコ", "choices": ["マクネコ", "マクニコ", "マクマク"], "points": 2, "hint": ""},
        {"id": 5, "title": "渡辺弦一郎さん", "question": "渡辺弦一郎さんはどこの熱狂的なファンか？", "answer": "浦和レッズ", "choices": ["浦和レッズ", "読売ジャイアンツ", "FCバルセロナ"], "points": 4, "hint": "聞いてみよう"},
        {"id": 6, "title": "MNCのフロア", "question": "MNCのフロアは2ビルの何階から何階まで？", "answer": "3～6階", "choices": ["3～6階", "4～6階", "3～7階"], "points": 2, "hint": ""},
        {"id": 7, "title": "新オフィス建設予定地", "question": "新オフィスの建設予定場所は何の跡地？", "answer": "新横浜プリンスペペ", "choices": ["新横浜プリンスペペ", "ホテルアソシア新横浜", "マクニカ第1ビル"], "points": 3, "hint": ""},
        {"id": 8, "title": "ラジオCM", "question": "マクニカのラジオCMが流れる番組名は？", "answer": "オールナイトニッポン", "choices": ["オールナイトニッポン", "ラジオ日経", "JUNK"], "points": 3, "hint": ""},
        {"id": 9, "title": "一番売れている製品", "question": "MNCで一番売れている製品は？", "answer": "CrowdStrike", "choices": ["CrowdStrike", "Cato Networks", "Thales"], "points": 3, "hint": ""},
        {"id": 10, "title": "和久輝さんの売上", "question": "和久輝さんの昨年度の売上は？", "answer": "106M円", "choices": ["106M円", "53M円", "20M円"], "points": 3, "hint": "PowerBI"},
        {"id": 11, "title": "藤田光太郎さんのおすすめ", "question": "藤田光太郎さんがおすすめしている場所は？", "answer": "石垣島", "choices": ["石垣島", "マダガスカル島", "戸塚"], "points": 3, "hint": "コバナシ"},
        {"id": 12, "title": "マッチングアプリ", "question": "社内で活用されているマッチングアプリは？", "answer": "Pinder", "choices": ["Pinder", "Ninder", "Minder"], "points": 2, "hint": ""},
        {"id": 13, "title": "田中佑磨さんの出身", "question": "田中佑磨さんの出身県は？", "answer": "香川県", "choices": ["香川県", "福岡県", "岩手県"], "points": 3, "hint": "コバナシ"},
        {"id": 14, "title": "品川オフィス", "question": "品川オフィスのマクニカのフロアは何階？", "answer": "5，6階", "choices": ["5，6階", "4階", "3，4階"], "points": 3, "hint": ""},
        {"id": 15, "title": "R6グレード基本給", "question": "R6グレードの基本給の上限額は？", "answer": "45万円", "choices": ["45万円", "50万円", "60万円"], "points": 4, "hint": "人事ポータル＞人事制度"},
        {"id": 16, "title": "齊藤諒太さん", "question": "齊藤諒太さんは何オタク？", "answer": "アイドル", "choices": ["アイドル", "鉄道", "アニメ"], "points": 3, "hint": "コバナシ"},
        {"id": 17, "title": "CMの芸能人", "question": "マクニカのCMで起用されている芸能人は？", "answer": "キンタロー、要潤", "choices": ["キンタロー、要潤", "どぶろっく", "サンドウィッチマン"], "points": 2, "hint": ""},
        {"id": 18, "title": "スポンサーサッカー", "question": "マクニカがスポンサーをしているサッカーチームは？", "answer": "横浜FC", "choices": ["横浜FC", "横浜F・マリノス", "湘南ベルマーレ"], "points": 2, "hint": ""},
        {"id": 19, "title": "川合航平さんの元居住地", "question": "川合航平さんの昨年末まで住んでいた場所は？", "answer": "歌舞伎町", "choices": ["歌舞伎町", "渋谷", "丸の内"], "points": 4, "hint": "聞いてみよう"},
        {"id": 20, "title": "位置確認アプリ", "question": "社員がオフィスのどこにいるか分かるアプリは？", "answer": "TeamsNavi", "choices": ["TeamsNavi", "Macnica Navi", "Phoone App"], "points": 2, "hint": ""},
        {"id": 21, "title": "ロジの場所", "question": "マクニカのロジがある場所は？", "answer": "新子安", "choices": ["新子安", "湘南", "平塚"], "points": 2, "hint": ""},
        {"id": 22, "title": "買収した会社", "question": "マクニカが自動運転ビジネスをするために買収した会社は？", "answer": "Naviya", "choices": ["Naviya", "CyberKnight", "グローセル"], "points": 2, "hint": ""},
        {"id": 23, "title": "和久輝さんのルーツ", "question": "和久輝さんはどこのハーフか？", "answer": "純ジャパ", "choices": ["純ジャパ", "ポルトガル", "ブラジル"], "points": 4, "hint": "聞いてみよう"},
        {"id": 24, "title": "日帰り出張の日当", "question": "日帰り出張をしたときにもらえる日当はいくら？", "answer": "2000円", "choices": ["2000円", "3000円", "5000円"], "points": 3, "hint": "人事ポータル＞人事制度"},
        {"id": 25, "title": "1ビル1階の名称", "question": "新横浜1ビル1階の名称は？", "answer": "MET VALLEY", "choices": ["MET VALLEY", "MAC VALLEY", "MET HILLS"], "points": 2, "hint": ""},
        {"id": 26, "title": "新卒2年目女性社員", "question": "新卒2年目の女性社員は何人？", "answer": "7人", "choices": ["7人", "9人", "11人"], "points": 2, "hint": ""},
        {"id": 27, "title": "ランチ亭の予約", "question": "ランチ亭の予約締め切り時間は？", "answer": "9時25分", "choices": ["9時25分", "10時25分", "10時55分"], "points": 3, "hint": "福利厚生"},
        {"id": 28, "title": "セキュリティ製品", "question": "マクニカが開発してるセキュリティ製品は？", "answer": "Macnica ASM", "choices": ["Macnica ASM", "Macnica EDR", "Macnica NET"], "points": 3, "hint": ""},
        {"id": 29, "title": "社員旅行", "question": "昨年度MNCが行った社員旅行はどこ？", "answer": "名古屋", "choices": ["名古屋", "大阪", "福岡"], "points": 3, "hint": "マクネコ"},
        {"id": 30, "title": "EDLの正式名称", "question": "EDLの正式名称は？", "answer": "Education Development Leader", "choices": ["Education Development Leader", "Education Leader", "Education Diversity Leader"], "points": 2, "hint": ""},
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
        self.game_state: str = "waiting"  # waiting / running / ended / result
        self.game_start_time: Optional[float] = None
        self.time_limit: int = 1200  # 20 minutes
        self.comeback_bonus_applied: bool = False
        self.comeback_bonus: Dict[str, Dict[int, float]] = {t: {} for t in TEAMS}
        self.edl_unlocked_qids: set = set()  # EDL解放済み問題ID

    @property
    def game_started(self):
        return self.game_state == "running"

    def init_edl_unlock(self):
        """EDL開始時解放: 2点問題全部 + 3点問題の半分(ランダム)"""
        q2 = [q["id"] for q in self.questions if q["points"] == 2]
        q3 = [q["id"] for q in self.questions if q["points"] == 3]
        random.shuffle(q3)
        half3 = q3[:len(q3) // 2]
        self.edl_unlocked_qids = set(q2) | set(half3)

    def unlock_edl_hard_questions(self):
        """残り時間半分時に3点問題の残り半分+4点問題を解放"""
        q3_all = set(q["id"] for q in self.questions if q["points"] == 3)
        q4_all = set(q["id"] for q in self.questions if q["points"] == 4)
        newly_unlocked = (q3_all | q4_all) - self.edl_unlocked_qids
        self.edl_unlocked_qids |= q3_all | q4_all
        return list(newly_unlocked)

    def is_edl_question_locked(self, question_id):
        """EDLチームにとってこの問題がロック中かどうか"""
        return question_id not in self.edl_unlocked_qids

    def sync_time_limit(self):
        if self.game_state != "running" or not self.game_start_time:
            return False
        if (time.time() - self.game_start_time) < self.time_limit:
            return False
        self.game_state = "ended"
        return True

    def current_remaining_seconds(self):
        self.sync_time_limit()
        if self.game_state == "running" and self.game_start_time:
            elapsed = time.time() - self.game_start_time
            return max(0, self.time_limit - elapsed)
        return 0 if self.game_state == "ended" else None

    def question_points_for_team(self, team, question_id):
        override_points = self.comeback_bonus.get(team, {}).get(question_id)
        if override_points is not None:
            return override_points
        q = next((qn for qn in self.questions if qn["id"] == question_id), None)
        if not q:
            return 0
        return q["points"]

    def apply_comeback_bonus(self):
        if self.comeback_bonus_applied:
            return []
        self.comeback_bonus_applied = True
        top_score = max(self.teams.values()) if self.teams else 0
        applied = []
        for team, score in self.teams.items():
            gap = top_score - score
            if gap < 10:
                continue
            unanswered = [
                q for q in self.questions
                if not self.team_status[team].get(q["id"], {}).get("solved", False)
            ]
            if not unanswered:
                continue
            target_total_points = gap - 3
            if target_total_points <= 0:
                continue
            target_count = max(1, math.floor(0.3 * len(unanswered)))
            target_count = min(target_count, len(unanswered))
            selected = []
            base_total = 0
            for candidate_count in range(target_count, 0, -1):
                max_trials = min(80, max(20, len(unanswered) * 4))
                if len(unanswered) <= candidate_count:
                    candidate_pool = [list(unanswered)]
                else:
                    candidate_pool = [random.sample(unanswered, candidate_count) for _ in range(max_trials)]
                best_selected = None
                best_score = None
                best_base_total = 0
                for candidate_selected in candidate_pool:
                    candidate_base_total = sum(q["points"] for q in candidate_selected)
                    if candidate_base_total > target_total_points - candidate_count:
                        continue
                    point_buckets = {}
                    for question in candidate_selected:
                        point_buckets[question["points"]] = point_buckets.get(question["points"], 0) + 1
                    spread_score = (
                        len(point_buckets),
                        -max(point_buckets.values()),
                        candidate_base_total,
                    )
                    if best_score is None or spread_score > best_score:
                        best_selected = candidate_selected
                        best_score = spread_score
                        best_base_total = candidate_base_total
                if best_selected is not None:
                    selected = best_selected
                    base_total = best_base_total
                    break
            if not selected:
                continue
            bonus_points = (target_total_points - base_total) / len(selected)
            if bonus_points < 1:
                continue
            for q in selected:
                self.comeback_bonus[team][q["id"]] = q["points"] + bonus_points
            applied.append({
                "team": team,
                "gap": gap,
                "count": len(selected),
                "points": bonus_points,
                "question_ids": [q["id"] for q in selected],
            })
        return applied

    def submit_answer(self, team, question_id, answer):
        self.sync_time_limit()
        if self.game_state != "running":
            return {"success": False, "message": "ゲームは終了しました"}
        if team not in self.teams:
            return {"success": False, "message": "無効なチームです"}
        q = next((q for q in self.questions if q["id"] == question_id), None)
        if not q:
            return {"success": False, "message": "問題が見つかりません"}
        # EDLチームのロックチェック
        if team == EDL_TEAM and self.is_edl_question_locked(question_id):
            return {"success": False, "message": "🔒 この問題はまだ解放されていません"}
        status = self.team_status[team].get(question_id, {"solved": False, "hint_used": False, "wrong_count": 0})
        if status["solved"]:
            return {"success": False, "message": "既に正解済みです"}
        correct = answer.strip() == q["answer"].strip()
        if correct:
            earned_points = self.question_points_for_team(team, question_id)
            status["solved"] = True
            self.teams[team] = max(0, self.teams[team] + earned_points)
            bonus_msg = None
            penalty_messages = []
            if question_id not in self.first_solver:
                self.first_solver[question_id] = team
                # EDLは最速ボーナス(+1点)なし、ただしランダム減点対象にはなる
                if team != EDL_TEAM:
                    self.teams[team] = max(0, self.teams[team] + 1.0)
                    bonus_msg = f"{team} が最速正解ボーナス +1点！"
                # ランダム減点は全チーム対象（EDL含む）
                penalty_target = random.choice(TEAMS)
                self.random_penalty[question_id] = penalty_target
                self.teams[penalty_target] = max(0, self.teams[penalty_target] - 1.0)
                penalty_messages.append(f"ランダム減点: {penalty_target} が -1点！")
            self.team_status[team][question_id] = status
            return {"success": True, "correct": True, "message": "正解！", "points_earned": earned_points, "bonus_msg": bonus_msg, "penalty_msg": " / ".join(penalty_messages) if penalty_messages else None}
        # 誤答: EDLは-5点、他は-0.5点
        status["wrong_count"] += 1
        penalty = 5.0 if team == EDL_TEAM else 0.5
        self.teams[team] = max(0, self.teams[team] - penalty)
        self.team_status[team][question_id] = status
        msg = f"不正解... (-{penalty:.1g}点) 誤答回数: {status['wrong_count']}"
        return {"success": True, "correct": False, "message": msg, "penalty_msg": None}

    def use_hint(self, team, question_id):
        self.sync_time_limit()
        if self.game_state != "running":
            return {"success": False, "message": "ゲームは終了しました"}
        if team not in self.teams:
            return {"success": False, "message": "無効なチームです"}
        # EDLチームはヒント使用禁止
        if team == EDL_TEAM:
            return {"success": False, "message": "🚫 EDLチームはヒントを使用できません"}
        q = next((q for q in self.questions if q["id"] == question_id), None)
        if not q or not q.get("hint"):
            return {"success": False, "message": "ヒントがありません"}
        status = self.team_status[team].get(question_id, {"solved": False, "hint_used": False, "wrong_count": 0})
        hint_text = q["hint"]
        if not status["hint_used"]:
            status["hint_used"] = True
            self.teams[team] = max(0, self.teams[team] - 1.0)
            self.team_status[team][question_id] = status
            return {"success": True, "hint": hint_text, "message": "ヒント表示 (-1点)", "already_used": False}
        return {"success": True, "hint": hint_text, "message": "ヒント表示済み", "already_used": True}

    def get_team_state(self, team):
        self.sync_time_limit()
        qs = []
        for q in self.questions:
            st = self.team_status[team].get(q["id"], {"solved": False, "hint_used": False, "wrong_count": 0})
            points = self.question_points_for_team(team, q["id"])
            is_bonus = q["id"] in self.comeback_bonus.get(team, {})
            locked = (team == EDL_TEAM) and self.is_edl_question_locked(q["id"])
            qs.append({"id": q["id"], "title": q["title"], "points": points, "base_points": q["points"], "is_bonus": is_bonus, "has_hint": bool(q.get("hint")), "solved": st.get("solved", False), "hint_used": st.get("hint_used", False), "wrong_count": st.get("wrong_count", 0), "locked": locked})
        remaining = self.current_remaining_seconds()
        return {"team": team, "score": self.teams[team], "teams": {t: self.teams[t] for t in TEAMS}, "questions": qs, "game_started": self.game_state == "running", "game_state": self.game_state, "remaining_seconds": remaining, "is_edl": team == EDL_TEAM}

    def get_question_detail(self, question_id, team):
        self.sync_time_limit()
        q = next((qn for qn in self.questions if qn["id"] == question_id), None)
        if not q:
            return None
        st = self.team_status[team].get(question_id, {"solved": False, "hint_used": False, "wrong_count": 0})
        choices = list(q.get("choices", []))
        random.shuffle(choices)
        points = self.question_points_for_team(team, q["id"])
        is_bonus = q["id"] in self.comeback_bonus.get(team, {})
        return {"id": q["id"], "title": q["title"], "question": q["question"], "points": points, "base_points": q["points"], "is_bonus": is_bonus, "has_hint": bool(q.get("hint")), "solved": st.get("solved", False), "hint_used": st.get("hint_used", False), "wrong_count": st.get("wrong_count", 0), "choices": choices, "game_state": self.game_state, "remaining_seconds": self.current_remaining_seconds()}

    def get_admin_state(self):
        remaining = self.current_remaining_seconds()
        return {"teams": {t: self.teams[t] for t in TEAMS}, "team_status": {t: {str(qid): s for qid, s in statuses.items()} for t, statuses in self.team_status.items()}, "first_solver": {str(k): v for k, v in self.first_solver.items()}, "random_penalty": {str(k): v for k, v in self.random_penalty.items()}, "questions": self.questions, "comeback_bonus_applied": self.comeback_bonus_applied, "comeback_bonus": {t: {str(qid): pts for qid, pts in bonuses.items()} for t, bonuses in self.comeback_bonus.items()}, "game_started": self.game_state == "running", "game_state": self.game_state, "remaining_seconds": remaining, "time_limit_minutes": self.time_limit // 60, "edl_unlocked_qids": list(self.edl_unlocked_qids)}

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


async def broadcast_bonus_applied(applied):
    data = json.dumps({"type": "comeback_bonus_applied", "data": applied}, ensure_ascii=False)
    for ws in game.connections + game.admin_connections:
        try:
            await ws.send_text(data)
        except Exception:
            pass


async def trigger_edl_unlock(started_at, time_limit):
    """残り時間が半分になったらEDLの3点後半+4点問題を解放"""
    await asyncio.sleep(time_limit / 2)
    if game.game_state != "running" or game.game_start_time != started_at:
        return
    newly = game.unlock_edl_hard_questions()
    if newly:
        await broadcast_event({"message": f"🔓 EDLチームに新問題が解放されました！（3点問題の残り半分 + 4点問題）"})
        # EDLプレイヤーに状態更新を通知
        for ws in game.connections:
            try:
                await ws.send_text(json.dumps({"type": "edl_unlocked", "unlocked_qids": newly}, ensure_ascii=False))
            except Exception:
                pass
        await broadcast_admin()


async def trigger_comeback_bonus_at_deadline(started_at, time_limit):
    await asyncio.sleep(max(0, time_limit - 180 + 0.1))
    if game.game_state != "running" or game.game_start_time != started_at:
        return
    applied = game.apply_comeback_bonus()
    if applied:
        teams = ", ".join(item["team"] for item in applied)
        await broadcast_event({"message": f"Comeback bonus: {teams}"})
    await broadcast_bonus_applied(applied)
    await broadcast_admin()


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
                if result.get("bonus_msg") or result.get("penalty_msg"):
                    await broadcast_event({"bonus_msg": result.get("bonus_msg"), "penalty_msg": result.get("penalty_msg")})
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
                minutes = msg.get("time_limit_minutes", game.time_limit // 60)
                try:
                    minutes = int(minutes)
                except (TypeError, ValueError):
                    minutes = 20
                game.time_limit = max(1, min(minutes, 999)) * 60
                game.game_state = "running"
                game.game_start_time = time.time()
                game.init_edl_unlock()  # EDL初期解放問題をセット
                asyncio.create_task(trigger_comeback_bonus_at_deadline(game.game_start_time, game.time_limit))
                asyncio.create_task(trigger_edl_unlock(game.game_start_time, game.time_limit))
                await broadcast_event({"message": "ゲームが開始されました！"})
                await broadcast_admin()
                for ws in game.connections:
                    try:
                        await ws.send_text(json.dumps({"type": "game_started"}, ensure_ascii=False))
                    except Exception:
                        pass
            elif msg["type"] == "stop_game":
                game.game_state = "waiting"
                await broadcast_admin()
            elif msg["type"] == "end_game":
                game.game_state = "ended"
                await broadcast_event({"message": "⏰ ゲーム終了！"})
                await broadcast_admin()
                for ws in game.connections:
                    try:
                        await ws.send_text(json.dumps({"type": "game_ended"}, ensure_ascii=False))
                    except Exception:
                        pass
            elif msg["type"] == "show_results":
                if game.game_state == "ended":
                    game.game_state = "result"
                    await broadcast_event({"message": "🏆 結果発表！"})
                    await broadcast_admin()
                    await broadcast_scores()
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
