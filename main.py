from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, timedelta
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os

app = FastAPI()

# HTML 파일을 불러오기 위한 경로 설정
@app.get("/")
async def read_index():
    return FileResponse('index.html')

class StudyTask(BaseModel):
    subject: str
    total_pages: int
    days_left: int
    concentration: int

# main.py의 로직 부분만 이렇게 수정해 보세요

@app.post("/generate-plan")
async def create_plan(task: StudyTask):
    daily_pages = task.total_pages / task.days_left
    plan = []
    total_progress = 0
    
    if task.concentration >= 9:
        strategy = {
            "title": "🚀 고효율 전략: '장기 기억' 전환 모드",
            "tip": "이미 이해도가 높으므로 7일 전 내용만 가볍게 훑으세요. 남는 에너지는 오늘 진도의 '심화 학습'에 쏟으십시오.",
            "review_intervals": [7] # 최상일 땐 굳이 어제껄 볼 필요 없음 (장기 기억 강화)
        }
    elif task.concentration >= 6:
        strategy = {
            "title": "⚖️ 표준 전략: '중요 지점' 복습 모드",
            "tip": "어제 내용과 3일 전 내용을 복습하세요. 이 주기가 망각을 막는 가장 효율적인 구간입니다.",
            "review_intervals": [1, 3] # 표준 주기는 2개로 제한
        }
    else:
        strategy = {
            "title": "🐢 생존 전략: '직전 내용' 사수 모드",
            "tip": "복습이 밀리면 의욕이 꺾입니다. 오늘은 오직 '어제 배운 것'만 복습하고 나머지는 과감히 버리세요!",
            "review_intervals": [1] # 낮을 땐 단 하나만 제대로 복습
        }

    for i in range(task.days_left):
        current_date = datetime.now() + timedelta(days=i)
        
        # [핵심] 집중도에 따라 설정된 간격 중 '가장 중요한 것'만 추출
        reviews = []
        for interval in strategy["review_intervals"]:
            if i >= interval:
                reviews.append(f"{i - interval + 1}일차")
        
        # 만약 복습이 너무 많아지면 최근 2개만 남김 (안전장치)
        reviews = reviews[-2:] 

        total_progress += (100 / task.days_left)
        plan.append({
            "day": i + 1,
            "date": current_date.strftime("%Y-%m-%d"),
            "study": f"{round(daily_pages, 1)}p",
            "review": reviews,
            "progress": min(100, round(total_progress, 1))
        })
        
    return {"subject": task.subject, "strategy": strategy, "plan": plan}

if __name__ == "__main__":
    import uvicorn
    # 배포 환경(Render)을 위해 포트 설정을 유동적으로 변경
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
