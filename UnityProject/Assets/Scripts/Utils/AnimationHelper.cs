using UnityEngine;
using System.Collections.Generic;

namespace KokoroNoBoukensha.Utils
{
    /// <summary>
    /// アニメーションヘルパークラス
    /// 8方向移動アニメーションの制御をサポート
    /// </summary>
    public static class AnimationHelper
    {
        /// <summary>
        /// 8方向から最も近い方向を取得
        /// </summary>
        public static Direction8 GetDirection8(Vector2Int direction)
        {
            if (direction == Vector2Int.zero)
                return Direction8.None;

            // 正規化
            float angle = Mathf.Atan2(direction.y, direction.x) * Mathf.Rad2Deg;
            
            // -180 ~ 180 → 0 ~ 360
            if (angle < 0) angle += 360;

            // 8方向に分割 (45度区切り)
            if (angle >= 337.5f || angle < 22.5f)
                return Direction8.East;
            else if (angle >= 22.5f && angle < 67.5f)
                return Direction8.NorthEast;
            else if (angle >= 67.5f && angle < 112.5f)
                return Direction8.North;
            else if (angle >= 112.5f && angle < 157.5f)
                return Direction8.NorthWest;
            else if (angle >= 157.5f && angle < 202.5f)
                return Direction8.West;
            else if (angle >= 202.5f && angle < 247.5f)
                return Direction8.SouthWest;
            else if (angle >= 247.5f && angle < 292.5f)
                return Direction8.South;
            else // 292.5f ~ 337.5f
                return Direction8.SouthEast;
        }

        /// <summary>
        /// Direction8からBlendTree用の2Dベクトルを取得
        /// </summary>
        public static Vector2 GetBlendTreeVector(Direction8 direction)
        {
            switch (direction)
            {
                case Direction8.North:
                    return new Vector2(0, 1);
                case Direction8.NorthEast:
                    return new Vector2(0.707f, 0.707f);
                case Direction8.East:
                    return new Vector2(1, 0);
                case Direction8.SouthEast:
                    return new Vector2(0.707f, -0.707f);
                case Direction8.South:
                    return new Vector2(0, -1);
                case Direction8.SouthWest:
                    return new Vector2(-0.707f, -0.707f);
                case Direction8.West:
                    return new Vector2(-1, 0);
                case Direction8.NorthWest:
                    return new Vector2(-0.707f, 0.707f);
                default:
                    return Vector2.zero;
            }
        }

        /// <summary>
        /// 方向からQuaternion回転を取得
        /// </summary>
        public static Quaternion GetRotationFromDirection(Direction8 direction)
        {
            float angle = GetAngleFromDirection(direction);
            return Quaternion.Euler(0, angle, 0);
        }

        /// <summary>
        /// 方向から角度を取得
        /// </summary>
        public static float GetAngleFromDirection(Direction8 direction)
        {
            switch (direction)
            {
                case Direction8.North:
                    return 0f;
                case Direction8.NorthEast:
                    return 45f;
                case Direction8.East:
                    return 90f;
                case Direction8.SouthEast:
                    return 135f;
                case Direction8.South:
                    return 180f;
                case Direction8.SouthWest:
                    return 225f;
                case Direction8.West:
                    return 270f;
                case Direction8.NorthWest:
                    return 315f;
                default:
                    return 0f;
            }
        }

        /// <summary>
        /// アニメーション名を取得 (方向別)
        /// </summary>
        public static string GetAnimationName(string baseAnimName, Direction8 direction)
        {
            if (direction == Direction8.None)
                return baseAnimName;

            string suffix = direction.ToString();
            return $"{baseAnimName}_{suffix}";
        }

        /// <summary>
        /// アニメーションの長さを取得
        /// </summary>
        public static float GetAnimationLength(Animator animator, string stateName)
        {
            if (animator == null) return 0f;

            AnimatorClipInfo[] clipInfo = animator.GetCurrentAnimatorClipInfo(0);
            
            foreach (var clip in clipInfo)
            {
                if (clip.clip.name == stateName)
                {
                    return clip.clip.length;
                }
            }

            return 0f;
        }

        /// <summary>
        /// 現在のアニメーションの正規化時間を取得 (0.0 ~ 1.0)
        /// </summary>
        public static float GetNormalizedTime(Animator animator, int layerIndex = 0)
        {
            if (animator == null) return 0f;

            AnimatorStateInfo stateInfo = animator.GetCurrentAnimatorStateInfo(layerIndex);
            return stateInfo.normalizedTime % 1.0f;
        }

        /// <summary>
        /// アニメーションが終了したか確認
        /// </summary>
        public static bool IsAnimationFinished(Animator animator, string stateName, int layerIndex = 0)
        {
            if (animator == null) return true;

            AnimatorStateInfo stateInfo = animator.GetCurrentAnimatorStateInfo(layerIndex);
            
            return stateInfo.IsName(stateName) && stateInfo.normalizedTime >= 1.0f;
        }

        /// <summary>
        /// アニメーションをクロスフェード
        /// </summary>
        public static void CrossFade(Animator animator, string stateName, float transitionDuration = 0.25f)
        {
            if (animator == null) return;

            animator.CrossFade(stateName, transitionDuration);
        }

        /// <summary>
        /// アニメーション速度を設定
        /// </summary>
        public static void SetAnimationSpeed(Animator animator, float speed)
        {
            if (animator == null) return;

            animator.speed = speed;
        }

        /// <summary>
        /// レイヤーの重みを設定
        /// </summary>
        public static void SetLayerWeight(Animator animator, int layerIndex, float weight)
        {
            if (animator == null) return;

            animator.SetLayerWeight(layerIndex, weight);
        }

        /// <summary>
        /// 全てのトリガーをリセット
        /// </summary>
        public static void ResetAllTriggers(Animator animator)
        {
            if (animator == null) return;

            foreach (var param in animator.parameters)
            {
                if (param.type == AnimatorControllerParameterType.Trigger)
                {
                    animator.ResetTrigger(param.name);
                }
            }
        }
    }

    /// <summary>
    /// 8方向の列挙型
    /// </summary>
    public enum Direction8
    {
        None,
        North,      // 北 (0, 1)
        NorthEast,  // 北東 (1, 1)
        East,       // 東 (1, 0)
        SouthEast,  // 南東 (1, -1)
        South,      // 南 (0, -1)
        SouthWest,  // 南西 (-1, -1)
        West,       // 西 (-1, 0)
        NorthWest   // 北西 (-1, 1)
    }

    /// <summary>
    /// アニメーションイベントヘルパー
    /// </summary>
    public class AnimationEventHelper : MonoBehaviour
    {
        // コールバック登録用
        public System.Action OnAttackStart;
        public System.Action OnAttackHit;
        public System.Action OnAttackEnd;
        public System.Action OnUseItem;
        public System.Action OnFootstep;

        // Animation Eventから呼ばれるメソッド
        public void AnimEvent_AttackStart()
        {
            OnAttackStart?.Invoke();
        }

        public void AnimEvent_AttackHit()
        {
            OnAttackHit?.Invoke();
        }

        public void AnimEvent_AttackEnd()
        {
            OnAttackEnd?.Invoke();
        }

        public void AnimEvent_UseItem()
        {
            OnUseItem?.Invoke();
        }

        public void AnimEvent_Footstep()
        {
            OnFootstep?.Invoke();
        }
    }

    /// <summary>
    /// アニメーションカーブヘルパー
    /// </summary>
    public static class AnimationCurveHelper
    {
        // イージング関数

        public static float EaseInQuad(float t)
        {
            return t * t;
        }

        public static float EaseOutQuad(float t)
        {
            return t * (2 - t);
        }

        public static float EaseInOutQuad(float t)
        {
            return t < 0.5f ? 2 * t * t : -1 + (4 - 2 * t) * t;
        }

        public static float EaseInCubic(float t)
        {
            return t * t * t;
        }

        public static float EaseOutCubic(float t)
        {
            return (--t) * t * t + 1;
        }

        public static float EaseInOutCubic(float t)
        {
            return t < 0.5f ? 4 * t * t * t : (t - 1) * (2 * t - 2) * (2 * t - 2) + 1;
        }

        public static float EaseInSine(float t)
        {
            return 1 - Mathf.Cos(t * Mathf.PI / 2);
        }

        public static float EaseOutSine(float t)
        {
            return Mathf.Sin(t * Mathf.PI / 2);
        }

        public static float EaseInOutSine(float t)
        {
            return -(Mathf.Cos(Mathf.PI * t) - 1) / 2;
        }

        /// <summary>
        /// アニメーションカーブを生成
        /// </summary>
        public static AnimationCurve CreateEaseCurve(System.Func<float, float> easeFunction, int segments = 10)
        {
            Keyframe[] keys = new Keyframe[segments + 1];
            
            for (int i = 0; i <= segments; i++)
            {
                float t = i / (float)segments;
                float value = easeFunction(t);
                keys[i] = new Keyframe(t, value);
            }

            return new AnimationCurve(keys);
        }
    }
}
