const fs = require('fs');
const path = require('path');

// GitHub Copilot
// Save as DBT.js and run with: node DBT.js --file model.sql --email you@org.com --metric delayed_shipments --flow fulfillment --type "mart model" --frequency daily --days 30


const flows = [
    { name: "fulfillment", metrics: ["delayed_shipments", "ontime_percentage", "avg_transit_days"], businessTerms: ["shipment", "carrier", "warehouse", "delivery", "transit"] },
    { name: "inventory", metrics: ["stockouts", "avg_days_on_hand", "cycle_accuracy"], businessTerms: ["inventory", "sku", "cycle", "stock", "warehouse"] },
    { name: "returns", metrics: ["rma_volume", "percent_refunded", "avg_processing_hours"], businessTerms: ["return", "rma", "refund", "restock", "inspection"] },
    { name: "support", metrics: ["sla_breaches", "avg_handle_minutes", "first_contact_resolution"], businessTerms: ["ticket", "agent", "sla", "queue", "contact"] }
];

const modelRules = {
    "mart model": [
        { name: "uses_ref", pattern: /{{\s*ref\(/i, message: "Mart models should use {{ ref() }} for dependencies." },
        { name: "group_by", pattern: /\bgroup\s+by\b/i, message: "Mart models require grouping for aggregations." },
        { name: "order_by", pattern: /\border\s+by\b/i, message: "Mart models should order results for BI friendliness." }
    ],
    "intermediate model": [
        { name: "uses_ref", pattern: /{{\s*ref\(/i, message: "Intermediate models should source data via {{ ref() }}." },
        { name: "cte", pattern: /\bwith\b/i, message: "Intermediate models should be structured with CTEs." }
    ]
};

const datePatterns = {
    daily: [/date_trunc\s*\(\s*'day'/i, /\b::date\b/i],
    weekly: [/date_trunc\s*\(\s*'week'/i, /\bextract\s*\(\s*week/i]
};

const metricTerms = {
    delayed_shipments: ["case", "delay", "interval", "count"],
    ontime_percentage: ["count", "case", "%", "ratio"],
    avg_transit_days: ["avg", "date_diff", "datediff"],
    stockouts: ["count", "stockout", "zero", "quantity"],
    avg_days_on_hand: ["avg", "days_on_hand", "inventory"],
    cycle_accuracy: ["count", "cycle", "accuracy"],
    rma_volume: ["count", "rma"],
    percent_refunded: ["sum", "refund", "amount"],
    avg_processing_hours: ["avg", "hour", "timestamp"],
    sla_breaches: ["case", "sla", "breach"],
    avg_handle_minutes: ["avg", "handle", "minute"],
    first_contact_resolution: ["count", "resolution", "first"]
};

function validateModel(sql, opts = {}) {
    // opts: { flow, metric, type, frequency, days }
    const checks = [];
    const s = (sql || '').toString();
    const t = (opts.type || "mart model");
    const T = (opts.frequency || "daily");
    const k = (opts.metric || "");
    const flowObj = flows.find(f => f.name === opts.flow) || flows[0];
    const businessTerms = flowObj.businessTerms || [];
    const metricWords = (metricTerms[k] || []);

    // 1. Non-empty
    checks.push({ check: "non_empty", passed: !!s.trim(), message: "Provide a dbt SQL model." });

    // 2. Jinja templating
    checks.push({ check: "jinja", passed: /{{/.test(s), message: "Use Jinja templating ({{ }}) for dbt models." });

    // 3. Model type rules (loop through required patterns)
    const rules = modelRules[t] || [];
    for (const r of rules) {
        checks.push({ check: r.name, passed: r.pattern.test(s), message: r.message });
    }

    // 4. Date handling for frequency
    const datePat = datePatterns[T] || [];
    const dateOk = (datePat[0] && datePat[0].test(s)) || (datePat[1] && datePat[1].test(s));
    checks.push({ check: "date_handling", passed: dateOk, message: `Include ${T} date handling (e.g. date_trunc('${T}', ...) or EXTRACT).` });

    // 5. Metric-specific logic
    const metricOk = metricWords.length === 0 || metricWords.some(w => s.toLowerCase().includes(w.toLowerCase()));
    checks.push({ check: "metric_logic", passed: metricOk, message: metricWords.length ? `Include logic related to ${k} (patterns like ${metricWords.join(", ")}).` : "No metric specified to validate." });

    // 6. Business/domain terms
    const domainOk = businessTerms.length === 0 || businessTerms.some(w => s.toLowerCase().includes(w.toLowerCase()));
    checks.push({ check: "domain_terms", passed: domainOk, message: businessTerms.length ? `Reference domain concepts such as ${businessTerms.join(", ")}.` : "No flow/business terms available." });

    // 7. Recent date filter (rudimentary)
    const days = opts.days || 30;
    const recentDateOk = /where\s+.+\bdate\b.+(>=|between)/i.test(s) || new RegExp(`date\\s*>=\\s*current_date\\s*-\\s*interval\\s+'?${days}'?`, 'i').test(s);
    checks.push({ check: "recent_filter", passed: recentDateOk, message: `Filter the dataset for the last ${days} days.` });

    // 8. SELECT and FROM
    const selectFromOk = /select/i.test(s) && /from/i.test(s);
    checks.push({ check: "select_from", passed: selectFromOk, message: "SQL must include SELECT and FROM clauses." });

    // 9. Missing value handling
    const missingOk = /coalesce|ifnull|isnull/i.test(s) || /\b0\)/.test(s);
    checks.push({ check: "missing_values", passed: missingOk, message: "Handle missing values using COALESCE/IFNULL." });

    // 10. Config block
    const configOk = /{{\s*config\s*\(/i.test(s);
    checks.push({ check: "config_block", passed: configOk, message: "Add a {{ config(...) }} block to declare materialization and freshness." });

    // Aggregate result
    const passedAll = checks.every(c => c.passed);
    return { passed: passedAll, checks };
}

// Simple CLI
function parseArgs() {
    const argv = process.argv.slice(2);
    const res = {};
    for (let i = 0; i < argv.length; i++) {
        const a = argv[i];
        if (a.startsWith('--')) {
            const key = a.slice(2);
            const val = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[++i] : true;
            res[key] = val;
        }
    }
    return res;
}

async function main() {
    const args = parseArgs();
    let sql = "";
    if (args.file) {
        const fp = path.resolve(args.file);
        if (!fs.existsSync(fp)) {
            console.error("File not found:", fp);
            console.log("\nExample dbt model you can create at:", fp, "\n");
            console.log(`
{{ config(materialized='table', tags=['mart'], meta={'owner':'data_team','freshness_days':1}) }}

-- Build on top of staging (e.g. stg_shipments). Uses {{ ref() }} + Jinja templating.
with src as (
  select
    date_trunc('day', coalesce(s.created_at, current_date)) as day,
    coalesce(s.order_id, '') as order_id,
    coalesce(s.sla_minutes, 0) as sla_minutes,
    coalesce(s.handle_minutes, 0) as handle_minutes,
    coalesce(s.first_contact_resolution, false) as first_contact_resolution,
    coalesce(s.some_status, '') as some_status
  from {{ ref('stg_shipments') }} s
  where date_trunc('day', s.created_at) between current_date - interval '45' day and current_date
)

select
  day,
  count(1) as total_interactions,
  sum(case when first_contact_resolution then 1 else 0 end) as first_contact_resolutions,
  round(100.0 * sum(case when first_contact_resolution then 1 else 0 end) / nullif(count(1),0), 2) as first_contact_resolution_pct,
  sum(case when handle_minutes > sla_minutes then 1 else 0 end) as sla_breaches,
  round(avg(handle_minutes), 2) as avg_handle_minutes
from src
group by 1
order by 1;
`);
            process.exit(2);
            process.exit(2);
        }
        sql = fs.readFileSync(fp, 'utf8');
    } else if (args.sql) {
        sql = args.sql;
    } else {
        console.error("Provide --file model.sql or --sql '<sql>'");
        process.exit(1);
    }

    const opts = {
        flow: args.flow || args.f || "fulfillment",
        metric: args.metric || args.m || "",
        type: args.type || "mart model",
        frequency: args.frequency || args.frequency || "daily",
        days: Number(args.days || 30),
        email: args.email || ""
    };

    const result = validateModel(sql, opts);

    // Display table of checks
    const tableRows = result.checks.map(c => ({ check: c.check, passed: c.passed ? "YES" : "NO", message: c.message }));
    console.log("\nValidation results:");
    console.table(tableRows);

    console.log("Overall:", result.passed ? "PASS" : "FAIL");
    process.exit(result.passed ? 0 : 3);
}

if (require.main === module) {
    main();
}

module.exports = { validateModel };