// 由 scripts/build.py 自动生成，请勿手动修改，改根目录的 .txt 即可
// Clash Verge Rev 全局扩展脚本：保留订阅里的节点，替换分组和规则。
// 用法：订阅页 → 全局扩展脚本 → 编辑 → 整段粘贴 → 保存。
// 规则内容按 interval 远程更新，只有规则顺序或分组改了才需要重新粘贴。

const ruleProviders = {
  "custom-reject": {
    "type": "http",
    "behavior": "classical",
    "format": "text",
    "url": "https://cdn.jsdelivr.net/gh/shawnxustudio/shawnxu-rules@main/dist/mihomo/reject.list",
    "path": "./ruleset/custom-reject.list",
    "interval": 3600
  },
  "custom-direct": {
    "type": "http",
    "behavior": "classical",
    "format": "text",
    "url": "https://cdn.jsdelivr.net/gh/shawnxustudio/shawnxu-rules@main/dist/mihomo/direct.list",
    "path": "./ruleset/custom-direct.list",
    "interval": 3600
  },
  "custom-proxy": {
    "type": "http",
    "behavior": "classical",
    "format": "text",
    "url": "https://cdn.jsdelivr.net/gh/shawnxustudio/shawnxu-rules@main/dist/mihomo/proxy.list",
    "path": "./ruleset/custom-proxy.list",
    "interval": 3600
  },
  "applications": {
    "type": "http",
    "behavior": "classical",
    "url": "https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/applications.txt",
    "path": "./ruleset/applications.yaml",
    "interval": 86400
  },
  "private": {
    "type": "http",
    "behavior": "domain",
    "url": "https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/private.txt",
    "path": "./ruleset/private.yaml",
    "interval": 86400
  },
  "lancidr": {
    "type": "http",
    "behavior": "ipcidr",
    "url": "https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/lancidr.txt",
    "path": "./ruleset/lancidr.yaml",
    "interval": 86400
  },
  "reject": {
    "type": "http",
    "behavior": "domain",
    "url": "https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/reject.txt",
    "path": "./ruleset/reject.yaml",
    "interval": 86400
  },
  "tld-not-cn": {
    "type": "http",
    "behavior": "domain",
    "url": "https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/tld-not-cn.txt",
    "path": "./ruleset/tld-not-cn.yaml",
    "interval": 86400
  },
  "gfw": {
    "type": "http",
    "behavior": "domain",
    "url": "https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/gfw.txt",
    "path": "./ruleset/gfw.yaml",
    "interval": 86400
  },
  "telegramcidr": {
    "type": "http",
    "behavior": "ipcidr",
    "url": "https://cdn.jsdelivr.net/gh/Loyalsoldier/clash-rules@release/telegramcidr.txt",
    "path": "./ruleset/telegramcidr.yaml",
    "interval": 86400
  }
};

const rules = [
  "RULE-SET,custom-reject,REJECT",
  "RULE-SET,custom-direct,DIRECT",
  "RULE-SET,custom-proxy,PROXY",
  "RULE-SET,applications,DIRECT",
  "RULE-SET,private,DIRECT",
  "RULE-SET,lancidr,DIRECT,no-resolve",
  "RULE-SET,reject,REJECT",
  "RULE-SET,tld-not-cn,PROXY",
  "RULE-SET,gfw,PROXY",
  "RULE-SET,telegramcidr,PROXY,no-resolve",
  "MATCH,DIRECT"
];

const infoNode = /剩余|到期|过期|官网|流量|重置|expire|traffic/i;

function main(config, profileName) {
  const names = (config.proxies || []).map((p) => p.name);
  if (names.length === 0) return config;
  const filtered = names.filter((n) => !infoNode.test(n));
  const nodes = filtered.length ? filtered : names;

  config["proxy-groups"] = [
    { name: "PROXY", type: "select", proxies: ["AUTO", ...nodes, "DIRECT"] },
    {
      name: "AUTO",
      type: "url-test",
      proxies: nodes,
      url: "https://www.gstatic.com/generate_204",
      interval: 300,
      tolerance: 50,
    },
  ];
  config["rule-providers"] = ruleProviders;
  config.rules = rules;
  return config;
}
