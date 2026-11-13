from fastapi import HTTPException
from ..models import TestCohort,Specimen,FollowupEvent
from ..utils.serialize import record

def specimen_rows(db,cid):
    if not db.get(TestCohort,cid):raise HTTPException(404,"工艺批次不存在")
    rows=db.query(Specimen,FollowupEvent).join(FollowupEvent).filter(Specimen.cohort_id==cid).order_by(Specimen.code).all()
    return [dict(record(s),followup_id=e.id,entry_hours=e.entry_hours if e.entry_hours is not None else 0.,duration_hours=e.duration_hours,event_observed=e.event_observed,note=e.note) for s,e in rows]
