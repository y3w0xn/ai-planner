from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, timedelta
from fastapi.responses import FileResponse
import os
import math

app = FastAPI()

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
    plan = []
    
    # 1. 집중도에 따른 실제 '공부 수행 일수' 결정
    # 최상: 기간의 60%만 사용(몰입), 보통: 80%, 낮음: 100%(천천히)
    if task.concentration >= 9:
        active_days_count = max(1, math.ceil(task.days_left * 0.6))
        strategy = {"title": "⚡ 초몰입 단기 완성", "tip": "에너지가 높을 때 몰아칩니다. 남은 기간의 절반은 자유시간입니다!"}
    elif task.concentration >= 6:
        active_days_count = max(1, math.ceil(task.days_left * 0.8))
        strategy = {"title": "📅 선택과 집중 모드", "tip": "주말이나 특정 일을 쉬기 위해 주중에 집중적으로 배분했습니다."}
    else:
        active_days_count = task.days_left
        strategy = {"title": "🧘 슬로우 페이스 모드", "tip": "부담을 최소화하기 위해 매일 조금씩 꾸준히 나아갑니다."}

    # 2. 정수 페이지 배분 알고리즘
    base_pages = task.total_pages // active_days_count
    extra_pages = task.total_pages % active_days_count
    
    current_progress = 0
    day_counter = 0

    for i in range(task.days_left):
        current_date = datetime.now() + timedelta(days=i)
        
        # 공부하는 날인지 판단 (앞쪽에 공부를 몰아넣음)
        if day_counter < active_days_count:
            # 마지막 공부 날에 남은 페이지 올림 처리
            pages_today = base_pages + (1 if day_counter < extra_pages else 0)
            study_msg = f"{pages_today}p"
            current_progress += (pages_today / task.total_pages) * 100
            
            # 복습 로직 (가장 중요한 직전 공부일 것만)
            reviews = [f"{day_counter}일차 내용"] if day_counter > 0 else []
            day_counter += 1
        else:
            study_msg = "휴식 및 보충"
            reviews = ["밀린 부분 검토"]

        plan.append({
            "day": i + 1,
            "date": current_date.strftime("%Y-%m-%d"),
            "study": study_msg,
            "review": reviews,
            "progress": min(100, round(current_progress, 1))
        })
        
    return {"subject": task.subject, "strategy": strategy, "plan": plan}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
