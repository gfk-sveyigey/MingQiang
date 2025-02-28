from mingqiang.model import User, Group, House, UserCollectionShip, RecommendJob
from mingqiang import services, app, db
from datetime import datetime, timedelta


def get_remaining(house: int|House) -> str:
    if type(house) == int:
        house: House = services.house.get(house)

    if house is None:
        return ""
    recommend_job: RecommendJob = RecommendJob.query.filter(RecommendJob.job_id == house.id).first()
    if recommend_job is None:
        return ""
    remaining: timedelta = recommend_job.date - datetime.now()
    remaining = f"{remaining.days}天{remaining.seconds//3600}时{(remaining.seconds%3600)//60}分"
    return remaining