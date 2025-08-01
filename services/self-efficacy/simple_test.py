"""
Self-Efficacy Gauge Service ?

?
"""

import asyncio
from main import efficacy_engine, EfficacyUpdateRequest

async def test_basic_functionality():
    """基本"""
    print("Self-Efficacy Gauge Service ?")
    print("=" * 50)
    
    user_id = "simple_test_user"
    therapeutic_focus = "Self-Discipline"
    
    # 1. ?
    print("1. ?")
    request = EfficacyUpdateRequest(
        user_id=user_id,
        therapeutic_focus=therapeutic_focus,
        task_completed=True,
        task_difficulty=3,
        mood_rating=4,
        reflection_quality=4
    )
    
    result = await efficacy_engine.update_efficacy_gauge(request)
    print(f"   ? ?: {result['efficacy_increase']:.2f}% ?")
    print(f"   ? ?: {result['gauge'].consecutive_days}?")
    
    # 2. 7?
    print("\n2. 7?")
    for day in range(2, 8):
        request.task_difficulty = 2 + (day % 3)
        request.mood_rating = 3 + (day % 3)
        
        result = await efficacy_engine.update_efficacy_gauge(request)
        
        if day == 7:
            print(f"   ? 7?: {result['gauge'].consecutive_days}?")
            print(f"   ? ?: {result['gauge'].current_level.value}")
            print(f"   ? ?: {len(result['milestone_rewards'])}?")
            if result['milestone_rewards']:
                print(f"   ? ?: {result['milestone_rewards'][0]['milestone'].title}")
    
    # 3. 21?
    print("\n3. 21?")
    for day in range(8, 22):
        request.task_difficulty = 2 + (day % 3)
        request.mood_rating = 3 + (day % 3)
        
        result = await efficacy_engine.update_efficacy_gauge(request)
        
        if day == 14:
            print(f"   ? 14?: ? {len(result['milestone_rewards'])}?")
        elif day == 21:
            print(f"   ? 21?: {result['gauge'].consecutive_days}?")
            print(f"   ? ?: {result['gauge'].current_level.value}")
            print(f"   ? ?: {result['gauge'].current_percentage:.1f}%")
            print(f"   ? ?: {len(result['milestone_rewards'])}?")
            print(f"   ? ?: {len(result['newly_unlocked_skills'])}?")
            
            if result['milestone_rewards']:
                for reward in result['milestone_rewards']:
                    print(f"       - {reward['milestone'].title}: {reward['milestone'].description}")
            
            if result['newly_unlocked_skills']:
                for skill in result['newly_unlocked_skills']:
                    print(f"       - {skill.name}: {skill.description}")
            
            print(f"   ? お: {result['celebration_message']}")
    
    # 4. ?
    print("\n4. ?")
    dashboard = await efficacy_engine.get_efficacy_dashboard(user_id)
    
    print(f"   ? ?: {dashboard['overall_efficacy_level'].value}")
    print(f"   ? ?: {dashboard['average_efficacy_percentage']:.1f}%")
    print(f"   ? ?: {dashboard['max_consecutive_days']}?")
    print(f"   ? ?: {dashboard['total_passive_skills']}?")
    print(f"   ? ?: {dashboard['efficacy_trend']}")
    print(f"   ? モデル: {dashboard['motivational_message']}")
    
    # 5. ?
    print("\n5. ?")
    milestones = efficacy_engine.milestones
    print(f"   ? ?: {len(milestones)}?")
    
    for milestone in milestones[:5]:  # ?5つ
        print(f"       - {milestone.day}?: {milestone.title}")
    
    # 6. ?
    print("\n6. ?")
    skills = efficacy_engine.passive_skills_pool
    print(f"   ? ?: {len(skills)}?")
    
    for skill in skills[:5]:  # ?5つ
        print(f"       - {skill.name} ({skill.unlock_requirement}?): {skill.description}")
    
    print("\n" + "=" * 50)
    print("? Self-Efficacy Gauge Service ?")
    print("\n?:")
    print("- 21? ?")
    print("- ? ?")
    print("- 治療 ?")
    print("- ? ?")
    print("- ? ?")

if __name__ == "__main__":
    asyncio.run(test_basic_functionality())