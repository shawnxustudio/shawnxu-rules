# Shawnxu Rules

个人使用的 Mihomo/Clash 规则集，按域名分流。

## 规则文件

| 文件 | 说明 | 策略 |
|------|------|------|
| [proxy.txt](proxy.txt) | 需要代理的域名 | PROXY |
| [direct.txt](direct.txt) | 国内直连域名 | DIRECT |
| [reject.txt](reject.txt) | 广告/跟踪/恶意域名 | REJECT |

## 使用方式

在 Mihomo/Clash 配置文件中添加 rule-provider：

```yaml
rule-providers:
  shawnxu-proxy:
    type: http
    behavior: domain
    url: "https://raw.githubusercontent.com/shawnxustudio/shawnxu-rules/main/proxy.txt"
    path: ./ruleset/shawnxu-proxy.yaml
    interval: 86400

  shawnxu-direct:
    type: http
    behavior: domain
    url: "https://raw.githubusercontent.com/shawnxustudio/shawnxu-rules/main/direct.txt"
    path: ./ruleset/shawnxu-direct.yaml
    interval: 86400

  shawnxu-reject:
    type: http
    behavior: domain
    url: "https://raw.githubusercontent.com/shawnxustudio/shawnxu-rules/main/reject.txt"
    path: ./ruleset/shawnxu-reject.yaml
    interval: 86400

rules:
  - RULE-SET,shawnxu-reject,REJECT
  - RULE-SET,shawnxu-direct,DIRECT
  - RULE-SET,shawnxu-proxy,PROXY
  - MATCH,DIRECT
```

## 国内加速访问

如果 `raw.githubusercontent.com` 访问不稳定，可使用 jsDelivr CDN：

```
https://cdn.jsdelivr.net/gh/shawnxustudio/shawnxu-rules@main/proxy.txt
https://cdn.jsdelivr.net/gh/shawnxustudio/shawnxu-rules@main/direct.txt
https://cdn.jsdelivr.net/gh/shawnxustudio/shawnxu-rules@main/reject.txt
```

## 格式说明

- `example.com` — 精确匹配该域名（不含子域名）
- `+.example.com` — 匹配该域名及所有子域名

## 贡献

欢迎提交 PR 补充常用域名规则。
