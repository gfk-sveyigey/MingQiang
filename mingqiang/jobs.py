# from mingqiang.services import map
from mingqiang.model import User, Group, House, UserCollectionShip, RecommendJob
from mingqiang import scheduler, services, app, db
from datetime import datetime, timedelta


def job_district_list() -> None:
    services.map.map_district_list()
    return

def job_cancel_recommend(house: int|House) -> None:
    with app.app_context():
        if type(house) == int:
            house: House = services.house.get(house)
        if house.reference_id != None:
            user = services.user.get(house.reference_id)
            services.user.cancel_recommend(user, house)

    with app.app_context():
        recommend_job: RecommendJob = RecommendJob.query.filter(RecommendJob.job_id == house.id).first()
        if recommend_job is not None:
            db.session.delete(recommend_job)
            db.session.commit()
    return

def add_cancel_recommend_job(house_id: int, date: datetime|None = None) -> None:
    if date is None:
        date = datetime.now() + timedelta(days=7)
    job = scheduler.get_job(str(house_id))
    if job is not None:
        scheduler.remove_job(str(house_id))
    scheduler.add_job(func=job_cancel_recommend, trigger='date', run_date=date, args=[house_id], id=str(house_id))
    with app.app_context():
        recommend_job: RecommendJob = RecommendJob.query.filter(RecommendJob.job_id == house_id).first()
        if recommend_job is None:
            new_recommend_job = RecommendJob(job_id = house_id, date = date)
            db.session.add(new_recommend_job)
        else:
            recommend_job.date = date
        db.session.commit()
    return

def remove_cancel_recommend_job(house_id: int) -> None:
    job = scheduler.get_job(str(house_id))
    if job is not None:
        scheduler.remove_job(str(house_id))
    job_cancel_recommend(house_id)
    return

def get_jobs():
    with app.app_context():
        jobs: list[RecommendJob] = RecommendJob.query.all()
        for job in jobs:
            if job.date < datetime.now() + timedelta(minutes=1):
                add_cancel_recommend_job(job.job_id, datetime.now() + timedelta(minutes=1))
            else:
                add_cancel_recommend_job(job.job_id, job.date)

# 启动获取地区数据任务
scheduler.add_job(func=job_district_list, trigger="interval", hours=1, id="job_district_list")

# 启动已有的推荐任务
get_jobs()
