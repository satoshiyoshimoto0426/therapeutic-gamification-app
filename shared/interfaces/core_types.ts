/**
 * Core TypeScript interfaces for the therapeutic gamification app
 * These interfaces define the core entities and data structures used across all services
 */

// Core Enums
export enum ChapterType {
  SELF_DISCIPLINE = "self_discipline",
  EMPATHY = "empathy",
  RESILIENCE = "resilience",
  CURIOSITY = "curiosity",
  COMMUNICATION = "communication",
  CREATIVITY = "creativity",
  COURAGE = "courage",
  WISDOM = "wisdom"
}

export enum CrystalAttribute {
  SELF_DISCIPLINE = "self_discipline",  // 自律
  EMPATHY = "empathy",                  // 共感
  RESILIENCE = "resilience",            // 回復力
  CURIOSITY = "curiosity",              // 好奇心
  COMMUNICATION = "communication",      // コミュニケーション
  CREATIVITY = "creativity",            // 創造性
  COURAGE = "courage",                  // 勇気
  WISDOM = "wisdom"                     // 知恵
}

export enum CrystalGrowthEvent {
  TASK_COMPLETION = "task_completion",
  STORY_CHOICE = "story_choice",
  MOOD_IMPROVEMENT = "mood_improvement",
  REFLECTION_ENTRY = "reflection_entry",
  SOCIAL_INTERACTION = "social_interaction",
  CREATIVE_ACTIVITY = "creative_activity",
  CHALLENGE_OVERCOME = "challenge_overcome",
  WISDOM_GAINED = "wisdom_gained"
}

export enum TaskType {
  ROUTINE = "routine",
  ONE_SHOT = "one_shot",
  SKILL_UP = "skill_up",
  SOCIAL = "social"
}

export enum TaskStatus {
  PENDING = "pending",
  IN_PROGRESS = "in_progress",
  COMPLETED = "completed",
  OVERDUE = "overdue"
}

export enum CellStatus {
  LOCKED = "locked",
  AVAILABLE = "available",
  IN_PROGRESS = "in_progress",
  COMPLETED = "completed"
}

export enum GuardianPermission {
  VIEW_ONLY = "view_only",
  TASK_EDIT = "task_edit",
  CHAT_SEND = "chat_send"
}

export enum NodeType {
  OPENING = "opening",
  CHALLENGE = "challenge",
  CHOICE = "choice",
  RESOLUTION = "resolution",
  REFLECTION = "reflection",
  COMPANION_INTRO = "companion_intro",
  MONSTER_ENCOUNTER = "monster_encounter",
  ENDING = "ending"
}

export enum UnlockConditionType {
  TASK_COMPLETION = "task_completion",
  MOOD_THRESHOLD = "mood_threshold",
  TIME_BASED = "time_based",
  LEVEL_REQUIREMENT = "level_requirement",
  COMPANION_RELATIONSHIP = "companion_relationship",
  ACHIEVEMENT_UNLOCK = "achievement_unlock",
  DIARY_COMPLETION = "diary_completion"
}

export enum ItemRarity {
  COMMON = "common",
  UNCOMMON = "uncommon",
  RARE = "rare",
  EPIC = "epic",
  LEGENDARY = "legendary"
}

export enum ItemType {
  WEAPON = "weapon",
  ARMOR = "armor",
  ACCESSORY = "accessory",
  CONSUMABLE = "consumable",
  MAGIC = "magic"
}

export enum JobClass {
  WARRIOR = "warrior",
  HERO = "hero",
  MAGE = "mage",
  PRIEST = "priest",
  SAGE = "sage",
  NINJA = "ninja",
  // Advanced classes
  PALADIN = "paladin",
  ARCHMAGE = "archmage",
  SHADOW_MASTER = "shadow_master"
}

export enum DemonType {
  PROCRASTINATION_DRAGON = "procrastination_dragon",
  ANXIETY_SHADOW = "anxiety_shadow",
  DEPRESSION_VOID = "depression_void",
  SOCIAL_FEAR_GOBLIN = "social_fear_goblin"
}

// Core Data Models
export interface UserProfile {
  uid: string;
  email: string;
  display_name: string;
  player_level: number;
  yu_level: number;
  total_xp: number;
  crystal_gauges: Record<string, number>; // 8 attributes: 0-100 percentage
  current_chapter: string;
  daily_task_limit: number; // ADHD consideration
  care_points: number;
  guardian_permissions: string[];
  adhd_profile: Record<string, any>;
  therapeutic_goals: string[];
  created_at: Date;
  last_active: Date;
}

export interface StoryState {
  uid: string;
  current_chapter: string;
  current_node: string;
  available_edges: string[];
  story_history: Record<string, any>[];
  last_generation_time?: Date;
  unlocked_chapters: string[];
  unlocked_nodes: string[];
  completed_nodes: string[];
  choice_history: Record<string, any>[];
  companion_relationships: Record<string, number>;
  ending_scores: Record<string, number>;
  story_flags: Record<string, string | number | boolean>;
  last_updated: Date;
}

export interface TaskRecord {
  task_id: string;
  uid: string;
  task_type: TaskType;
  title: string;
  description: string;
  difficulty: number; // 1-5 scale
  status: TaskStatus;
  due_date?: Date;
  completion_time?: Date;
  xp_earned: number;
  mood_at_completion?: number; // 1-5 scale
  linked_story_edge?: string;
  habit_tag?: string;
  adhd_support: Record<string, any>; // Pomodoro settings, reminders
  created_at: Date;
}

export interface GameState {
  player_level: number;
  yu_level: number;
  current_chapter: ChapterType;
  crystal_gauges: Record<ChapterType, number>; // 0-100 percentage
  total_xp: number;
  last_resonance_event?: Date;
}

export interface XPCalculation {
  base_xp: number;
  difficulty_multiplier: number;
  mood_coefficient: number; // 0.8 - 1.2
  adhd_assist_multiplier: number; // 1.0 - 1.3
  final_xp: number;
}

export interface User {
  uid: string;
  email: string;
  display_name: string;
  player_level: number;
  yu_level: number;
  total_xp: number;
  created_at: Date;
  last_active: Date;
  adhd_profile: Record<string, any>;
  therapeutic_goals: string[];
  game_state: GameState;
}

export interface MandalaCell {
  id: string;
  position: [number, number]; // [row, col]
  status: CellStatus;
  task_id?: string;
  unlock_conditions: string[];
  xp_reward: number;
  chapter_type: ChapterType;
}

export interface MandalaGrid {
  chapter_type: ChapterType;
  cells: MandalaCell[][]; // 9x9 grid
  center_value: string; // Core value for this chapter
  completion_percentage: number;
}

export interface Task {
  task_id: string;
  uid: string;
  task_type: TaskType;
  title: string;
  description: string;
  difficulty: number; // 1-5 scale
  status: TaskStatus;
  due_date?: Date;
  mandala_cell_id?: string;
  adhd_support: Record<string, any>; // Pomodoro settings, reminders, etc.
  created_at: Date;
  completed_at?: Date;
}

export interface MoodLog {
  uid: string;
  log_date: Date;
  mood_score: number; // 1-5 scale
  notes?: string;
  context_tags: string[];
  calculated_coefficient: number; // 0.8-1.2 for XP calculation
}

export interface UnlockCondition {
  condition_type: UnlockConditionType;
  parameters: Record<string, string | number>;
  required: boolean;
}

export interface StoryChapter {
  chapter_id: string;
  chapter_type: ChapterType;
  title: string;
  description: string;
  unlock_conditions: UnlockCondition[];
  estimated_completion_time: number; // minutes
  therapeutic_focus: string[];
  created_at: Date;
}

export interface StoryNode {
  node_id: string;
  chapter_id: string; // Links to parent chapter
  node_type: NodeType;
  title: string;
  content: string;
  estimated_read_time: number; // minutes
  therapeutic_tags: string[];
  unlock_conditions: UnlockCondition[];
  companion_effects: Record<string, number>;
  mood_effects: Record<string, number>;
  ending_flags: Record<string, string | number | boolean>;
  created_at: Date;
}

export interface StoryEdge {
  edge_id: string;
  from_node_id: string;
  to_node_id: string;
  choice_text: string;
  real_task_id?: string; // Links to real-world task
  habit_tag?: string; // Links to habit tracking
  probability: number;
  therapeutic_weight: number;
  companion_requirements: Record<string, number>;
  achievement_rewards: string[];
  ending_influence: Record<string, number>;
}

export interface UserStoryState {
  uid: string;
  current_chapter_id: string;
  current_node_id: string;
  unlocked_chapters: string[];
  unlocked_nodes: string[];
  completed_nodes: string[];
  choice_history: Array<Record<string, string | Date>>;
  companion_relationships: Record<string, number>;
  ending_scores: Record<string, number>;
  story_flags: Record<string, string | number | boolean>;
  last_updated: Date;
}

export interface GuardianLink {
  guardian_id: string;
  user_id: string;
  permission_level: GuardianPermission;
  created_at: Date;
  approved_by_user: boolean;
  care_points: number;
}

// RPG System Types
export interface RPGItem {
  item_id: string;
  name: string;
  description: string;
  item_type: ItemType;
  rarity: ItemRarity;
  stat_bonuses: Record<string, number>; // focus, resilience, motivation, etc.
  therapeutic_effect?: string;
  flavor_text: string;
  icon_url?: string;
}

export interface UserInventory {
  uid: string;
  items: RPGItem[];
  equipped_items: Record<string, string | null>; // slot -> item_id
  total_coins: number;
  last_updated: Date;
}

export interface JobProgression {
  uid: string;
  current_job: JobClass;
  job_levels: Record<JobClass, number>;
  unlocked_jobs: JobClass[];
  job_skills: Record<string, number>; // skill_name -> level
  stat_bonuses: Record<string, number>; // from job progression
}

export interface InnerDemon {
  demon_id: string;
  demon_type: DemonType;
  name: string;
  hp: number;
  max_hp: number;
  weaknesses: string[]; // action types that damage this demon
  rewards: Record<string, number | string[]>; // coins, items
  therapeutic_message: string;
  appearance_conditions: string[];
}

export interface BattleState {
  uid: string;
  demon: InnerDemon;
  user_recent_actions: string[];
  battle_log: string[];
  is_active: boolean;
  started_at: Date;
}

// Crystal System Types
export interface CrystalState {
  attribute: CrystalAttribute;
  current_value: number; // 0-100 percentage
  growth_rate: number; // Multiplier for growth events
  last_growth_event?: Date;
  milestone_rewards: string[]; // Unlocked rewards at milestones
  therapeutic_insights: string[]; // Generated insights for this attribute
}

export interface CrystalGrowthRecord {
  uid: string;
  attribute: CrystalAttribute;
  event_type: CrystalGrowthEvent;
  growth_amount: number; // Points added to crystal
  trigger_context: Record<string, any>; // Context that triggered growth
  therapeutic_message?: string;
  created_at: Date;
}

export interface CrystalMilestone {
  attribute: CrystalAttribute;
  threshold: number; // 0-100 percentage
  title: string;
  description: string;
  rewards: string[]; // Item IDs, abilities, etc.
  therapeutic_benefit: string;
  unlock_content: string[]; // Story nodes, features, etc.
}

export interface UserCrystalSystem {
  uid: string;
  crystals: Record<CrystalAttribute, CrystalState>;
  total_growth_events: number;
  resonance_level: number; // Overall harmony between crystals
  last_resonance_check?: Date;
  active_synergies: string[]; // Active crystal combinations
  growth_history: CrystalGrowthRecord[];
}

export interface CrystalSynergy {
  synergy_id: string;
  name: string;
  required_attributes: CrystalAttribute[];
  min_levels: Record<CrystalAttribute, number>; // Minimum levels required
  effect_description: string;
  stat_bonuses: Record<string, number>;
  therapeutic_benefit: string;
  story_unlock?: string;
}

// Growth Note (グルノート) System Types
export interface GrowthNoteEntry {
  uid: string;
  entry_date: Date;
  current_problems: string; // ①現実世界で困っていること
  ideal_world: string; // ②理想的な世界とは
  ideal_emotions: string; // ③理想的な世界に住むあなたの感情は？
  tomorrow_actions: string; // ④明日から何が出来る？
  xp_earned: number;
  emotional_tone?: string;
  key_themes: string[];
  crystal_growth_triggered: CrystalAttribute[]; // Which crystals grew from this entry
  created_at: Date;
}

export interface ReflectionStreak {
  uid: string;
  current_streak: number;
  longest_streak: number;
  total_reflections: number;
  last_reflection_date?: Date;
  missed_days_this_week: number;
  needs_reminder: boolean;
}

// Utility Types
export type ValidationResult = {
  isValid: boolean;
  errors: string[];
  warnings: string[];
};

export type APIResponse<T> = {
  success: boolean;
  data?: T;
  error?: string;
  timestamp: Date;
};

export type PaginatedResponse<T> = APIResponse<{
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  hasNext: boolean;
}>;

// Constants
export const CRYSTAL_ATTRIBUTES = Object.values(CrystalAttribute);
export const TASK_TYPES = Object.values(TaskType);
export const TASK_STATUSES = Object.values(TaskStatus);
export const CHAPTER_TYPES = Object.values(ChapterType);

export const XP_CALCULATION_CONSTANTS = {
  BASE_XP_PER_DIFFICULTY: 10,
  MOOD_COEFFICIENT_RANGE: { min: 0.8, max: 1.2 },
  ADHD_ASSIST_RANGE: { min: 1.0, max: 1.3 },
  RESONANCE_BONUS_MULTIPLIER: 1.5
} as const;

export const MANDALA_CONSTANTS = {
  GRID_SIZE: 9,
  CENTER_POSITION: [4, 4] as [number, number],
  MAX_DAILY_TASKS: 16
} as const;

export const THERAPEUTIC_CONSTANTS = {
  MOOD_SCALE_MIN: 1,
  MOOD_SCALE_MAX: 5,
  CRYSTAL_MAX_VALUE: 100,
  RESONANCE_LEVEL_THRESHOLD: 5,
  GROWTH_NOTE_XP_REWARD: 25
} as const;