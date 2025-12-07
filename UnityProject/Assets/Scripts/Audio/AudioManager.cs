using UnityEngine;
using UnityEngine.Audio;
using System.Collections;
using System.Collections.Generic;

namespace KokoroNoBoukensha.Audio
{
    /// <summary>
    /// オーディオ管理システム
    /// BGM・SE・ボイスの再生を統合管理
    /// </summary>
    public class AudioManager : MonoBehaviour
    {
        #region Singleton
        private static AudioManager instance;
        public static AudioManager Instance
        {
            get
            {
                if (instance == null)
                {
                    instance = FindObjectOfType<AudioManager>();
                    if (instance == null)
                    {
                        GameObject go = new GameObject("AudioManager");
                        instance = go.AddComponent<AudioManager>();
                    }
                }
                return instance;
            }
        }
        #endregion

        [Header("Audio Mixer")]
        [Tooltip("オーディオミキサー")]
        public AudioMixer audioMixer;

        [Header("Audio Sources")]
        [Tooltip("BGM用AudioSource")]
        public AudioSource bgmSource;
        
        [Tooltip("SE用AudioSourceプール")]
        public List<AudioSource> sfxSources = new List<AudioSource>();
        
        [Tooltip("SE用AudioSourceの数")]
        public int sfxSourceCount = 10;

        [Header("BGM Settings")]
        [Tooltip("BGMクリップ")]
        public List<BGMClip> bgmClips = new List<BGMClip>();
        
        [Tooltip("BGMフェード時間")]
        public float bgmFadeDuration = 1.5f;
        
        [Tooltip("BGMループ")]
        public bool bgmLoop = true;

        [Header("SFX Settings")]
        [Tooltip("SEクリップ")]
        public List<SFXClip> sfxClips = new List<SFXClip>();
        
        [Tooltip("SEの最大同時再生数")]
        public int maxSimultaneousSFX = 5;

        [Header("Volume Settings")]
        [Tooltip("マスターボリューム (0.0 - 1.0)")]
        [Range(0f, 1f)]
        public float masterVolume = 1.0f;
        
        [Tooltip("BGMボリューム (0.0 - 1.0)")]
        [Range(0f, 1f)]
        public float bgmVolume = 0.7f;
        
        [Tooltip("SEボリューム (0.0 - 1.0)")]
        [Range(0f, 1f)]
        public float sfxVolume = 1.0f;

        // 内部状態
        private BGMClip currentBGM;
        private Coroutine bgmFadeCoroutine;
        private int currentSfxSourceIndex = 0;
        private Dictionary<string, AudioClip> bgmCache = new Dictionary<string, AudioClip>();
        private Dictionary<string, AudioClip> sfxCache = new Dictionary<string, AudioClip>();

        private void Awake()
        {
            if (instance == null)
            {
                instance = this;
                DontDestroyOnLoad(gameObject);
                InitializeAudioSources();
                LoadVolumeSettings();
            }
            else if (instance != this)
            {
                Destroy(gameObject);
                return;
            }
        }

        /// <summary>
        /// AudioSourceを初期化
        /// </summary>
        private void InitializeAudioSources()
        {
            // BGM AudioSource
            if (bgmSource == null)
            {
                GameObject bgmGO = new GameObject("BGM_Source");
                bgmGO.transform.SetParent(transform);
                bgmSource = bgmGO.AddComponent<AudioSource>();
                bgmSource.loop = bgmLoop;
                bgmSource.playOnAwake = false;
                
                if (audioMixer != null)
                {
                    bgmSource.outputAudioMixerGroup = audioMixer.FindMatchingGroups("BGM")[0];
                }
            }

            // SFX AudioSources
            if (sfxSources.Count == 0)
            {
                for (int i = 0; i < sfxSourceCount; i++)
                {
                    GameObject sfxGO = new GameObject($"SFX_Source_{i}");
                    sfxGO.transform.SetParent(transform);
                    AudioSource sfxSource = sfxGO.AddComponent<AudioSource>();
                    sfxSource.playOnAwake = false;
                    sfxSource.loop = false;
                    
                    if (audioMixer != null)
                    {
                        sfxSource.outputAudioMixerGroup = audioMixer.FindMatchingGroups("SFX")[0];
                    }
                    
                    sfxSources.Add(sfxSource);
                }
            }
        }

        #region BGM Control

        /// <summary>
        /// BGMを再生（名前で指定）
        /// </summary>
        public void PlayBGM(string bgmName, bool fade = true)
        {
            BGMClip clip = bgmClips.Find(b => b.clipName == bgmName);
            
            if (clip == null)
            {
                Debug.LogWarning($"[AudioManager] BGM not found: {bgmName}");
                return;
            }

            PlayBGM(clip, fade);
        }

        /// <summary>
        /// BGMを再生（BGMClipで指定）
        /// </summary>
        public void PlayBGM(BGMClip clip, bool fade = true)
        {
            if (clip == null || clip.audioClip == null)
            {
                Debug.LogWarning("[AudioManager] Invalid BGM clip");
                return;
            }

            // 同じBGMが再生中なら何もしない
            if (currentBGM != null && currentBGM.clipName == clip.clipName && bgmSource.isPlaying)
            {
                return;
            }

            currentBGM = clip;

            if (fade)
            {
                if (bgmFadeCoroutine != null)
                {
                    StopCoroutine(bgmFadeCoroutine);
                }
                bgmFadeCoroutine = StartCoroutine(FadeBGM(clip.audioClip));
            }
            else
            {
                bgmSource.clip = clip.audioClip;
                bgmSource.volume = bgmVolume * masterVolume;
                bgmSource.Play();
            }

            Debug.Log($"[AudioManager] Playing BGM: {clip.clipName}");
        }

        /// <summary>
        /// BGMをフェードイン/アウト
        /// </summary>
        private IEnumerator FadeBGM(AudioClip newClip)
        {
            // フェードアウト
            if (bgmSource.isPlaying)
            {
                float startVolume = bgmSource.volume;
                float elapsed = 0f;

                while (elapsed < bgmFadeDuration)
                {
                    elapsed += Time.deltaTime;
                    bgmSource.volume = Mathf.Lerp(startVolume, 0f, elapsed / bgmFadeDuration);
                    yield return null;
                }

                bgmSource.Stop();
            }

            // 新しいBGMを設定
            bgmSource.clip = newClip;
            bgmSource.Play();

            // フェードイン
            float targetVolume = bgmVolume * masterVolume;
            float elapsed2 = 0f;

            while (elapsed2 < bgmFadeDuration)
            {
                elapsed2 += Time.deltaTime;
                bgmSource.volume = Mathf.Lerp(0f, targetVolume, elapsed2 / bgmFadeDuration);
                yield return null;
            }

            bgmSource.volume = targetVolume;
        }

        /// <summary>
        /// BGMを停止
        /// </summary>
        public void StopBGM(bool fade = true)
        {
            if (fade)
            {
                if (bgmFadeCoroutine != null)
                {
                    StopCoroutine(bgmFadeCoroutine);
                }
                bgmFadeCoroutine = StartCoroutine(FadeOutBGM());
            }
            else
            {
                bgmSource.Stop();
            }
        }

        /// <summary>
        /// BGMフェードアウト
        /// </summary>
        private IEnumerator FadeOutBGM()
        {
            float startVolume = bgmSource.volume;
            float elapsed = 0f;

            while (elapsed < bgmFadeDuration)
            {
                elapsed += Time.deltaTime;
                bgmSource.volume = Mathf.Lerp(startVolume, 0f, elapsed / bgmFadeDuration);
                yield return null;
            }

            bgmSource.Stop();
            bgmSource.volume = bgmVolume * masterVolume;
        }

        /// <summary>
        /// BGMを一時停止
        /// </summary>
        public void PauseBGM()
        {
            if (bgmSource.isPlaying)
            {
                bgmSource.Pause();
            }
        }

        /// <summary>
        /// BGMを再開
        /// </summary>
        public void ResumeBGM()
        {
            if (!bgmSource.isPlaying && bgmSource.clip != null)
            {
                bgmSource.UnPause();
            }
        }

        #endregion

        #region SFX Control

        /// <summary>
        /// SEを再生（名前で指定）
        /// </summary>
        public void PlaySFX(string sfxName, float volumeScale = 1.0f)
        {
            SFXClip clip = sfxClips.Find(s => s.clipName == sfxName);
            
            if (clip == null)
            {
                Debug.LogWarning($"[AudioManager] SFX not found: {sfxName}");
                return;
            }

            PlaySFX(clip.audioClip, volumeScale);
        }

        /// <summary>
        /// SEを再生（AudioClipで指定）
        /// </summary>
        public void PlaySFX(AudioClip clip, float volumeScale = 1.0f)
        {
            if (clip == null)
            {
                Debug.LogWarning("[AudioManager] Invalid SFX clip");
                return;
            }

            // 利用可能なAudioSourceを取得
            AudioSource availableSource = GetAvailableSFXSource();
            
            if (availableSource != null)
            {
                availableSource.clip = clip;
                availableSource.volume = sfxVolume * masterVolume * volumeScale;
                availableSource.Play();
            }
        }

        /// <summary>
        /// SEを再生（3D空間位置指定）
        /// </summary>
        public void PlaySFX3D(string sfxName, Vector3 position, float volumeScale = 1.0f)
        {
            SFXClip clip = sfxClips.Find(s => s.clipName == sfxName);
            
            if (clip == null || clip.audioClip == null)
            {
                Debug.LogWarning($"[AudioManager] SFX not found: {sfxName}");
                return;
            }

            // 3D AudioSourceを一時生成
            GameObject tempGO = new GameObject($"TempSFX_{sfxName}");
            tempGO.transform.position = position;
            AudioSource tempSource = tempGO.AddComponent<AudioSource>();
            
            tempSource.clip = clip.audioClip;
            tempSource.volume = sfxVolume * masterVolume * volumeScale;
            tempSource.spatialBlend = 1.0f; // 3D
            tempSource.Play();

            // 再生終了後に破棄
            Destroy(tempGO, clip.audioClip.length);
        }

        /// <summary>
        /// 利用可能なSFX AudioSourceを取得
        /// </summary>
        private AudioSource GetAvailableSFXSource()
        {
            // 再生していないSourceを探す
            foreach (AudioSource source in sfxSources)
            {
                if (!source.isPlaying)
                {
                    return source;
                }
            }

            // 全て再生中なら、最も古いものを使用
            currentSfxSourceIndex = (currentSfxSourceIndex + 1) % sfxSources.Count;
            return sfxSources[currentSfxSourceIndex];
        }

        /// <summary>
        /// 全てのSEを停止
        /// </summary>
        public void StopAllSFX()
        {
            foreach (AudioSource source in sfxSources)
            {
                source.Stop();
            }
        }

        #endregion

        #region Volume Control

        /// <summary>
        /// マスターボリュームを設定
        /// </summary>
        public void SetMasterVolume(float volume)
        {
            masterVolume = Mathf.Clamp01(volume);
            
            if (audioMixer != null)
            {
                audioMixer.SetFloat("MasterVolume", LinearToDecibel(masterVolume));
            }
            
            UpdateAllVolumes();
            SaveVolumeSettings();
        }

        /// <summary>
        /// BGMボリュームを設定
        /// </summary>
        public void SetBGMVolume(float volume)
        {
            bgmVolume = Mathf.Clamp01(volume);
            
            if (audioMixer != null)
            {
                audioMixer.SetFloat("BGMVolume", LinearToDecibel(bgmVolume));
            }
            else if (bgmSource != null)
            {
                bgmSource.volume = bgmVolume * masterVolume;
            }
            
            SaveVolumeSettings();
        }

        /// <summary>
        /// SEボリュームを設定
        /// </summary>
        public void SetSFXVolume(float volume)
        {
            sfxVolume = Mathf.Clamp01(volume);
            
            if (audioMixer != null)
            {
                audioMixer.SetFloat("SFXVolume", LinearToDecibel(sfxVolume));
            }
            
            SaveVolumeSettings();
        }

        /// <summary>
        /// 全てのボリュームを更新
        /// </summary>
        private void UpdateAllVolumes()
        {
            if (bgmSource != null)
            {
                bgmSource.volume = bgmVolume * masterVolume;
            }

            foreach (AudioSource source in sfxSources)
            {
                source.volume = sfxVolume * masterVolume;
            }
        }

        /// <summary>
        /// リニアをデシベルに変換
        /// </summary>
        private float LinearToDecibel(float linear)
        {
            if (linear <= 0f)
                return -80f;
            
            return Mathf.Log10(linear) * 20f;
        }

        #endregion

        #region Settings Persistence

        /// <summary>
        /// ボリューム設定を保存
        /// </summary>
        private void SaveVolumeSettings()
        {
            PlayerPrefs.SetFloat("MasterVolume", masterVolume);
            PlayerPrefs.SetFloat("BGMVolume", bgmVolume);
            PlayerPrefs.SetFloat("SFXVolume", sfxVolume);
            PlayerPrefs.Save();
        }

        /// <summary>
        /// ボリューム設定をロード
        /// </summary>
        private void LoadVolumeSettings()
        {
            masterVolume = PlayerPrefs.GetFloat("MasterVolume", 1.0f);
            bgmVolume = PlayerPrefs.GetFloat("BGMVolume", 0.7f);
            sfxVolume = PlayerPrefs.GetFloat("SFXVolume", 1.0f);

            SetMasterVolume(masterVolume);
            SetBGMVolume(bgmVolume);
            SetSFXVolume(sfxVolume);
        }

        #endregion

        #region Utility Methods

        /// <summary>
        /// BGMが再生中か
        /// </summary>
        public bool IsBGMPlaying()
        {
            return bgmSource != null && bgmSource.isPlaying;
        }

        /// <summary>
        /// 現在再生中のBGM名を取得
        /// </summary>
        public string GetCurrentBGMName()
        {
            return currentBGM != null ? currentBGM.clipName : "None";
        }

        #endregion
    }

    #region Data Classes

    /// <summary>
    /// BGMクリップデータ
    /// </summary>
    [System.Serializable]
    public class BGMClip
    {
        public string clipName;
        public AudioClip audioClip;
        [TextArea(2, 4)]
        public string description;
    }

    /// <summary>
    /// SEクリップデータ
    /// </summary>
    [System.Serializable]
    public class SFXClip
    {
        public string clipName;
        public AudioClip audioClip;
        [Range(0f, 1f)]
        public float defaultVolume = 1.0f;
        [TextArea(2, 4)]
        public string description;
    }

    #endregion
}
