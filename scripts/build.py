#!/usr/bin/env python3
"""把 proxy.txt / direct.txt / reject.txt 构建成各客户端可用的规则和配置。

源文件每行一条：
  +.example.com    匹配域名及所有子域名
  example.com      精确匹配
  keyword:example  域名中包含该关键词即匹配

输出到 dist/：
  mihomo/*.list         Mihomo classical 规则集（Clash Verge / 群晖 Mihomo 共用）
  mihomo/*.txt          旧版 domain 规则集，不含关键词，仅为兼容未更新的配置
  shadowrocket/*.list   Shadowrocket RULE-SET 格式规则集
  mihomo.yaml           群晖 Mihomo 完整配置（订阅链接需在 NAS 上自行填写）
  clash-verge.js        Clash Verge Rev 全局扩展脚本
  shadowrocket.conf     Shadowrocket 配置（URL 导入）

用法: python scripts/build.py
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"

REPO = "shawnxustudio/shawnxu-rules"
SELF_CDN = f"https://cdn.jsdelivr.net/gh/{REPO}@main/dist"
CLASH_CDN = "https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release"
SURGE_CDN = "https://cdn.jsdelivr.net/gh/Loyalsoldier/surge-rules@release/ruleset"

PROXY = "PROXY"
AUTO = "AUTO"

# 个人规则文件，按优先级排列（越靠前越优先）
CUSTOM = [
    ("reject", "REJECT"),
    ("direct", "DIRECT"),
    ("proxy", PROXY),
]

# Loyalsoldier 黑名单模式规则：(名称, behavior, 策略, 是否给 Shadowrocket 用)
# applications 是 PROCESS-NAME 规则，iOS 上没有意义
# lancidr 在 surge-rules 里没有，Shadowrocket 由 skip-proxy / bypass-tun 绕过局域网
UPSTREAM = [
    ("applications", "classical", "DIRECT", False),
    ("private", "domain", "DIRECT", True),
    ("lancidr", "ipcidr", "DIRECT", False),
    ("reject", "domain", "REJECT", True),
    ("tld-not-cn", "domain", PROXY, True),
    ("gfw", "domain", PROXY, True),
    ("telegramcidr", "ipcidr", PROXY, True),
]

FINAL = "DIRECT"

# 订阅里的流量、到期提示等信息节点，不放进分组
INFO_NODE = "剩余|到期|过期|官网|流量|重置|expire|traffic"

DOMAIN_RE = re.compile(r"^(?=.{1,253}$)([a-z0-9_]([a-z0-9_-]{0,61}[a-z0-9_])?\.)*[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$")
KEYWORD_RE = re.compile(r"^[a-z0-9._-]+$")

# 规则种类 → 规则类型
RULE_TYPE = {"suffix": "DOMAIN-SUFFIX", "exact": "DOMAIN", "keyword": "DOMAIN-KEYWORD"}


def parse(path):
    """返回 [(种类, 值)]，种类为 suffix / exact / keyword，遇到格式错误直接退出。"""
    entries, seen, errors = [], set(), []
    for no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.split("#", 1)[0].strip().lower()
        if not line:
            continue
        if line.startswith("keyword:"):
            kind, value, valid = "keyword", line[8:].strip(), KEYWORD_RE
        elif line.startswith("+."):
            kind, value, valid = "suffix", line[2:], DOMAIN_RE
        else:
            kind, value, valid = "exact", line, DOMAIN_RE
        if not valid.match(value):
            errors.append(f"{path.name}:{no}: 无法识别的规则 {raw.strip()!r}")
            continue
        if (kind, value) in seen:
            print(f"提示 {path.name}:{no}: 重复的 {line}，已忽略")
            continue
        seen.add((kind, value))
        entries.append((kind, value))
    if errors:
        sys.exit("\n".join(errors))
    return entries


def matched_by(kind, value, entries):
    """返回 entries 中会抢先匹配 value 的那条规则，没有则返回 None。"""
    if kind == "keyword":
        return next((f"keyword:{v}" for k, v in entries if k == "keyword" and v in value), None)
    parts = value.split(".")
    suffixes = {".".join(parts[i:]) for i in range(len(parts))}
    for k, v in entries:
        if (k == "keyword" and v in value) or (k == "suffix" and v in suffixes) or (k == "exact" and kind == "exact" and v == value):
            return f"keyword:{v}" if k == "keyword" else v
    return None


def check_conflicts(rules):
    """同一个域名被多个文件匹配时提示，优先级高的文件会生效。"""
    for i, (name, _) in enumerate(CUSTOM):
        for later, _ in CUSTOM[i + 1:]:
            for kind, value in rules[later]:
                hit = matched_by(kind, value, rules[name])
                if hit:
                    print(f"提示: {later}.txt 的 {value} 已被 {name}.txt 的 {hit} 覆盖，以 {name} 为准")


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def header(comment):
    return f"{comment} 由 scripts/build.py 自动生成，请勿手动修改，改根目录的 .txt 即可\n"


def mihomo_providers():
    providers = {}
    for name, _ in CUSTOM:
        providers[f"custom-{name}"] = {
            "type": "http",
            "behavior": "classical",
            "format": "text",
            "url": f"{SELF_CDN}/mihomo/{name}.list",
            "path": f"./ruleset/custom-{name}.list",
            # 个人规则文件很小、改得勤，1 小时拉一次
            "interval": 3600,
        }
    for name, behavior, _, _ in UPSTREAM:
        providers[name] = {
            "type": "http",
            "behavior": behavior,
            "url": f"{CLASH_CDN}/{name}.txt",
            "path": f"./ruleset/{name}.yaml",
            "interval": 86400,
        }
    return providers


def mihomo_rules():
    rules = [f"RULE-SET,custom-{name},{policy}" for name, policy in CUSTOM]
    for name, behavior, policy, _ in UPSTREAM:
        rules.append(f"RULE-SET,{name},{policy}" + (",no-resolve" if behavior == "ipcidr" else ""))
    rules.append(f"MATCH,{FINAL}")
    return rules


def yaml_value(v):
    return json.dumps(v, ensure_ascii=False) if isinstance(v, str) else str(v).lower() if isinstance(v, bool) else str(v)


def build_mihomo_yaml():
    lines = [header("#").rstrip(), "# 群晖 Mihomo 完整配置。只需把下方 <在这里填写你的订阅链接> 换成机场订阅。", "# 注意：填好订阅的文件只放在 NAS 上，不要提交回仓库。", ""]
    lines += [
        "mixed-port: 7890",
        "allow-lan: true",
        "bind-address: \"*\"",
        "mode: rule",
        "log-level: info",
        "ipv6: false",
        "external-controller: 0.0.0.0:9090",
        "secret: \"<在这里设置面板密码>\"",
        "",
        "profile:",
        "  store-selected: true",
        "",
        "dns:",
        "  enable: true",
        "  ipv6: false",
        "  enhanced-mode: redir-host",
        "  default-nameserver: [223.5.5.5, 119.29.29.29]",
        "  nameserver: [\"https://dns.alidns.com/dns-query\", \"https://doh.pub/dns-query\"]",
        "",
        "proxy-providers:",
        "  airport:",
        "    type: http",
        "    url: \"<在这里填写你的订阅链接>\"",
        "    path: ./providers/airport.yaml",
        "    interval: 86400",
        "    health-check:",
        "      enable: true",
        "      url: https://www.gstatic.com/generate_204",
        "      interval: 300",
        "",
        "proxy-groups:",
        f"  - name: {PROXY}",
        "    type: select",
        f"    proxies: [{AUTO}, DIRECT]",
        "    use: [airport]",
        f"    exclude-filter: \"{INFO_NODE}\"",
        f"  - name: {AUTO}",
        "    type: url-test",
        "    use: [airport]",
        "    url: https://www.gstatic.com/generate_204",
        "    interval: 300",
        "    tolerance: 50",
        f"    exclude-filter: \"{INFO_NODE}\"",
        "",
        "rule-providers:",
    ]
    for name, conf in mihomo_providers().items():
        lines.append(f"  {name}:")
        lines += [f"    {k}: {yaml_value(v)}" for k, v in conf.items()]
    lines += ["", "rules:"] + [f"  - {r}" for r in mihomo_rules()]
    return "\n".join(lines) + "\n"


def build_clash_verge_js():
    providers = json.dumps(mihomo_providers(), ensure_ascii=False, indent=2)
    rules = json.dumps(mihomo_rules(), ensure_ascii=False, indent=2)
    return f"""{header("//").rstrip()}
// Clash Verge Rev 全局扩展脚本：保留订阅里的节点，替换分组和规则。
// 用法：订阅页 → 全局扩展脚本 → 编辑 → 整段粘贴 → 保存。
// 规则内容按 interval 远程更新，只有规则顺序或分组改了才需要重新粘贴。

const ruleProviders = {providers};

const rules = {rules};

const infoNode = /{INFO_NODE}/i;

function main(config, profileName) {{
  const names = (config.proxies || []).map((p) => p.name);
  if (names.length === 0) return config;
  const filtered = names.filter((n) => !infoNode.test(n));
  const nodes = filtered.length ? filtered : names;

  config["proxy-groups"] = [
    {{ name: "{PROXY}", type: "select", proxies: ["{AUTO}", ...nodes, "DIRECT"] }},
    {{
      name: "{AUTO}",
      type: "url-test",
      proxies: nodes,
      url: "https://www.gstatic.com/generate_204",
      interval: 300,
      tolerance: 50,
    }},
  ];
  config["rule-providers"] = ruleProviders;
  config.rules = rules;
  return config;
}}
"""


def build_shadowrocket_conf():
    rules = [f"RULE-SET,{SELF_CDN}/shadowrocket/{name}.list,{policy}" for name, policy in CUSTOM]
    for name, behavior, policy, ios in UPSTREAM:
        if ios:
            rules.append(f"RULE-SET,{SURGE_CDN}/{name}.txt,{policy}" + (",no-resolve" if behavior == "ipcidr" else ""))
    rules.append(f"FINAL,{FINAL}")
    return "\n".join([
        header("#").rstrip(),
        "# Shadowrocket 配置：配置 → 右上角 + → 粘贴本文件的 URL → 下载后点击使用。",
        "# 节点仍在 Shadowrocket 首页的订阅里管理，规则里的 PROXY 即首页选中的节点。",
        "",
        "[General]",
        "bypass-system = true",
        "skip-proxy = 192.168.0.0/16, 10.0.0.0/8, 172.16.0.0/12, localhost, *.local, captive.apple.com",
        "bypass-tun = 10.0.0.0/8, 100.64.0.0/10, 127.0.0.0/8, 169.254.0.0/16, 172.16.0.0/12, 192.0.0.0/24, 192.0.2.0/24, 192.88.99.0/24, 192.168.0.0/16, 198.18.0.0/15, 198.51.100.0/24, 203.0.113.0/24, 224.0.0.0/4, 255.255.255.255/32",
        "dns-server = system",
        "ipv6 = false",
        f"update-url = {SELF_CDN}/shadowrocket.conf",
        "",
        "[Rule]",
        *rules,
        "",
        "[Host]",
        "localhost = 127.0.0.1",
        "",
    ])


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    rules ={name: parse(ROOT / f"{name}.txt") for name, _ in CUSTOM}
    check_conflicts(rules)

    for name, _ in CUSTOM:
        entries = rules[name]
        classical = header("#") + "".join(f"{RULE_TYPE[k]},{v}\n" for k, v in entries)
        write(DIST / "mihomo" / f"{name}.list", classical)
        write(DIST / "shadowrocket" / f"{name}.list", classical)
        write(DIST / "mihomo" / f"{name}.txt",
              header("#") + "# 旧版格式，不含关键词规则，请改用同目录的 .list\n"
              + "".join(f"{'+.' if k == 'suffix' else ''}{v}\n" for k, v in entries if k != "keyword"))

    write(DIST / "mihomo.yaml", build_mihomo_yaml())
    write(DIST / "clash-verge.js", build_clash_verge_js())
    write(DIST / "shadowrocket.conf", build_shadowrocket_conf())

    print("构建完成: " + ", ".join(f"{name} {len(rules[name])} 条" for name, _ in CUSTOM))


if __name__ == "__main__":
    main()
