# Requirements Document

## Introduction

This feature is a comprehensive therapeutic gamification application that integrates habit-building RPG mechanics, Mandala charts, and multi-scenario novel games. The system is specifically designed to help individuals with ADHD, school refusal issues, and young NEETs (Not in Education, Employment, or Training) rebuild self-efficacy and take steps toward social reintegration through "therapy-grade entertainment."

The core innovation lies in the "Parallel Plot Structure" where story progression is completely synchronized with real-world task completion, creating a seamless experience where players level up both their character "Yu" and themselves simultaneously.

**重要な設計前提：本アプリケーションはスマートフォン・タブレット端末での利用を主目的とし、モバイルファーストの設計思想に基づいて開発されます。**

## Requirements

### Requirement 1: Core Gamification Loop

**User Story:** As a user with ADHD or social reintegration challenges, I want a daily gamified routine that connects my real-world tasks to story progression, so that I can build habits while experiencing meaningful narrative advancement.

#### Acceptance Criteria

1. WHEN the system time reaches 7:00 AM THEN the system SHALL present today's "Heart Crystal" tasks via LINE Bot in a 3x3 Mandala format optimized for mobile screens
2. WHEN a user completes a real-world task THEN the system SHALL allow one-tap reporting to the bot with touch-friendly interface
3. WHEN the system time reaches 21:30 THEN the AI SHALL generate personalized story content based on task completion and mood logs
4. WHEN story choices are presented THEN the system SHALL link them to "real action hooks" that reflect in tomorrow's Mandala
5. WHEN a crystal gauge reaches 100% THEN the system SHALL unlock the next chapter and new abilities with mobile-optimized animations

### Requirement 2: AI-Powered Live Story Engine

**User Story:** As a user seeking personalized therapeutic content, I want an AI system that adapts the story based on my daily performance and emotional state, so that the narrative remains relevant and motivating to my personal journey.

#### Acceptance Criteria

1. WHEN the AI processes daily input THEN the system SHALL generate story content within 3.5 seconds (P95 latency)
2. WHEN generating stories THEN the AI SHALL use GPT-4o with fine-tuned prompts for narrative structure and schema-enforced JSON output
3. WHEN story branches are created THEN the system SHALL maintain a directed acyclic graph (DAG) structure with CHAPTER > NODE > EDGE hierarchy
4. WHEN isolated story nodes are detected THEN the AI SHALL automatically merge them to provide task completion rescue paths
5. WHEN story content is generated THEN the system SHALL ensure therapeutic safety with 98% F1 score for self-harm trigger detection

### Requirement 3: ADHD-Optimized User Experience

**User Story:** As a user with ADHD, I want an interface designed specifically for my cognitive patterns and attention challenges, so that I can use the app effectively without becoming overwhelmed or losing focus.

#### Acceptance Criteria

1. WHEN displaying any interface THEN the system SHALL follow "One-Screen, One-Action" layout with maximum 3 simultaneous choices
2. WHEN a user works continuously for 60 minutes THEN the system SHALL automatically suggest breaks with "mother's concern" narrative if refused twice
3. WHEN displaying text THEN the system SHALL use BIZ UDGothic font with 1.6 line spacing and maximum 4 lines before page break
4. WHEN setting daily tasks THEN the system SHALL limit maximum tasks to 16 per day to respect working memory constraints
5. WHEN providing deadline extensions THEN the system SHALL offer "Daily Buffer" feature allowing 2 free extensions per day

### Requirement 4: Mandala Chart Integration

**User Story:** As a user working on personal development, I want a Mandala chart system that organizes my growth journey into 8 human development attributes, so that I can systematically work on different aspects of my character development.

#### Acceptance Criteria

1. WHEN accessing the Mandala system THEN the API endpoint `/mandala/{uid}/grid` SHALL return a 9x9 JSON array with locked cells marked as "locked"
2. WHEN organizing chapters THEN the system SHALL structure content around 8 attributes: Self-Discipline, Empathy, Resilience, Curiosity, Communication, Creativity, Courage, and Wisdom
3. WHEN a chapter is accessed THEN the system SHALL present 81 "Memory Cells" (quests) in a 9x9 Mandala structure
4. WHEN cells are unlocked THEN the system SHALL synchronize progression between Yu (character) and player levels
5. WHEN player and Yu levels differ by 5 or more THEN the system SHALL trigger "resonance events" with bonus XP

### Requirement 5: Multi-Modal Task Management

**User Story:** As a user with varying daily capabilities and energy levels, I want different types of tasks that accommodate my changing needs and abilities, so that I can maintain progress regardless of my daily condition.

#### Acceptance Criteria

1. WHEN creating tasks THEN the system SHALL support 4 task types: Routine, One-Shot, Skill-Up, and Social
2. WHEN calculating XP THEN the system SHALL use the formula: XP = Σ(difficulty × mood_coefficient × adhd_assist) where mood_coefficient ranges 0.8-1.2 and adhd_assist ranges 1.0-1.3
3. WHEN Pomodoro timer or reminder features are used THEN the system SHALL apply adhd_assist multiplier based on usage frequency
4. WHEN daily mood is logged THEN the system SHALL adjust XP coefficients accordingly (1-5 scale mapped to 0.8-1.2)
5. WHEN tasks are linked to story edges THEN each EDGE SHALL contain either `real_task_id` or `habit_tag` for real-world action tracking

### Requirement 6: Guardian/Support System Portal

**User Story:** As a parent, counselor, or support worker, I want access to a management portal that allows me to monitor and support the user's progress, so that I can provide appropriate guidance while respecting their autonomy.

#### Acceptance Criteria

1. WHEN accessing the guardian portal THEN the system SHALL implement RBAC with three permission levels: "view-only", "task-edit", and "chat-send"
2. WHEN generating reports THEN the system SHALL automatically create weekly PDF reports for guardians
3. WHEN ADHD medical documentation is provided THEN the system SHALL apply 50% discount via Stripe Coupon system
4. WHEN corporations purchase care points THEN the system SHALL allow transferable "Care Points" to be allocated to users
5. WHEN real-time monitoring is enabled THEN the system SHALL optionally track location and heart rate data with explicit consent

### Requirement 7: Therapeutic Safety and Content Moderation

**User Story:** As a user seeking therapeutic support, I want the system to provide psychologically safe content and interventions, so that my mental health is protected while I work on personal development.

#### Acceptance Criteria

1. WHEN generating story content THEN the system SHALL apply OpenAI Moderation plus custom tone filtering
2. WHEN negative thought patterns are detected THEN the AI SHALL generate CBT-based "Story Break" dialogs for cognitive reframing
3. WHEN displaying core values THEN the system SHALL fix value cards in the center of the Mandala with daily reminders (ACT therapy integration)
4. WHEN tracking user state THEN the system SHALL implement a 5-stage state machine: Apathy → Interest → Action → Continuation → Habituation
5. WHEN harmful content risks are identified THEN the system SHALL achieve 98% F1 score for self-harm trigger detection

### Requirement 8: Performance and Scalability

**User Story:** As a user relying on this system for daily support, I want fast, reliable performance that works consistently, so that my therapeutic routine is not disrupted by technical issues.

#### Acceptance Criteria

1. WHEN processing non-AI requests THEN the system SHALL respond within 1.2 seconds (P95 latency)
2. WHEN handling concurrent users THEN the system SHALL support 20,000 simultaneous users and 200,000 monthly active users
3. WHEN system availability is measured THEN the system SHALL maintain 99.95% uptime with multi-region failover
4. WHEN rate limiting is applied THEN the system SHALL enforce 120 requests per minute per IP via Cloud Endpoints
5. WHEN scaling is required THEN the system SHALL automatically scale using Cloud Run infrastructure

### Requirement 9: Mobile-First Responsive Design

**User Story:** As a user primarily using smartphones and tablets, I want a mobile-optimized interface that provides seamless interaction across all device sizes, so that I can engage with the therapeutic content comfortably anywhere.

#### Acceptance Criteria

1. WHEN accessing the app on mobile devices THEN the system SHALL provide responsive design supporting screen sizes from 320px to 1024px width
2. WHEN interacting on touch devices THEN the system SHALL implement touch-friendly UI with minimum 44px touch targets and gesture support
3. WHEN using the app THEN the system SHALL optimize for portrait orientation as primary with landscape support for tablets
4. WHEN loading content THEN the system SHALL implement progressive loading with skeleton screens and maintain <3 second initial load time on 3G networks
5. WHEN displaying the 3x3 Mandala THEN the system SHALL adapt grid layout for mobile screens with swipe navigation and zoom functionality

### Requirement 10: Accessibility and Inclusive Design

**User Story:** As a user with diverse abilities and needs, I want an accessible interface that accommodates various disabilities and learning differences, so that I can fully participate regardless of my specific challenges.

#### Acceptance Criteria

1. WHEN designing interfaces THEN the system SHALL comply with JIS X 8341-3 AAA and WCAG 2.2 AA standards
2. WHEN choosing colors THEN the system SHALL use base color #2E3A59 (calming) and accent #FFC857 (achievement) with color vision diversity support
3. WHEN displaying content THEN the system SHALL reduce screen flashing and provide high contrast options
4. WHEN providing guidance THEN the system SHALL show operation guides in bottom-right modal for all workflows
5. WHEN users need assistance THEN the system SHALL provide 15-minute half-time reminders to address time perception issues

### Requirement 11: RPG経済システムとアイテム管理

**User Story:** As a user seeking deeper engagement, I want a comprehensive RPG economy with coins, equipment, and gacha mechanics, so that I can customize my character and feel rewarded for completing therapeutic tasks.

#### Acceptance Criteria

1. WHEN completing tasks or defeating inner demons THEN the system SHALL award both XP and coins based on difficulty and performance
2. WHEN accessing the shop THEN the system SHALL provide gacha mechanics for equipment, weapons, magic, and consumables with therapeutic themes
3. WHEN obtaining items THEN the system SHALL allow equipment management with stat bonuses that affect task completion rates
4. WHEN coins are earned THEN the system SHALL implement a balanced economy preventing pay-to-win while encouraging engagement
5. WHEN rare items are obtained THEN the system SHALL provide visual feedback and achievement recognition to reinforce positive behavior

### Requirement 12: 職業システムと成長パス

**User Story:** As a user exploring personal identity, I want to choose and develop character classes that reflect my therapeutic journey, so that I can experience meaningful progression aligned with my personal growth.

#### Acceptance Criteria

1. WHEN starting the game THEN the system SHALL offer 6 base classes: Warrior, Hero, Mage, Priest, Sage, and Ninja, each with unique therapeutic focuses
2. WHEN meeting advancement criteria THEN the system SHALL unlock advanced classes based on ability scores, task completion rates, and story choices
3. WHEN selecting a class THEN the system SHALL provide class-specific abilities that enhance different types of therapeutic activities
4. WHEN progressing in class levels THEN the system SHALL unlock new skills that provide gameplay advantages and therapeutic benefits
5. WHEN changing classes THEN the system SHALL allow class switching with appropriate story integration and stat adjustments

### Requirement 13: 内なる魔物バトルシステム

**User Story:** As a user confronting personal challenges, I want to battle symbolic representations of my inner struggles, so that I can process difficult emotions through engaging gameplay mechanics.

#### Acceptance Criteria

1. WHEN encountering negative thought patterns THEN the system SHALL generate "inner demon" battles representing specific therapeutic challenges
2. WHEN engaging in battle THEN the system SHALL use turn-based mechanics where real-world actions (completed tasks, mood improvements) serve as attacks
3. WHEN defeating demons THEN the system SHALL award coins and rare items while providing CBT-based reflection prompts
4. WHEN losing battles THEN the system SHALL offer supportive narratives and alternative strategies rather than punishment
5. WHEN demon types are encountered THEN the system SHALL include therapeutic archetypes: Procrastination Dragon, Anxiety Shadow, Depression Void, Social Fear Goblin

### Requirement 14: ゲーム性強化とエンゲージメント

**User Story:** As a user seeking long-term motivation, I want enhanced game mechanics that maintain interest and provide meaningful choices, so that my therapeutic journey remains engaging over months and years.

#### Acceptance Criteria

1. WHEN playing daily THEN the system SHALL provide seasonal events, limited-time challenges, and community goals
2. WHEN making progress THEN the system SHALL offer branching storylines that reflect real-world therapeutic milestones
3. WHEN interacting with others THEN the system SHALL provide optional cooperative features like guild systems for peer support
4. WHEN achieving milestones THEN the system SHALL unlock cosmetic customization options that reflect personal growth themes
5. WHEN engaging long-term THEN the system SHALL provide prestige systems and legacy features that honor sustained therapeutic work

### Requirement 15: 日次振り返りとグルノートシステム

**User Story:** As a user seeking continuous self-improvement, I want a structured daily reflection system using growth note (グルノート) format, so that I can process my experiences and maintain therapeutic progress through consistent self-reflection.

#### Acceptance Criteria

1. WHEN the system time reaches 22:00 THEN the system SHALL prompt users via LINE Bot for mandatory daily reflection in グルノート format
2. WHEN users access the reflection system THEN the system SHALL provide structured prompts covering the 4 グルノート categories: ①現実世界で困っていること (Current World Problems), ②理想的な世界とは (Ideal World Vision), ③理想的な世界に住むあなたの感情は？ (Emotions in Ideal World), ④明日から何が出来る？ (What Can You Do Starting Tomorrow)
3. WHEN reflection is completed THEN the system SHALL award reflection XP and unlock evening story content
4. WHEN users skip reflection for 2 consecutive days THEN the system SHALL send gentle reminder messages with therapeutic encouragement
5. WHEN reflection data is collected THEN the system SHALL use insights to personalize future story content and task recommendations

### Requirement 16: Data Privacy and Security

**User Story:** As a user sharing personal and sensitive information, I want robust data protection and privacy controls, so that my personal information and therapeutic progress remain secure and confidential.

#### Acceptance Criteria

1. WHEN storing PII data THEN the system SHALL implement region-locked storage with 16-character messaging hashing
2. WHEN implementing security THEN the system SHALL use VPC-SC, IAM Conditions, Cloud Armor WAF, and Secret Manager KMS
3. WHEN handling authentication THEN the guardian portal SHALL support SAML and Magic Link authentication via Supabase Auth
4. WHEN processing payments THEN the system SHALL use Stripe with ethical monetization focused on season passes and cosmetic items
5. WHEN serving advertisements THEN the system SHALL limit to offline learning content only, filtering out violence and gambling ads