using UnityEngine;

namespace KokoroNoBoukensha.Character
{
    /// <summary>
    /// 敵のアニメーション制御
    /// </summary>
    [RequireComponent(typeof(Animator))]
    public class EnemyAnimationController : MonoBehaviour
    {
        [Header("Animator")]
        public Animator animator;

        [Header("Animation Parameters")]
        private readonly int isMovingHash = Animator.StringToHash("IsMoving");
        private readonly int isAttackingHash = Animator.StringToHash("IsAttacking");
        private readonly int attackTriggerHash = Animator.StringToHash("Attack");
        private readonly int takeDamageTriggerHash = Animator.StringToHash("TakeDamage");
        private readonly int deathTriggerHash = Animator.StringToHash("Death");
        private readonly int idleTriggerHash = Animator.StringToHash("Idle");

        [Header("Animation Speeds")]
        public float idleAnimSpeed = 1f;
        public float walkAnimSpeed = 0.8f;
        public float attackAnimSpeed = 1f;

        [Header("Enemy Specific")]
        public bool hasSpecialAnimation = false;
        public string specialAnimationTrigger = "Special";

        private Enemy enemy;

        private void Awake()
        {
            if (animator == null)
            {
                animator = GetComponent<Animator>();
            }

            enemy = GetComponent<Enemy>();
        }

        private void Update()
        {
            UpdateAnimationStates();
        }

        /// <summary>
        /// アニメーション状態を更新
        /// </summary>
        private void UpdateAnimationStates()
        {
            if (animator == null || enemy == null) return;

            // 移動アニメーション
            bool isMoving = enemy.isMoving;
            animator.SetBool(isMovingHash, isMoving);
        }

        /// <summary>
        /// 待機アニメーション
        /// </summary>
        public void PlayIdle()
        {
            if (animator == null) return;

            animator.SetTrigger(idleTriggerHash);
            animator.SetBool(isMovingHash, false);
            animator.speed = idleAnimSpeed;
        }

        /// <summary>
        /// 移動アニメーション
        /// </summary>
        public void PlayMove()
        {
            if (animator == null) return;

            animator.SetBool(isMovingHash, true);
            animator.speed = walkAnimSpeed;
        }

        /// <summary>
        /// 攻撃アニメーション
        /// </summary>
        public void PlayAttack()
        {
            if (animator == null) return;

            animator.SetTrigger(attackTriggerHash);
            animator.SetBool(isAttackingHash, true);
            animator.speed = attackAnimSpeed;

            // 攻撃アニメーション終了後にリセット
            StartCoroutine(ResetAttackFlag());
        }

        /// <summary>
        /// 被ダメージアニメーション
        /// </summary>
        public void PlayTakeDamage()
        {
            if (animator == null) return;

            animator.SetTrigger(takeDamageTriggerHash);
        }

        /// <summary>
        /// 死亡アニメーション
        /// </summary>
        public void PlayDeath()
        {
            if (animator == null) return;

            animator.SetTrigger(deathTriggerHash);
        }

        /// <summary>
        /// 特殊アニメーション（ボス専用など）
        /// </summary>
        public void PlaySpecial()
        {
            if (animator == null || !hasSpecialAnimation) return;

            int specialHash = Animator.StringToHash(specialAnimationTrigger);
            animator.SetTrigger(specialHash);
        }

        /// <summary>
        /// 攻撃フラグをリセット
        /// </summary>
        private System.Collections.IEnumerator ResetAttackFlag()
        {
            yield return new WaitForSeconds(0.5f);
            
            if (animator != null)
            {
                animator.SetBool(isAttackingHash, false);
                animator.speed = 1f;
            }
        }

        /// <summary>
        /// アニメーション速度を設定
        /// </summary>
        public void SetAnimationSpeed(float speed)
        {
            if (animator != null)
            {
                animator.speed = speed;
            }
        }
    }
}
