# Shawnxu Rules

个人补充规则集，基于 [Loyalsoldier/clash-rules](https://github.com/Loyalsoldier/clash-rules) 之上，仅包含个人需要的额外域名。

## 规则文件

| 文件 | 说明 | 加载位置 |
|------|------|----------|
| [proxy.txt](proxy.txt) | 补充代理域名 | 放在 tld-not-cn 和 gfw 之前 |
| [direct.txt](direct.txt) | 补充直连域名 | 放在 tld-not-cn 之前 |
| [reject.txt](reject.txt) | 补充拒绝域名 | 放在 reject 之前 |

## 接入配置

```yaml
rule-providers:
  custom-proxy:
    type: http
    behavior: domain
    url: "https://raw.githubusercontent.com/shawnxustudio/shawnxu-rules/main/proxy.txt"
    path: ./ruleset/custom-proxy.yaml
    interval: 86400

  custom-direct:
    type: http
    behavior: domain
    url: "https://raw.githubusercontent.com/shawnxustudio/shawnxu-rules/main/direct.txt"
    path: ./ruleset/custom-direct.yaml
    interval: 86400

  custom-reject:
    type: http
    behavior: domain
    url: "https://raw.githubusercontent.com/shawnxustudio/shawnxu-rules/main/reject.txt"
    path: ./ruleset/custom-reject.yaml
    interval: 86400

rules:
  # 自定义规则（优先级最高）
  - RULE-SET,custom-reject,REJECT
  - RULE-SET,custom-direct,DIRECT
  - RULE-SET,custom-proxy,PROXY

  # Loyalsoldier 基础规则
  - RULE-SET,applications,DIRECT
  - RULE-SET,private,DIRECT
  - RULE-SET,reject,REJECT
  - RULE-SET,tld-not-cn,PROXY
  - RULE-SET,gfw,PROXY
  - RULE-SET,telegramcidr,PROXY
  - MATCH,DIRECT
```

## 国内加速

```
https://cdn.jsdelivr.net/gh/shawnxustudio/shawnxu-rules@main/proxy.txt
https://cdn.jsdelivr.net/gh/shawnxustudio/shawnxu-rules@main/direct.txt
https://cdn.jsdelivr.net/gh/shawnxustudio/shawnxu-rules@main/reject.txt
```

## 如何新增规则

1. 在 GitHub 网页上打开对应 .txt 文件
2. 点编辑（✏️ 图标）
3. 加一行 `+.你要的域名.com`
4. Commit 保存即可
5. Mihomo 到 interval 时间会自动拉取更新
