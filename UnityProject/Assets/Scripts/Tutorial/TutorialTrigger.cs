using UnityEngine;

namespace KokoroNoBoukensha.Tutorial
{
    /// <summary>
    /// チュートリアルトリガー
    /// プレイヤーの行動を検知してTutorialManagerに通知
    /// </summary>
    public class TutorialTrigger : MonoBehaviour
    {
        /// <summary>
        /// 移動アクション通知
        /// </summary>
        public static void NotifyMove()
        {
            if (TutorialManager.Instance != null && TutorialManager.Instance.IsTutorialActive)
            {
                TutorialManager.Instance.OnActionPerformed(TutorialAction.Move);
            }
        }

        /// <summary>
        /// 斜め移動アクション通知
        /// </summary>
        public static void NotifyMoveDiagonal()
        {
            if (TutorialManager.Instance != null && TutorialManager.Instance.IsTutorialActive)
            {
                TutorialManager.Instance.OnActionPerformed(TutorialAction.MoveDiagonal);
            }
        }

        /// <summary>
        /// 攻撃アクション通知
        /// </summary>
        public static void NotifyAttack()
        {
            if (TutorialManager.Instance != null && TutorialManager.Instance.IsTutorialActive)
            {
                TutorialManager.Instance.OnActionPerformed(TutorialAction.Attack);
            }
        }

        /// <summary>
        /// アイテム拾得アクション通知
        /// </summary>
        public static void NotifyPickupItem()
        {
            if (TutorialManager.Instance != null && TutorialManager.Instance.IsTutorialActive)
            {
                TutorialManager.Instance.OnActionPerformed(TutorialAction.PickupItem);
            }
        }

        /// <summary>
        /// インベントリ開く通知
        /// </summary>
        public static void NotifyOpenInventory()
        {
            if (TutorialManager.Instance != null && TutorialManager.Instance.IsTutorialActive)
            {
                TutorialManager.Instance.OnActionPerformed(TutorialAction.OpenInventory);
            }
        }

        /// <summary>
        /// アイテム使用通知
        /// </summary>
        public static void NotifyUseItem()
        {
            if (TutorialManager.Instance != null && TutorialManager.Instance.IsTutorialActive)
            {
                TutorialManager.Instance.OnActionPerformed(TutorialAction.UseItem);
            }
        }

        /// <summary>
        /// アイテム装備通知
        /// </summary>
        public static void NotifyEquipItem()
        {
            if (TutorialManager.Instance != null && TutorialManager.Instance.IsTutorialActive)
            {
                TutorialManager.Instance.OnActionPerformed(TutorialAction.EquipItem);
            }
        }

        /// <summary>
        /// 階段発見通知
        /// </summary>
        public static void NotifyFindStairs()
        {
            if (TutorialManager.Instance != null && TutorialManager.Instance.IsTutorialActive)
            {
                TutorialManager.Instance.OnActionPerformed(TutorialAction.FindStairs);
            }
        }

        /// <summary>
        /// ガチャ開く通知
        /// </summary>
        public static void NotifyOpenGacha()
        {
            if (TutorialManager.Instance != null && TutorialManager.Instance.IsTutorialActive)
            {
                TutorialManager.Instance.OnActionPerformed(TutorialAction.OpenGacha);
            }
        }

        /// <summary>
        /// 敵撃破通知
        /// </summary>
        public static void NotifyDefeatEnemy()
        {
            if (TutorialManager.Instance != null && TutorialManager.Instance.IsTutorialActive)
            {
                TutorialManager.Instance.OnActionPerformed(TutorialAction.DefeatEnemy);
            }
        }
    }
}
