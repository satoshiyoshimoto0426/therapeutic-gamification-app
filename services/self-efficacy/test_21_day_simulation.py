"""
21?

?21?
"""

import asyncio
from datetime import datetime, timedelta
from main import efficacy_engine, EfficacyUpdateRequest, EfficacyGauge, EfficacyLevel

async def test_21_day_habit_formation():
    """21?"""
    print("21?")
    print("=" * 50)
    
    user_id = "habit_formation_user"
    therapeutic_focus = "Self-Discipline"
    
    # ?
    base_date = datetime(2024, 1, 1)
    
    # ?
    gauge = EfficacyGauge(
        user_id=user_id,
        therapeutic_focus=therapeutic_focus,
        current_level=EfficacyLevel.NOVICE,
        current_percentage=0.0,
        consecutive_days=0,
        total_days_active=0,
        last_activity_date=base_date - timedelta(days=1),
        milestone_reached=[],
        passive_skills=[],
        efficacy_history=[]
    )
    
    # ?
    if not hasattr(efficacy_engine, '_test_gauges'):
        efficacy_engine._test_gauges = {}
    efficacy_engine._test_gauges[f"{user_id}_{therapeutic_focus}"] = gauge
    
    # 21?
    milestone_days = [3, 7, 14, 21]
    
    for day in range(1, 22):
        # ?
        current_date = base_date + timedelta(days=day-1)
        gauge.last_activity_date = current_date - timedelta(days=1)
        
        # タスク
        request = EfficacyUpdateRequest(
            user_id=user_id,
            therapeutic_focus=therapeutic_focus,
            task_completed=True,
            task_difficulty=2 + (day % 3),
            mood_rating=3 + (day % 3),
            reflection_quality=3 + (day % 2)
        )
        
        # ?
        # ?
        gauge.consecutive_days = day
        gauge.total_days_active = day
        gauge.last_activity_date = current_date
        
        # ?
        efficacy_increase = efficacy_engine._calculate_efficacy_increase(request, gauge)
        gauge.current_percentage = min(100.0, gauge.current_percentage + efficacy_increase)
        gauge.current_level = efficacy_engine._calculate_efficacy_level(gauge.current_percentage)
        
        # ?
        gauge.efficacy_history.append({
            "date": current_date.date().isoformat(),
            "percentage": gauge.current_percentage,
            "consecutive_days": gauge.consecutive_days,
            "efficacy_increase": efficacy_increase,
            "task_completed": request.task_completed,
            "mood_rating": request.mood_rating
        })
        
        # ?
        milestone_rewards = await efficacy_engine._check_milestones(gauge)
        
        # ?
        newly_unlocked_skills = await efficacy_engine._check_passive_skill_unlocks(gauge)
        
        # ?
        if day in milestone_days:
            print(f"\n{day}?:")
            print(f"  ? ?: {gauge.consecutive_days}?")
            print(f"  ? ?: {gauge.current_level.value}")
            print(f"  ? ?: {gauge.current_percentage:.1f}%")
            print(f"  ? ?: {len(milestone_rewards)}?")
            print(f"  ? ?: {len(newly_unlocked_skills)}?")
            
            if milestone_rewards:
                for reward in milestone_rewards:
                    print(f"    - ?: {reward['milestone'].title}")
                    print(f"      {reward['milestone'].description}")
            
            if newly_unlocked_skills:
                for skill in newly_unlocked_skills:
                    print(f"    - ?: {skill.name}")
                    print(f"      {skill.description}")
            
            # 21?
            if day == 21:
                print(f"  ? ?:")
                print(f"    - ?: {len(gauge.passive_skills)}")
                print(f"    - ?: {gauge.milestone_reached}")
                
                # 21?
                expected_skills = [skill for skill in efficacy_engine.passive_skills_pool 
                                 if skill.unlock_requirement <= 21 and skill.therapeutic_focus == therapeutic_focus]
                print(f"    - ?: {len(expected_skills)}")
                
                # お
                celebration = efficacy_engine._generate_celebration_message(gauge, milestone_rewards)
                print(f"  ? お: {celebration}")
    
    print("\n" + "=" * 50)
    print("? 21?")
    
    # ?
    print(f"\n?:")
    print(f"- ?: {gauge.consecutive_days}?")
    print(f"- ?: {gauge.current_level.value}")
    print(f"- ?: {gauge.current_percentage:.1f}%")
    print(f"- ?: {len(gauge.milestone_reached)}?")
    print(f"- ?: {len(gauge.passive_skills)}?")
    
    # ?
    print(f"\n?:")
    print(f"- 21?: {'?' if gauge.consecutive_days >= 21 else '?'}")
    print(f"- ?: {'?' if 21 in gauge.milestone_reached else '?'}")
    print(f"- ?: {'?' if len(gauge.passive_skills) > 0 else '?'}")
    print(f"- 治療: {'?' if gauge.current_percentage > 50 else '?'}")
    
    return gauge

async def test_multiple_therapeutic_focuses():
    """?"""
    print("\n" + "=" * 50)
    print("?")
    
    user_id = "multi_focus_user"
    focuses = ["Self-Discipline", "Empathy", "Resilience"]
    
    for focus in focuses:
        print(f"\n{focus} の7?:")
        
        # ?7?
        gauge = EfficacyGauge(
            user_id=user_id,
            therapeutic_focus=focus,
            current_level=EfficacyLevel.NOVICE,
            current_percentage=0.0,
            consecutive_days=0,
            total_days_active=0,
            last_activity_date=datetime.now() - timedelta(days=1),
            milestone_reached=[],
            passive_skills=[],
            efficacy_history=[]
        )
        
        # ?
        efficacy_engine._test_gauges[f"{user_id}_{focus}"] = gauge
        
        for day in range(1, 8):
            gauge.consecutive_days = day
            gauge.total_days_active = day
            gauge.current_percentage += 3.0  # ?
            gauge.current_level = efficacy_engine._calculate_efficacy_level(gauge.current_percentage)
            
            if day == 7:
                milestone_rewards = await efficacy_engine._check_milestones(gauge)
                skills = await efficacy_engine._check_passive_skill_unlocks(gauge)
                
                print(f"  ? 7?: {gauge.current_percentage:.1f}%")
                print(f"  ? ?: {len(milestone_rewards)}?")
                print(f"  ? ストーリー: {len(skills)}?")
    
    # ?
    dashboard = await efficacy_engine.get_efficacy_dashboard(user_id)
    print(f"\n?:")
    print(f"  ? ?: {dashboard['overall_efficacy_level'].value}")
    print(f"  ? ?: {dashboard['average_efficacy_percentage']:.1f}%")
    print(f"  ? ?: {dashboard['max_consecutive_days']}?")
    print(f"  ? ?: {dashboard['total_passive_skills']}?")

async def main():
    """メイン"""
    # 21?
    await test_21_day_habit_formation()
    
    # ?
    await test_multiple_therapeutic_focuses()
    
    print("\n" + "=" * 50)
    print("? Self-Efficacy Gauge ?")
    print("\n?:")
    print("- 21? ?")
    print("- ? ?")
    print("- 治療 ?")
    print("- 8つ ?")
    print("- ? ?")

if __name__ == "__main__":
    asyncio.run(main())