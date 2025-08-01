# Core Game Engine Service

The Core Game Engine is the heart of the therapeutic gamification system, managing XP calculation, level progression, chapter advancement, and the resonance event system that synchronizes player and character "Yu" development.

## Features

### XP Calculation System
- **Formula**: `XP = Σ(difficulty × mood_coefficient × adhd_assist)`
- **Mood Coefficient**: 0.8-1.2 based on daily mood logs (1-5 scale)
- **ADHD Assist Multiplier**: 1.0-1.3 based on support tool usage
- **Difficulty Scaling**: 1-5 task difficulty maps to 10-50 base XP

### Level Progression
- **Exponential Growth**: Each level requires progressively more XP
- **Dual Character System**: Player and Yu level independently
- **Yu Modifier**: Yu gains XP 10% slower for balance
- **Max Level**: 100 levels with meaningful progression

### Chapter System
- **8 Human Development Attributes**:
  1. Self-Discipline
  2. Empathy
  3. Resilience
  4. Curiosity
  5. Communication
  6. Creativity
  7. Courage
  8. Wisdom

### Crystal Gauge System
- **Progress Tracking**: Each chapter has a 0-100% completion gauge
- **XP Contribution**: Every 10 XP adds 1% to current chapter's crystal
- **Chapter Unlock**: 100% completion unlocks next chapter

### Resonance Events
- **Trigger Condition**: Player and Yu level difference ≥ 5
- **Bonus XP**: 500 XP awarded during resonance
- **Cooldown**: 24-hour cooldown between resonance events
- **Therapeutic Purpose**: Encourages balanced character development

## API Endpoints

### Game State Management
```http
GET /game-state/{uid}
```
Retrieve user's current game state including levels, XP, and chapter progress.

```http
POST /award-xp/{uid}?xp_amount={amount}&source={source}
```
Award XP to user and handle level progression automatically.

### Task Completion
```http
POST /complete-task/{uid}/{task_id}
```
Complete a task and award appropriate XP based on difficulty, mood, and ADHD support.

### Level Information
```http
GET /level-info/{level}
```
Get XP requirements and progression information for a specific level.

### Chapter Progress
```http
GET /chapter-progress/{uid}
```
Get detailed progress through all 8 chapters including unlock status.

## ADHD Support Features

### Multiplier Calculation
- **Pomodoro Timer**: +0.1 multiplier when enabled
- **Reminder System**: +0.1 multiplier when active
- **Break Detection**: +0.1 multiplier when used
- **Maximum Bonus**: Capped at 1.3x (30% bonus)

### Therapeutic Integration
- Encourages use of evidence-based ADHD management tools
- Rewards consistent engagement with support systems
- Balances challenge with accessibility

## Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**:
   ```bash
   export GOOGLE_CLOUD_PROJECT="your-project-id"
   export FIRESTORE_EMULATOR_HOST="localhost:8080"  # For local development
   ```

3. **Run Service**:
   ```bash
   python run_service.py
   ```

## Testing

### Unit Tests
```bash
pytest test_core_game.py -v
```

### Implementation Validation
```bash
python validate_implementation.py
```

### Test Coverage
- XP calculation with various coefficients
- Level progression consistency
- Chapter advancement logic
- Resonance event triggers
- ADHD support multipliers
- Game state management

## Configuration

### Environment Variables
- `HOST`: Service host (default: 0.0.0.0)
- `PORT`: Service port (default: 8002)
- `DEBUG`: Enable debug mode (default: false)
- `GOOGLE_CLOUD_PROJECT`: GCP project ID
- `FIRESTORE_EMULATOR_HOST`: Firestore emulator (development only)

### Game Balance Constants
```python
BASE_XP_PER_LEVEL = 100           # Base XP for level 2
LEVEL_MULTIPLIER = 1.5            # Exponential growth factor
MAX_LEVEL = 100                   # Maximum achievable level
CRYSTAL_COMPLETION_THRESHOLD = 100 # Chapter completion requirement
RESONANCE_LEVEL_DIFF_THRESHOLD = 5 # Level difference for resonance
RESONANCE_BONUS_XP = 500          # Bonus XP during resonance
```

## Database Schema

### Game States Collection
```json
{
  "uid": "user_id",
  "player_level": 5,
  "yu_level": 4,
  "current_chapter": "empathy",
  "crystal_gauges": {
    "self_discipline": 100,
    "empathy": 75,
    "resilience": 0,
    // ... other chapters
  },
  "total_xp": 850,
  "last_resonance_event": "2024-01-15T10:30:00Z"
}
```

## Therapeutic Design Principles

### Evidence-Based Mechanics
- **Progressive Disclosure**: Chapters unlock sequentially
- **Mastery Learning**: 100% completion required before advancement
- **Positive Reinforcement**: XP rewards for all completed tasks
- **Self-Efficacy Building**: Dual character progression shows growth

### ADHD Accommodations
- **Executive Function Support**: Automated XP calculation
- **Working Memory Protection**: Simple, consistent formulas
- **Attention Regulation**: Bonus rewards for using focus tools
- **Time Perception**: Level progression provides concrete milestones

### Therapeutic Safety
- **No Punishment**: Failed tasks don't reduce XP or levels
- **Flexible Pacing**: No time pressure for chapter completion
- **Balanced Challenge**: Difficulty scaling prevents overwhelming users
- **Positive Feedback Loop**: Success breeds more success

## Performance Considerations

### Optimization Strategies
- **Cached Calculations**: Level-XP mappings cached in memory
- **Batch Operations**: Multiple XP awards processed together
- **Efficient Queries**: Indexed Firestore queries for game states
- **Async Processing**: Non-blocking database operations

### Scalability
- **Stateless Design**: No server-side session storage
- **Horizontal Scaling**: Multiple service instances supported
- **Database Optimization**: Proper indexing for user queries
- **Caching Layer**: Redis integration for frequently accessed data

## Monitoring and Analytics

### Key Metrics
- **XP Distribution**: Track XP earning patterns
- **Level Progression**: Monitor advancement rates
- **Chapter Completion**: Measure engagement across attributes
- **Resonance Events**: Track dual character balance
- **ADHD Tool Usage**: Measure support feature adoption

### Health Checks
- Service availability monitoring
- Database connection health
- XP calculation accuracy
- Level progression consistency

## Future Enhancements

### Planned Features
- **Seasonal Events**: Special XP bonuses during holidays
- **Achievement System**: Milestone rewards for progression
- **Social Features**: Friend comparisons and group challenges
- **Advanced Analytics**: Machine learning for personalized XP curves

### Therapeutic Expansions
- **CBT Integration**: Cognitive behavioral therapy mechanics
- **Mindfulness Rewards**: Meditation and reflection bonuses
- **Social Skills**: Multiplayer cooperative challenges
- **Real-World Integration**: GPS and activity tracking bonuses