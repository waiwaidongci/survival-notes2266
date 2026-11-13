"""Right-censored Kaplan-Meier with delayed entry and pointwise exponential Greenwood (log-log) interval."""
import math
from statistics import NormalDist

def normalize(observation):
    if len(observation)==2:return 0.,observation[0],observation[1]
    return observation[0],observation[1],observation[2]

def validate_observations(observations):
    if len(observations)<2:raise ValueError("每组至少需要2个独立试件")
    for observation in observations:
        entry,duration,event=normalize(observation)
        if type(entry) not in (int,float) or not math.isfinite(entry) or entry<0 or entry>1e6:raise ValueError("入组时累计工作时长必须是[0,1000000]内的有限小时数")
        if type(duration) not in (int,float) or abs(duration)>1e6 or not math.isfinite(duration) or duration<=0:raise ValueError("随访时长必须是(0,1000000]内的有限小时数")
        if entry>duration:raise ValueError("入组时累计工作时长晚于终态时长，记录被拒绝")
        if type(event) is not bool:raise ValueError("事件标记必须是布尔值，不能把删失当失效")

def kaplan_meier(observations,confidence=.95,risk_times=(400.,800.,1200.)):
    validate_observations(observations)
    if not math.isfinite(confidence) or not .8<=confidence<=.99:raise ValueError("置信水平必须位于[0.8,0.99]")
    observations=[normalize(o) for o in observations]
    times=sorted(set(duration for entry,duration,event in observations));z=NormalDist().inv_cdf((1+confidence)/2)
    survival=1.;greenwood=0.;median=None
    curve=[{"time":0.,"at_risk":sum(entry<=0<=duration for entry,duration,event in observations),"events":0,"censored":0,"survival":1.,"lower":1.,"upper":1.,"greenwood_sum":0.}]
    for time in times:
        at_risk=sum(entry<=time<=duration for entry,duration,event in observations)
        events=sum(duration==time and event for entry,duration,event in observations)
        censored=sum(duration==time and not event for entry,duration,event in observations)
        if events:
            survival*=1-events/at_risk
            if at_risk>events:greenwood+=events/(at_risk*(at_risk-events))
        if survival<=0:lower=upper=0.
        elif survival>=1:lower=upper=1.
        else:
            transformed=math.log(-math.log(survival));se=math.sqrt(greenwood)/abs(math.log(survival))
            lower=math.exp(-math.exp(transformed+z*se));upper=math.exp(-math.exp(transformed-z*se))
        if median is None and survival<=.5:median=time
        curve.append({"time":time,"at_risk":at_risk,"events":events,"censored":censored,"survival":survival,"lower":lower,"upper":upper,"greenwood_sum":greenwood})
    risk=[{"time":time,"at_risk":sum(entry<=time<=duration for entry,duration,event in observations)} for time in risk_times]
    return {"n":len(observations),"delayed":sum(entry>0 for entry,duration,event in observations),"max_entry":max(entry for entry,duration,event in observations),"events":sum(event for entry,duration,event in observations),"censored":sum(not event for entry,duration,event in observations),"curve":curve,"risk_table":risk,"median":median,"median_status":"estimated" if median is not None else "not_reached","last_observed":max(times),"confidence":confidence,"interval_method":"Greenwood log-log pointwise"}
