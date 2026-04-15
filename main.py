from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse
from typing import Dict, List, Optional
import json
import asyncio

app = FastAPI()


class QuizGame:
    def __init__(self):
        self.teams: Dict[str, int] = {}
        self.questions: List[dict] = self._default_questions()
        self.current_question_index: int = -1
        self.current_question: Optional[dict] = None
        self.answers: Dict[str, str] = {}
        self.phase: str = "waiting"
        self.connections: List[WebSocket] = []
        self.admin_connections: List[WebSocket] = []

    def _default_questions(self) -> List[dict]:
        return [
            {"id": 1, "question": "会社の創立年は？", "choices": ["2000年", "2005年", "2010年", "2015年"], "answer": "2010年", "points": 10},
            {"id": 2, "question": "社長の好きな食べ物は？", "choices": ["寿司", "ラーメン", "カレー", "ハンバーグ"], "answer": "カレー", "points": 10},
            {"id": 3, "question": "オフィスがある階は？", "choices": ["3階", "5階", "7階", "10階"], "answer": "5階", "points": 10},
            {"id": 4, "question": "社員数は約何人？", "choices": ["50人", "100人", "200人", "500人"], "answer": "100人", "points": 10},
            {"id": 5, "question": "会社のスローガンは？", "choices": ["挑戦と革新", "信頼と成長", "夢と情熱", "つながりと創造"], "answer": "信頼と成長", "points": 10},
            {"id": 6, "question": "昨年の社内イベントで一番人気だったのは？", "choices": ["BBQ", "ボウリング大会", "社員旅行", "忘年会"], "answer": "BBQ", "points": 20},
            {"id": 7, "question": "会社の公式キャラクターの名前は？", "choices": ["ワークくん", "ビズたん", "テックちゃん", "いない"], "answer": "いない", "points": 20},
            {"id": 8, "question": "自販機で一番売れている飲み物は？", "choices": ["コーヒー", "お茶", "水", "エナジードリンク"], "answer": "コーヒー", "points": 10},
            {"id": 9, "question": "会社の最寄り駅はどこ？", "choices": ["東京駅", "新宿駅", "渋谷駅", "品川駅"], "answer": "渋谷駅", "points": 10},
            {"id": 10, "question": "社内で一番多い部署は？", "choices": ["営業部", "開発部", "人事部", "マーケティング部"], "answer": "開発部", "points": 20},
        ]

    def add_team(self, team_name: str) -> bool:
        if team_name in self.teams:
            return False
        self.teams[team_name] = 0
        return True

    def remove_team(self, team_name: str):
        if team_name in self.teams:
            del self.teams[team_name]

    def next_question(self) -> Optional[dict]:
        self.current_question_index += 1
        self.answers = {}
        if self.current_question_index >= len(self.questions):
            self.phase = "finished"
            self.current_question = None
            return None
        self.current_question = self.questions[self.current_question_index]
        self.phase = "question"
        return self.current_question

    def submit_answer(self, team_name: str, answer: str) -> bool:
        if team_name not in self.teams:
            return False
        if team_name in self.answers:
            return False
        self.answers[team_name] = answer
        return True

    def judge(self) -> dict:
        if not self.current_question:
            return {}
        correct = self.current_question["answer"]
        points = self.current_question["points"]
        results = {}
        for team, answer in self.answers.items():
            is_correct = answer == correct
            if is_correct:
                self.teams[team] += points
            results[team] = {"answer": answer, "correct": is_correct, "points": points if is_correct else 0}
        for team in self.teams:
            if team not in results:
                results[team] = {"answer": "未回答", "correct": False, "points": 0}
        self.phase = "result"
        return {"correct_answer": correct, "results": results, "scores": self.teams}

    def reset(self):
        self.__init__()

    def get_state(self) -> dict:
        q = None
        if self.current_question:
            q = {
                "id": self.current_question["id"],
                "question": self.current_question["question"],
                "choices": self.current_question["choices"],
                "points": self.current_question["points"],
                "number": self.current_question_index + 1,
                "total": len(self.questions),
            }
        return {
            "phase": self.phase,
            "teams": self.teams,
            "current_question": q,
            "answers_received": list(self.answers.keys()),
            "total_questions": len(self.questions),
        }


game = QuizGame()


async def broadcast(message: dict):
    data = json.dumps(message, ensure_ascii=False)
    for ws in game.connections + game.admin_connections:
        try:
            await ws.send_text(data)
        except Exception:
            pass


async def broadcast_state():
    await broadcast({"type": "state", "data": game.get_state()})


@app.websocket("/ws/player")
async def player_ws(websocket: WebSocket):
    await websocket.accept()
    game.connections.append(websocket)
    await websocket.send_text(json.dumps({"type": "state", "data": game.get_state()}, ensure_ascii=False))
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            if msg["type"] == "answer":
                game.submit_answer(msg["team"], msg["answer"])
                await broadcast_state()
    except WebSocketDisconnect:
        game.connections.remove(websocket)


@app.websocket("/ws/admin")
async def admin_ws(websocket: WebSocket):
    await websocket.accept()
    game.admin_connections.append(websocket)
    await websocket.send_text(json.dumps({"type": "state", "data": game.get_state()}, ensure_ascii=False))
    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            if msg["type"] == "add_team":
                game.add_team(msg["team"])
                await broadcast_state()
            elif msg["type"] == "remove_team":
                game.remove_team(msg["team"])
                await broadcast_state()
            elif msg["type"] == "next_question":
                game.next_question()
                await broadcast_state()
            elif msg["type"] == "judge":
                result = game.judge()
                await broadcast({"type": "judge_result", "data": result})
                await asyncio.sleep(0.1)
                await broadcast_state()
            elif msg["type"] == "reset":
                game.reset()
                await broadcast_state()
            elif msg["type"] == "update_questions":
                game.questions = msg["questions"]
                await broadcast_state()
    except WebSocketDisconnect:
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
