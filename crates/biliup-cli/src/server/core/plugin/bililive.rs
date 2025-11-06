use crate::server::common::util::media_ext_from_url;
use crate::server::config::Config;
use crate::server::core::downloader::Downloader;
use crate::server::core::plugin::{DownloadPlugin, StreamInfoExt, StreamStatus};
use crate::server::errors::AppError;
use crate::server::infrastructure::context::Context;
use crate::server::infrastructure::models::StreamerInfo;
use async_trait::async_trait;
use chrono::Utc;
use error_stack::{Report, ResultExt, bail};
use regex::Regex;
use reqwest::header::HeaderMap;
use serde::{Deserialize, Serialize};
use serde_json::json;
use std::collections::HashMap;
use std::time::{SystemTime, UNIX_EPOCH};


const OFFICIAL_API: &str = "https://api.live.bilibili.com";


#[derive(Debug, Clone)]
enum Protocol {
    Stream,
    Ts,
    Fmp4,
}

/// Bililive 插件配置
///
/// 此结构体通过 serde 自动从 Config 中反序列化
/// 字段名对应 config.yaml 中去掉 "bililive_" 前缀后的名称
#[derive(Debug, Clone, serde::Deserialize)]
#[serde(default)]
struct PluginConfig {
    /// 弹幕录制 (对应 bililive_danmaku)
    danmaku: bool,
    /// CDN 节点列表 (对应 bililive_cdn)
    cdn: Vec<String>,
    /// 协议类型 (对应 bililive_protocol)
    #[serde(deserialize_with = "deserialize_protocol")]
    protocol: Protocol,
    /// 强制原画 (对应 bililive_force_source)
    force_source: bool,
    /// 直播 API (对应 bililive_liveapi)
    liveapi: String,
    /// 画质编号 (对应 bililive_qn)
    qn: u32,
}

/// 自定义反序列化 Protocol
fn deserialize_protocol<'de, D>(deserializer: D) -> Result<Protocol, D::Error>
where
    D: serde::Deserializer<'de>,
{
    let s: Option<String> = Option::deserialize(deserializer)?;
    Ok(match s.as_deref() {
        Some("hls_ts") => Protocol::Ts,
        Some("hls_fmp4") => Protocol::Fmp4,
        _ => Protocol::Stream,
    })
}

impl Default for PluginConfig {
    fn default() -> Self {
        Self {
            danmaku: false,
            cdn: Vec::new(),
            protocol: Protocol::Stream,
            force_source: false,
            liveapi: OFFICIAL_API.to_string(),
            qn: 25000,
        }
    }
}

impl PluginConfig {
    /// 从全局配置中提取指定前缀的配置项
    ///
    /// # 参数
    /// * `config` - 全局配置
    /// * `prefix` - 配置前缀（如 "bililive"）
    ///
    /// # 示例
    /// ```
    /// let plugin_config = PluginConfig::from_config(&config, "bililive").unwrap();
    /// ```
    fn from_config(config: &Config, prefix: &str) -> Result<Self, AppError> {
        // 使用 Config 的通用方法提取配置
        config.get_paltform_config_by_prefix(prefix).map_err(|e| {
            AppError::Custom(format!("Failed to parse {} config: {}", prefix, e))
        })
    }
}

pub struct Bililive {
    fake_headers: HeaderMap,
    re: Regex,
}

impl Bililive {
    pub fn new() -> Self {
        Self {
            fake_headers: Default::default(),
            re: Regex::new(r"live\.bilibili\.com").unwrap(),
        }
    }
}

#[async_trait]
impl DownloadPlugin for Bililive {
    fn matches(&self, url: &str) -> bool {
        self.re.is_match(url)
    }

    async fn check_status(&self, ctx: &mut Context) -> Result<StreamStatus, Report<AppError>> {
        // 从全局配置中批量初始化插件配置
        // Config 会自动提取所有 bililive_ 前缀的配置并反序列化为 PluginConfig
        let config = ctx.worker.get_config();
        let plugin_config = PluginConfig::from_config(&config, self.name())
            .change_context(AppError::Custom("加载插件配置失败".to_string()))?;

        // 现在可以直接使用 plugin_config 中的所有配置项
        // 例如：plugin_config.danmaku, plugin_config.cdn, plugin_config.protocol 等
        // 无需手动写 config.bililive_xxx

        let mut fake_headers = self.fake_headers.clone();
        // 设置headers
        fake_headers.insert("content-type", "text/plain;charset=UTF-8".parse().unwrap());
        fake_headers.insert("referer", "https://www.yy.com/".parse().unwrap());
        let url = ctx.worker.live_streamer.url.to_string();
        let name = ctx.worker.live_streamer.remark.to_string();
        // 提取房间ID
        let rid = match url.split("www.yy.com/").nth(1) {
            Some(part) => part.split('/').next().unwrap_or(""),
            None => {
                bail!(AppError::Custom("直播间地址错误".to_string()))
            }
        };

        if rid.is_empty() {
            bail!(AppError::Custom("rid 为空".to_string()))
        }

        // 获取时间戳
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .expect("时间错误");
        let millis_13 = now.as_millis() as u64;
        let millis_10 = now.as_secs();

        // 构建JSON数据
        let data = json!({
            "head": {
                "seq": millis_13,
                "appidstr": "0",
                "bidstr": "121",
                "cidstr": rid,
                "sidstr": rid,
                "uid64": 0,
                "client_type": 108,
                "client_ver": "5.11.0-alpha.4",
                "stream_sys_ver": 1,
                "app": "yylive_web",
                "playersdk_ver": "5.11.0-alpha.4",
                "thundersdk_ver": "0",
                "streamsdk_ver": "5.11.0-alpha.4"
            },
            "client_attribute": {
                "client": "web",
                "model": "",
                "cpu": "",
                "graphics_card": "",
                "os": "chrome",
                "osversion": "106.0.0.0",
                "vsdk_version": "",
                "app_identify": "",
                "app_version": "",
                "business": "",
                "width": "1536",
                "height": "864",
                "scale": "",
                "client_type": 8,
                "h265": 0
            },
            "avp_parameter": {
                "version": 1,
                "client_type": 8,
                "service_type": 0,
                "imsi": 0,
                "send_time": millis_10,
                "line_seq": -1,
                "gear": 4,
                "ssl": 1,
                "stream_format": 0
            }
        })
        .to_string();

        // 构建URL
        // 发送POST请求并处理响应
        let result = ctx
            .worker
            .client
            .client
            .post(&format!(
                "https://stream-manager.yy.com/v3/channel/streams?uid=0&cid={}&sid={}&appid=0&sequence={}&encode=json",
                rid, rid, millis_13
            ))
            .timeout(std::time::Duration::from_secs(30))
            .headers(self.fake_headers.clone())
            .body(data)
            .send()
            .await
            .change_context(AppError::Custom(format!("rid: {rid}")))?
            .json::<serde_json::Value>()
            .await
            .change_context(AppError::Custom(format!("解析json出错 rid: {rid}")))?;

        let Some(_stream_url) = result
            .get("avp_info_res")
            .and_then(|info| info.get("stream_line_addr"))
            .and_then(|addr| addr.as_object())
            .and_then(|obj| obj.values().next())
            .and_then(|val| val.get("cdn_info"))
            .and_then(|cdn| cdn.get("url"))
            .and_then(|url| url.as_str())
        else {
            return Ok(StreamStatus::Offline);
        };
        let raw_stream_url = "".to_string();
        Ok(StreamStatus::Live {
            stream_info: Box::new(StreamInfoExt {
                streamer_info: StreamerInfo {
                    id: -1,
                    name,
                    url,
                    title: "".to_string(),
                    date: Utc::now(),
                    live_cover_path: "".to_string(),
                },
                suffix: media_ext_from_url(&raw_stream_url).unwrap(),
                raw_stream_url,
                platform: self.name().to_string(),
                stream_headers: HashMap::new(),
            }),
        })
    }

    fn danmaku_init(&self) -> Option<Box<dyn Downloader>> {
        None
    }

    fn name(&self) -> &str {
        "Bililive"
    }
}
