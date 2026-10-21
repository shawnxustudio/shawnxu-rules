# Shawnxu Rules

个人补充规则集，叠加在 [Loyalsoldier/clash-rules](https://github.com/Loyalsoldier/clash-rules)（Shadowrocket 用 [Loyalsoldier/surge-rules](https://github.com/Loyalsoldier/surge-rules)）之上，采用黑名单模式：命中规则的走代理，其余直连。

- **个人规则**：只维护根目录的三个 `.txt`，GitHub Actions 自动生成各客户端的格式
- **Loyalsoldier 规则**：直接远程引用，跟随上游每日更新，不复制进本仓库

## 规则顺序

| 顺序 | 规则集 | 策略 | 来源 |
|---|---|---|---|
| 1 | [reject.txt](reject.txt) | REJECT | 本仓库 |
| 2 | [direct.txt](direct.txt) | DIRECT | 本仓库 |
| 3 | [proxy.txt](proxy.txt) | PROXY | 本仓库 |
| 4 | applications | DIRECT | Loyalsoldier（仅 Clash，iOS 无进程规则） |
| 5 | private | DIRECT | Loyalsoldier |
| 6 | lancidr | DIRECT | Loyalsoldier（仅 Clash，Shadowrocket 由 `bypass-tun` 绕过局域网） |
| 7 | reject | REJECT | Loyalsoldier |
| 8 | tld-not-cn | PROXY | Loyalsoldier |
| 9 | gfw | PROXY | Loyalsoldier |
| 10 | telegramcidr | PROXY | Loyalsoldier |
| 11 | 其余所有 | DIRECT | |

> `tld-not-cn` 只包含 `.io`、`.gov` 等少数顶级域，**不含 `.com/.org/.net`**。这些域名不在 gfw 列表里时会直连，需要代理就加进 `proxy.txt`。

## 生成的文件

| 文件 | 用途 |
|---|---|
| [dist/clash-verge.js](dist/clash-verge.js) | Clash Verge Rev 全局扩展脚本 |
| [dist/mihomo.yaml](dist/mihomo.yaml) | 群晖 Mihomo 完整配置模板 |
| [dist/shadowrocket.conf](dist/shadowrocket.conf) | Shadowrocket 配置 |
| `dist/mihomo/*.list`、`dist/shadowrocket/*.list` | 上面三个配置引用的个人规则集（classical 格式，支持关键词） |
| `dist/mihomo/*.txt` | 旧版 domain 格式，不含关键词，仅为兼容尚未更新的配置 |

## 接入

### 电脑：Clash Verge Rev

1. 正常导入机场订阅
2. 在「订阅」页找到「全局扩展脚本」，编辑，把 [dist/clash-verge.js](dist/clash-verge.js) 的内容整段粘贴进去并保存
3. 选中订阅，让配置重新生效

脚本保留订阅里的节点，把分组换成 `PROXY`（手动选择）和 `AUTO`（自动测速），规则换成上表。之后加域名不用重新粘贴，客户端会按周期拉取新规则；只有规则顺序或分组变了才需要重新粘贴。

### 群晖：Mihomo

1. 下载 [dist/mihomo.yaml](dist/mihomo.yaml)，改名为 `config.yaml`
2. 把 `<在这里填写你的订阅链接>` 换成机场订阅，把 `<在这里设置面板密码>` 换成面板密码
3. 放到 Mihomo 的配置目录（Docker 一般映射到 `/root/.config/mihomo`），重启容器

**填好订阅的文件只放在 NAS 上，不要提交回仓库**，否则订阅会公开泄露。局域网设备把代理设为 `NAS的IP:7890` 即可使用。

### 手机：Shadowrocket

1. 首页照常添加机场订阅
2. 「配置」页 → 右上角 `+` → 粘贴下面的地址 → 下载
   ```
   https://cdn.jsdelivr.net/gh/shawnxustudio/shawnxu-rules@main/dist/shadowrocket.conf
   ```
3. 点击下载好的配置 →「使用配置」

规则里的 `PROXY` 就是首页选中的节点。Loyalsoldier 的 reject 列表接近 20 万条，如果手机上发现卡顿或耗电明显，可以在 Shadowrocket 里把那一条规则删掉。

## 新增规则

1. 在 GitHub 网页上打开 `proxy.txt`（或 `direct.txt` / `reject.txt`），点 ✏️ 编辑
2. 加一行：`+.example.com` 匹配域名及所有子域名，`example.com` 只匹配这一个域名，`keyword:example` 匹配所有包含该关键词的域名（范围大，慎用）
3. Commit 保存

Actions 会自动生成 `dist/` 并刷新 jsDelivr 缓存，各客户端到更新周期后拿到新规则（Clash 的个人规则 1 小时、Loyalsoldier 规则 24 小时），想马上生效就在客户端里手动更新规则集。域名写错时构建会失败，`dist/` 保持不变，客户端不受影响。

本地构建：`python scripts/build.py`
