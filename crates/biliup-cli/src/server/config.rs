use crate::server::core::downloader::DownloaderType;
use crate::server::errors::{AppError, AppResult};
use crate::server::infrastructure::models::hook_step::HookStep;
use biliup::bilibili::Credit;
use error_stack::bail;
use serde::{Deserialize, Serialize};
use std::{collections::HashMap, path::Path, path::PathBuf};

/// 下载配置模块
/// 包含录播下载相关的所有配置项
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DownloadConfig {
    /// 下载器类型：streamlink | ffmpeg | stream-gears | 自定义
    #[serde(default)]
    pub downloader: Option<DownloaderType>,

    /// 文件大小限制（字节）
    #[serde(default = "default_file_size")]
    pub file_size: u64,

    /// 分段时间，格式如 "00:00:00"，保留为字符串以保持直观
    #[serde(default = "default_segment_time")]
    pub segment_time: Option<String>,

    /// 过滤阈值（MB）
    #[serde(default = "default_filtering_threshold")]
    pub filtering_threshold: u64,

    /// 文件名前缀
    #[serde(default)]
    pub filename_prefix: Option<String>,

    /// 分段处理器是否并行执行
    #[serde(default)]
    pub segment_processor_parallel: Option<bool>,
}

impl Default for DownloadConfig {
    fn default() -> Self {
        Self {
            downloader: None,
            file_size: default_file_size(),
            segment_time: default_segment_time(),
            filtering_threshold: default_filtering_threshold(),
            filename_prefix: None,
            segment_processor_parallel: None,
        }
    }
}

/// 上传配置模块
/// 包含视频上传相关的所有配置项
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UploadConfig {
    /// 上传器类型：Noop | bili_web | biliup-rs | 其他
    #[serde(default)]
    pub uploader: Option<String>,

    /// 提交API类型：web | client
    #[serde(default)]
    pub submit_api: Option<String>,

    /// 上传线路：AUTO | alia | bda2 | bldsa | qn | tx | txa
    #[serde(default = "default_lines")]
    pub lines: String,

    /// 上传线程数
    #[serde(default = "default_threads")]
    pub threads: u32,

    /// 延迟时间（秒）
    #[serde(default = "default_delay")]
    pub delay: u64,

    /// 是否使用直播封面
    #[serde(default)]
    pub use_live_cover: Option<bool>,
}

impl Default for UploadConfig {
    fn default() -> Self {
        Self {
            uploader: None,
            submit_api: None,
            lines: default_lines(),
            threads: default_threads(),
            delay: default_delay(),
            use_live_cover: None,
        }
    }
}

/// 运行时配置模块
/// 包含程序运行时的系统配置项
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RuntimeConfig {
    /// 事件循环间隔（秒）
    #[serde(default = "default_event_loop_interval")]
    pub event_loop_interval: u64,

    /// 检查器休眠时间（秒）
    #[serde(default = "default_checker_sleep")]
    pub checker_sleep: u64,

    /// 连接池1大小
    #[serde(default = "default_pool1_size")]
    pub pool1_size: u32,

    /// 连接池2大小
    #[serde(default = "default_pool2_size")]
    pub pool2_size: u32,
}

impl Default for RuntimeConfig {
    fn default() -> Self {
        Self {
            event_loop_interval: default_event_loop_interval(),
            checker_sleep: default_checker_sleep(),
            pool1_size: default_pool1_size(),
            pool2_size: default_pool2_size(),
        }
    }
}

/// 平台特定配置模块
/// 包含各个直播平台的专属配置项
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct PlatformConfigs {
    // ===== 斗鱼平台设置 =====
    /// 斗鱼CDN节点
    #[serde(default)]
    pub douyu_cdn: Option<String>,
    /// 斗鱼弹幕录制
    #[serde(default)]
    pub douyu_danmaku: Option<bool>,
    /// 斗鱼码率
    #[serde(default)]
    pub douyu_rate: Option<u32>,

    // ===== 虎牙平台设置 =====
    /// 虎牙CDN节点
    #[serde(default)]
    pub huya_cdn: Option<String>,
    /// 虎牙CDN回退
    #[serde(default)]
    pub huya_cdn_fallback: Option<bool>,
    /// 虎牙弹幕录制
    #[serde(default)]
    pub huya_danmaku: Option<bool>,
    /// 虎牙最大比率
    #[serde(default)]
    pub huya_max_ratio: Option<u32>,
    /// 虎牙 Flv or Hls
    #[serde(default)]
    pub huya_protocol: Option<String>,

    // ===== 抖音平台设置 =====
    /// 抖音弹幕录制
    #[serde(default)]
    pub douyin_danmaku: Option<bool>,
    /// 抖音画质
    #[serde(default)]
    pub douyin_quality: Option<String>,
    /// 双屏直播录制方式
    #[serde(default)]
    pub douyin_double_screen: Option<bool>,
    /// 抖音真原画
    #[serde(default)]
    pub douyin_true_origin: Option<bool>,

    // ===== 哔哩哔哩平台设置 =====
    /// B站弹幕录制
    #[serde(default)]
    pub bililive_danmaku: Option<bool>,
    /// B站协议类型：stream | hls_ts | hls_fmp4
    #[serde(default)]
    pub bililive_protocol: Option<String>,
    /// B站CDN节点列表
    #[serde(default)]
    pub bililive_cdn: Option<Vec<String>>,
    /// B站强制原画
    #[serde(default)]
    pub bililive_force_source: Option<bool>,
    /// B站直播API
    #[serde(default)]
    pub bililive_liveapi: Option<String>,
    /// B站画质编号
    #[serde(default)]
    pub bililive_qn: Option<u32>,

    // ===== YouTube平台设置 =====
    /// YouTube首选视频编码
    #[serde(default)]
    pub youtube_prefer_vcodec: Option<String>,
    /// YouTube首选音频编码
    #[serde(default)]
    pub youtube_prefer_acodec: Option<String>,
    /// YouTube最大分辨率
    #[serde(default)]
    pub youtube_max_resolution: Option<u32>,
    /// YouTube最大视频大小
    #[serde(default)]
    pub youtube_max_videosize: Option<String>,
    /// YouTube开始日期
    #[serde(default)]
    pub youtube_after_date: Option<String>,
    /// YouTube结束日期
    #[serde(default)]
    pub youtube_before_date: Option<String>,
    /// YouTube启用直播下载
    #[serde(default)]
    pub youtube_enable_download_live: Option<bool>,
    /// YouTube启用回放下载
    #[serde(default)]
    pub youtube_enable_download_playback: Option<bool>,

    // ===== Twitch平台设置 =====
    /// Twitch弹幕录制
    #[serde(default)]
    pub twitch_danmaku: Option<bool>,
    /// Twitch禁用广告
    #[serde(default)]
    pub twitch_disable_ads: Option<bool>,

    // ===== TwitCasting平台设置 =====
    /// TwitCasting弹幕录制
    #[serde(default)]
    pub twitcasting_danmaku: Option<bool>,
    /// TwitCasting密码
    #[serde(default)]
    pub twitcasting_password: Option<String>,
}

/// 全局配置结构体
#[derive(bon::Builder, Debug, Clone, Serialize, Deserialize)]
pub struct Config {
    /// 下载配置模块
    #[serde(flatten)]
    #[builder(default)]
    pub download: DownloadConfig,

    /// 上传配置模块
    #[serde(flatten)]
    #[builder(default)]
    pub upload: UploadConfig,

    /// 运行时配置模块
    #[serde(flatten)]
    #[builder(default)]
    pub runtime: RuntimeConfig,

    /// 平台特定配置模块
    #[serde(flatten)]
    #[builder(default)]
    pub platform: PlatformConfigs,

    /// 录制主播配置映射
    #[serde(default)]
    pub streamers: HashMap<String, StreamerConfig>,

    /// 用户Cookie配置
    #[serde(default)]
    pub user: Option<UserConfig>,
}

/// 主播配置结构体
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct StreamerConfig {
    /// 直播间URL列表
    pub url: Vec<String>,

    /// 视频标题
    #[serde(default)]
    pub title: Option<String>,

    /// 分区ID
    #[serde(default)]
    pub tid: Option<u32>,

    /// 版权类型
    #[serde(default)]
    pub copyright: Option<u8>,

    /// 封面路径
    #[serde(default)]
    pub cover_path: Option<PathBuf>,

    /// 视频描述（保留缩进和多行格式）
    #[serde(default)]
    pub description: Option<String>,

    #[serde(default)]
    pub credits: Option<Vec<Credit>>,

    #[serde(default)]
    pub dynamic: Option<String>,

    #[serde(default)]
    pub dtime: Option<u64>,

    #[serde(default)]
    pub dolby: Option<u8>,

    #[serde(default)]
    pub hires: Option<u8>,

    #[serde(default)]
    pub charging_pay: Option<u8>,

    #[serde(default)]
    pub no_reprint: Option<u8>,

    #[serde(default)]
    pub is_only_self: Option<u8>,

    #[serde(default)]
    pub uploader: Option<String>,

    #[serde(default)]
    pub filename_prefix: Option<String>,

    #[serde(default)]
    pub user_cookie: Option<String>,

    #[serde(default)]
    pub use_live_cover: Option<bool>,

    #[serde(default)]
    pub tags: Option<Vec<String>>,

    #[serde(default)]
    pub time_range: Option<String>,

    #[serde(default)]
    pub excluded_keywords: Option<Vec<String>>,

    #[serde(default)]
    pub preprocessor: Option<Vec<HookStep>>,

    #[serde(default)]
    pub segment_processor: Option<Vec<HookStep>>,

    #[serde(default)]
    pub downloaded_processor: Option<Vec<HookStep>>,

    #[serde(default)]
    pub postprocessor: Option<Vec<HookStep>>,

    #[serde(default)]
    pub format: Option<String>,

    #[serde(default)]
    pub opt_args: Option<Vec<String>>,

    // “override” 是字段名，这里改为 override_cfg 避免与保留字混淆
    #[serde(rename = "override", default)]
    pub override_cfg: Option<HashMap<String, serde_json::Value>>,
}

/// 用户配置结构体
#[derive(bon::Builder, Debug, Clone, Serialize, Deserialize, Default)]
pub struct UserConfig {
    // B站配置
    /// B站Cookie字符串
    #[serde(default)]
    pub bili_cookie: Option<String>,
    /// B站Cookie文件路径
    #[serde(default)]
    pub bili_cookie_file: Option<PathBuf>,

    // 抖音配置
    /// 抖音Cookie
    #[serde(default)]
    pub douyin_cookie: Option<String>,

    // Twitch配置
    /// Twitch Cookie
    #[serde(default)]
    pub twitch_cookie: Option<String>,

    // YouTube配置
    /// YouTube Cookie文件路径
    #[serde(default)]
    pub youtube_cookie: Option<PathBuf>,

    // Niconico配置（使用rename保持与配置文件一致）
    /// Niconico邮箱
    #[serde(rename = "niconico-email", default)]
    pub niconico_email: Option<String>,
    /// Niconico密码
    #[serde(rename = "niconico-password", default)]
    pub niconico_password: Option<String>,
    /// Niconico用户会话
    #[serde(rename = "niconico-user-session", default)]
    pub niconico_user_session: Option<String>,
    /// Niconico清除凭据
    #[serde(rename = "niconico-purge-credentials", default)]
    pub niconico_purge_credentials: Option<String>,

    // AfreecaTV配置
    /// AfreecaTV用户名
    #[serde(default)]
    pub afreecatv_username: Option<String>,
    /// AfreecaTV密码
    #[serde(default)]
    pub afreecatv_password: Option<String>,
}

/// 默认文件大小：2.5GB
fn default_file_size() -> u64 {
    2_621_440_000
}

/// 默认分段时间：2小时
pub fn default_segment_time() -> Option<String> {
    Some("02:00:00".to_string())
}

/// 默认过滤阈值：20MB
fn default_filtering_threshold() -> u64 {
    20
}

/// 默认上传线路：自动选择
fn default_lines() -> String {
    "AUTO".to_string()
}

/// 默认线程数：3
fn default_threads() -> u32 {
    3
}

/// 默认延迟：300秒
fn default_delay() -> u64 {
    300
}

/// 默认事件循环间隔：30秒
fn default_event_loop_interval() -> u64 {
    30
}

/// 默认检查器休眠时间：10秒
fn default_checker_sleep() -> u64 {
    10
}

/// 默认连接池1大小：5
fn default_pool1_size() -> u32 {
    5
}

/// 默认连接池2大小：3
fn default_pool2_size() -> u32 {
    3
}

impl Config {
    /// 从指定路径加载配置文件，如果不存在则创建默认配置
    pub fn load_or_create<P: AsRef<Path>>(path: P) -> AppResult<Self> {
        bail!(AppError::Custom(format!(
            "load_or_create: {:?}",
            path.as_ref().display()
        )))
    }

    /// 根据前缀提取配置项
    ///
    /// # 参数
    /// * `prefix` - 配置前缀（如 "bililive"、"douyu"、"huya" 等）
    ///
    /// # 返回
    /// 返回一个 HashMap，key 是去掉前缀后的字段名，value 是配置值
    ///
    /// # 示例
    /// ```
    /// let bililive_config = config.get_prefix_config("bililive");
    /// // 返回: {"danmaku": true, "protocol": "hls_fmp4", "cdn": [...], ...}
    /// ```
    pub fn get_paltform_config(&self, prefix: &str) -> HashMap<String, serde_json::Value> {
        let mut result = HashMap::new();

        // 将 Config 序列化为 JSON Value
        let config_value = serde_json::to_value(self).unwrap_or(serde_json::Value::Null);

        if let serde_json::Value::Object(map) = config_value {
            let prefix_with_underscore = format!("{}_", prefix.to_lowercase());

            // 过滤出所有以指定前缀开头的字段
            for (key, value) in map {
                if key.starts_with(&prefix_with_underscore) {
                    // 去掉前缀，只保留字段名
                    let field_name = key.strip_prefix(&prefix_with_underscore)
                        .unwrap_or(&key)
                        .to_string();
                    result.insert(field_name, value);
                }
            }
        }

        result
    }

    /// 根据前缀提取配置并反序列化为指定类型
    ///
    /// # 参数
    /// * `prefix` - 配置前缀（如 "bililive"、"douyu"、"huya" 等）
    ///
    /// # 返回
    /// 返回反序列化后的配置结构体
    ///
    /// # 示例
    /// ```
    /// let plugin_config: PluginConfig = config.get_prefix_config_as("bililive")?;
    /// ```
    pub fn get_paltform_config_by_prefix<T: serde::de::DeserializeOwned>(
        &self,
        prefix: &str,
    ) -> AppResult<T> {
        let config_map = self.get_prefix_config(prefix);
        let value = serde_json::to_value(config_map)
            .map_err(|e| AppError::Custom(format!("序列化配置失败: {}", e)))?;

        serde_json::from_value(value)
            .map_err(|e| AppError::Custom(format!("反序列化配置失败: {}", e)).into())
    }
}
