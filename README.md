# 🖥️ JustRunMy.App 自动续期 (多账号可Proxy随机时间签到版)

> **本项目支持多账号无限扩展，随机顺序续签，带代理支持。**

【 ⚡ 快速开始 】
1. [Fork] 本项目到个人仓库。
2. 在 [Secrets] 中填入下方表格对应的账号信息。
3. 在 [Actions] 页面点击 "Run workflow" 手动激活。
4. [每1~2 天] 系统**随机自动**巡航运行一次，即便多账号也无需担心系统检测为BOT。

【 🛠️ 环境变量配置 (Secrets) 】
请前往仓库 [Settings] -> [Secrets and variables] -> [Actions]
依次添加以下加密变量：

| 变量类型 | 变量名 (Name) | 示例值 (Value) |
| :--- | :--- | :--- |
| **通知 ID（可选）** | TG_ID | 987654321 |
| **通知 Token（可选）** | TG_TOKEN | 123456:ABC-DEF... |
| **代理链接（可选）** | PROXY_URL | vless://uuid@host:port?security=tls&type=ws... |
| **账号邮箱** | EML_1, EML_2, EML_3... | user@example.com |
| **账号密码** | PWD_1, PWD_2, PWD_3... | your_password |

### 总结如下图
<img width="1428" height="817" alt="26-03-10-19-44-30" src="https://github.com/user-attachments/assets/a6351243-793f-49bc-9841-c0e619ffe9e7" />

【 🔄 运行逻辑 】
- 🔍 智能扫描：自动解析 EML_N / PWD_N 系列变量，实现账号无限扩容。
- 🎭 隔离执行：确保各账号独立运行，互不干扰。
- 🎲 随机巡航：0-2 小时随机启动延迟，彻底打破固定运行规律。
- 🌐 代理支持：支持 socks5/http/https/vless/vmess/hy2/tuic 等**明文**或**base64编码**协议，实现**固定ip**续签。

【 ⚠️ 调试与报错 】
若 Actions 运行失败，请在当前任务页面的底端 [Artifacts] 区域
下载名为 "debug-acc-X" 的压缩包，查看浏览器报错截图。

====================================

## 【 🌟 特别鸣谢 】
本项目核心续期逻辑参考并使用了👉[https://github.com/mangguo88/JustRunMy-Renew](https://github.com/mangguo88/JustRunMy-Renew)

在此特别感谢 mangguo88 提供的稳定物理模拟续期算法和proxy代理想法。
