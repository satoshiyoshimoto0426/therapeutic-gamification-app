using UnityEngine;

namespace KokoroNoBoukensha.Character
{
    /// <summary>
    /// プレイヤーのアニメーション制御
    /// </summary>
    [RequireComponent(typeof(Animator))]
    public class PlayerAnimationController : MonoBehaviour
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
        private readonly int moveSpeedHash = Animator.StringToHash("MoveSpeed");

        [Header("Animation Speeds")]
        public float idleAnimSpeed = 1f;
        public float walkAnimSpeed = 1f;
        public float attackAnimSpeed = 1.2f;

        private Player player;

        private void Awake()
        {
            if (animator == null)
            {
                animator = GetComponent<Animator>();
            }

            player = GetComponent<Player>();
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
            if (animator == null || player == null) return;

            // 移動アニメーション
            bool isMoving = player.isMoving;
            animator.SetBool(isMovingHash, isMoving);

            // 移動速度を設定
            float moveSpeed = isMoving ? player.moveSpeed : 0f;
            animator.SetFloat(moveSpeedHash, moveSpeed);
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

            Debug.Log("[PlayerAnimation] Playing Idle");
        }

        /// <summary>
        /// 移動アニメーション
        /// </summary>
        public void PlayMove()
        {
            if (animator == null) return;

            animator.SetBool(isMovingHash, true);
            animator.speed = walkAnimSpeed;

            Debug.Log("[PlayerAnimation] Playing Move");
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

            Debug.Log("[PlayerAnimation] Playing Attack");

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

            Debug.Log("[PlayerAnimation] Playing TakeDamage");
        }

        /// <summary>
        /// 死亡アニメーション
        /// </summary>
        public void PlayDeath()
        {
            if (animator == null) return;

            animator.SetTrigger(deathTriggerHash);

            Debug.Log("[PlayerAnimation] Playing Death");
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

        /// <summary>
        /// アニメーターの状態を取得
        /// </summary>
        public bool IsPlayingAnimation(string animationName)
        {
            if (animator == null) return false;

            AnimatorStateInfo stateInfo = animator.GetCurrentAnimatorStateInfo(0);
            return stateInfo.IsName(animationName);
        }

        /// <summary>
        /// 現在のアニメーションが終了したかチェック
        /// </summary>
        public bool IsAnimationFinished()
        {
            if (animator == null) return true;

            AnimatorStateInfo stateInfo = animator.GetCurrentAnimatorStateInfo(0);
            return stateInfo.normalizedTime >= 1.0f;
        }
    }
}
