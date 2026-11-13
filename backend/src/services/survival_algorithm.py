from .km_algorithm import kaplan_meier
from .logrank_algorithm import logrank
from ..utils.fingerprint import fingerprint

METHOD="km-loglog-logrank-v2-delayed-entry"

def analyze_survival(cohort_a,cohort_b,rows_a,rows_b,confidence=.95):
    if cohort_a.id==cohort_b.id:raise ValueError("必须选择两批不同工艺")
    groups=[];inputs=[]
    for cohort,rows in [(cohort_a,rows_a),(cohort_b,rows_b)]:
        rows=sorted(({**r,"entry_hours":r.get("entry_hours") or 0.} for r in rows),key=lambda x:x['code'])
        if len({r['code'] for r in rows})!=len(rows):raise ValueError("同组试件编号重复")
        observations=[(r['entry_hours'],r['duration_hours'],r['event_observed']) for r in rows]
        info={"id":cohort.id,"code":cohort.code,"name":cohort.name,"process":cohort.process}
        groups.append({"cohort":info,**kaplan_meier(observations,confidence)})
        inputs.append({"cohort":info,"rows":rows})
    comparison=logrank([(r['entry_hours'],r['duration_hours'],r['event_observed']) for r in inputs[0]["rows"]],[(r['entry_hours'],r['duration_hours'],r['event_observed']) for r in inputs[1]["rows"]])
    return {"groups":groups,"logrank":comparison,"confidence":confidence,"time_unit":"小时","input_hash":fingerprint({"method":METHOD,"groups":inputs,"confidence":confidence,"risk_times":[400,800,1200],"time_unit":"hours"}),"method_version":METHOD,"interpretation":"两批耐久分布存在统计差异；结合删失、延迟入组与工艺条件审阅" if comparison['estimable'] and comparison['p_value']<.05 else "尚无足够差异证据；不能据此认定两批等效" if comparison['estimable'] else "事件信息不足，log-rank不可估计","assumptions":"独立试件、非信息性右删失；支持延迟入组，横轴为累计工作时长，试件自入组时长起才计入风险集，同一时点先入组再处理事件与删失。区间是逐点区间，不是同时置信带；比较为关联研究，不自动决定维护周期。"}
