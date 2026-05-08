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

@app.post("/generate-plan")
async def create_plan(task: StudyTask):
    daily_pages = task.total_pages / task.days_left
    plan = []
    total_progress = 0
    
    # 1. 집중도별 맞춤 학습 전략 메시지 & 복습 주기 설정
    if task.concentration >= 9:
        strategy = {
            "title": "🚀 고효율 파고들기 모드",
            "tip": "딥러닝 논문이나 물리 수식 유도처럼 깊은 사고가 필요한 공부에 최적입니다. 50분 집중 후 10분 휴식하는 뽀모도로 기법을 추천합니다.",
            "review_intervals": [3, 7] # 고집중은 복습 주기를 큼직하게
        }
    elif task.concentration >= 6:
        strategy = {
            "title": "⚖️ 꾸준한 밸런스 모드",
            "tip": "진도와 복습의 비율을 7:3으로 유지하세요. 아는 내용을 백지에 써보는 '능동적 회상'법이 가장 효과적입니다.",
            "review_intervals": [1, 3, 7] # 표준 주기
        }
    else:
        strategy = {
            "title": "🐢 거북이 스파르타 모드",
            "tip": "집중력이 낮을 땐 '분량'보다 '완성도'입니다. 20분 공부 후 5분 휴식하며, 복습이 벅차면 '어제 내용'만이라도 완벽히 보세요.",
            "review_intervals": [1, 2] # 부하를 줄이기 위해 짧은 주기만 반복
        }

    # 2. 날짜별 계획 생성
    for i in range(task.days_left):
        current_date = datetime.now() + timedelta(days=i)
        
        # 복습 항목 계산
        reviews = []
        for interval in strategy["review_intervals"]:
            if i >= interval:
                reviews.append(f"{i - interval + 1}일차")

        total_progress += (100 / task.days_left)
        
        plan.append({
            "day": i + 1,
            "date": current_date.strftime("%Y-%m-%d"),
            "study": f"{round(daily_pages, 1)}p",
            "review": reviews,
            "progress": min(100, round(total_progress, 1))
        })
        
    return {
        "subject": task.subject,
        "strategy": strategy,
        "plan": plan
    }

if __name__ == "__main__":
    import uvicorn
    # 배포 환경(Render)을 위해 포트 설정을 유동적으로 변경
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
