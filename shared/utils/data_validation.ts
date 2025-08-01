/**
 * データ整合性のためのバリデーション関数 (TypeScript版)
 * 
 * このモジュールは、治療的ゲーミフィケーションアプリの
 * コアデータモデルに対する包括的なバリデーション機能を提供します。
 */

import {
  UserProfile, StoryState, TaskRecord, TaskType, TaskStatus,
  CrystalAttribute, ChapterType, CellStatus, GuardianPermission,
  NodeType, UnlockConditionType, ItemRarity, ItemType, JobClass, DemonType,
  ValidationResult
} from '../interfaces/core_types';

/**
 * バリデーションエラークラス
 */
export