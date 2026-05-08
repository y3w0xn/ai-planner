from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import datetime, timedelta
import uvicorn

app = FastAPI()

class StudyTask(BaseModel):
    subject: str
    total_pages: int
    days_left: int
    concentration: int

import os

@app.get("/", response_class=HTMLResponse)
async def read_root():
    # 현재 실행 중인 main.py 파일의 폴더 경로를 가져옵니다.
    base_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_path, "index.html")
    
    try:
        with open(file_path, encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>에러: index.html 파일을 찾을 수 없습니다! 파일이 미소강 폴더 안에 있는지 확인하세요.</h1>"

# main.py의 create_plan 함수 부분을 아래와 같이 수정해보세요.

@app.post("/generate-plan")
async def create_plan(task: StudyTask):
    # 집중도(concentration)를 가중치로 활용
    # 10(높음) -> 분량 그대로, 4(낮음) -> 복습 주기를 더 촘촘하게 설정
    
    daily_pages = task.total_pages / task.days_left
    plan = []
    total_progress = 0
    
    for i in range(task.days_left):
        current_date = datetime.now() + timedelta(days=i)
        
        # 집중도 스타일에 따른 복습 주기 설정
        if task.concentration >= 9:
            review_intervals = [3, 7] # 고집중: 굵직하게 복습
        elif task.concentration >= 6:
            review_intervals = [1, 3, 7] # 보통: 표준 주기
        else:
            review_intervals = [1, 2, 3, 5, 7] # 낮음: 망각 방지를 위해 아주 자주 복습

        reviews = []
        for interval in review_intervals:
            if i >= interval:
                reviews.append(f"{i - interval + 1}일차 내용")

        total_progress += (100 / task.days_left)
        
        plan.append({
            "day": i + 1,
            "date": current_date.strftime("%Y-%m-%d"),
            "study": f"{round(daily_pages, 1)}p",
            "review": reviews,
            "progress": min(100, round(total_progress, 1))
        })
        
    return {"subject": task.subject, "plan": plan}

# 이 부분이 핵심입니다! 터미널 명령어 없이도 실행되게 해줘요.
if __name__ == "__main__":
    import uvicorn
    # log_level="info"를 넣어 서버 상태를 더 자세히 봅니다.
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
