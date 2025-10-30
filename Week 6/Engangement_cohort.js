const duckdb = require('duckdb');

// Engangement_cohort.js
// Node.js script — deterministic seeded data generation and terminal display

// Seeded RNG (xmur3 + mulberry32)
function xmur3(str) {
    for (var i = 0, h = 1779033703 ^ str.length; i < str.length; i++) {
        h = Math.imul(h ^ str.charCodeAt(i), 3432918353);
        h = (h << 13) | (h >>> 19);
    }
    return function() {
        h = Math.imul(h ^ (h >>> 16), 2246822507);
        h = Math.imul(h ^ (h >>> 13), 3266489909);
        return (h ^ (h >>> 16)) >>> 0;
    };
}
function mulberry32(a) {
    return function() {
        var t = (a += 0x6D2B79F5);
        t = Math.imul(t ^ (t >>> 15), t | 1);
        t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
        return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
}

// Helpers
function seededRngFromString(seedStr) {
    const seedFunc = xmur3(seedStr);
    const seed = seedFunc();
    return mulberry32(seed);
}
function randomInt(rng, min, max) {
    return Math.floor(rng() * (max - min + 1)) + min;
}
function randomElem(rng, arr) {
    return arr[Math.floor(rng() * arr.length)];
}
function alphanumeric(rng, len = 10) {
    const chars = 'abcdefghijklmnopqrstuvwxyz0123456789';
    let out = '';
    for (let i = 0; i < len; i++) out += chars[Math.floor(rng() * chars.length)];
    return out;
}
function firstOfMonthUTC(date) {
    return new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), 1));
}
function isoDateOnly(d) {
    return d.toISOString().split('T')[0];
}

async function runCohortQueryInDuckDB(user_profiles, user_events) {
    // Requires the 'duckdb' package: npm install duckdb
    const db = new duckdb.Database(':memory:');
    const conn = db.connect();

    function run(sql, params = []) {
        return new Promise((resolve, reject) => {
            conn.all(sql, params, (err, rows) => {
                if (err) reject(err);
                else resolve(rows);
            });
        });
    }

    // Helper to escape single quotes for SQL literals
    const esc = s => String(s).replace(/'/g, "''");

    // Create tables
    await run(`CREATE TABLE user_profiles (user_id TEXT, signup_date DATE, cohort_month DATE, country TEXT, plan TEXT);`);
    await run(`CREATE TABLE user_events (user_id TEXT, event_date DATE, event_type TEXT, minutes_spent INTEGER, feature TEXT);`);

    // Bulk insert (build VALUES lists)
    if (user_profiles.length > 0) {
        const upVals = user_profiles.map(u =>
            `('${esc(u.user_id)}','${esc(u.signup_date)}','${esc(u.cohort_month)}','${esc(u.country)}','${esc(u.plan)}')`
        ).join(',');
        await run(`INSERT INTO user_profiles VALUES ${upVals};`);
    }

    if (user_events.length > 0) {
        const ueVals = user_events.map(e =>
            `('${esc(e.user_id)}','${esc(e.event_date)}','${esc(e.event_type)}',${Number(e.minutes_spent)||0},'${esc(e.feature)}')`
        ).join(',');
        await run(`INSERT INTO user_events VALUES ${ueVals};`);
    }

    // Query for March 2024 cohort (Enterprise, Australia), measure engagement in Aug 2024
    const sql = `
    WITH cohort_users AS (
      SELECT user_id
      FROM user_profiles
      WHERE cohort_month = DATE '2024-03-01'
        AND plan = 'Enterprise'
        AND country = 'Australia'
    ),
    sessions_in_aug AS (
      SELECT user_id, event_date::DATE AS event_date, minutes_spent
      FROM user_events
      WHERE event_type = 'session'
        AND event_date >= DATE '2024-08-01'
        AND event_date < DATE '2024-09-01'
    ),
    retained AS (
      SELECT DISTINCT s.user_id
      FROM sessions_in_aug s
      JOIN cohort_users c ON s.user_id = c.user_id
    )
    SELECT
      (SELECT COUNT(*) FROM cohort_users) AS cohort_users,
      (SELECT COUNT(*) FROM retained) AS retained_users,
      CASE WHEN (SELECT COUNT(*) FROM cohort_users)=0 THEN 0.0
           ELSE (SELECT COUNT(*) FROM retained)::DOUBLE / (SELECT COUNT(*) FROM cohort_users)
      END AS active_rate,
      CASE WHEN (SELECT COUNT(*) FROM retained)=0 THEN 0.0
           ELSE (SELECT COUNT(*) FROM sessions_in_aug s JOIN cohort_users c ON s.user_id = c.user_id)::DOUBLE
                / (SELECT COUNT(*) FROM retained)
      END AS avg_sessions_per_user,
      CASE WHEN (SELECT COUNT(*) FROM retained)=0 THEN 0.0
           ELSE (SELECT SUM(s.minutes_spent)::DOUBLE FROM sessions_in_aug s JOIN cohort_users c ON s.user_id = c.user_id)
                / (SELECT COUNT(*) FROM retained)
      END AS avg_minutes_per_user;
    `;

    const rows = await run(sql);
    // rows is an array with exactly one row per the query
    if (rows.length === 0) {
        console.log('No result returned.');
    } else {
        // Print single row to terminal
        console.log('Cohort (Mar 2024, Enterprise, Australia) — engagement in Aug 2024:');
        console.table(rows);
    }

    conn.close();
    db.close();
}

// Main generation function (mirrors original logic)
async function generate({ userEmail = '24f3001383@ds.study.iitm.ac.in', weight = 1 } = {}) {
    const a = 'q-duckdb-engagement-cohorts';
    const seedStr = `${userEmail}#${a}`;
    const rng = seededRngFromString(seedStr);

    // Constants
    const countries = ["United States", "Canada", "Germany", "United Kingdom", "India", "Australia", "Singapore"];
    const plans = ["Free", "Professional", "Enterprise"];
    const eventTypes = ["session", "workflow_run", "export", "collaboration", "admin_action"];
    const features = ["dashboard", "automation", "insights", "api", "billing", "governance"];

    // Date bounds
    const startDate = new Date("2023-11-01T00:00:00Z");
    const endDate = new Date("2024-05-31T23:59:59Z");
    const maxUsers = 520;

    // Storage
    const user_profiles = [];
    const user_events = [];

    function randBetweenDate(s, e) {
        return new Date(s.getTime() + rng() * (e.getTime() - s.getTime()));
    }
    function randInt(s, e) { return randomInt(rng, s, e); }
    function pick(arr) { return randomElem(rng, arr); }

    // Generate users and events
    for (let i = 0; i < maxUsers; i++) {
        const signup = randBetweenDate(startDate, endDate);
        const cohort_month = firstOfMonthUTC(signup);
        const user_id = `user_${alphanumeric(rng, 10)}`;
        const profile = {
            user_id,
            signup_date: isoDateOnly(signup),
            cohort_month: isoDateOnly(cohort_month),
            country: pick(countries),
            plan: pick(plans)
        };
        user_profiles.push(profile);

        const monthsCount = randInt(1, 6);
        for (let m = 0; m < monthsCount; m++) {
            // start from Nov 2023 month index 10, add m months
            const monthIndex = 10 + m;
            const monthYear = 2023 + Math.floor(monthIndex / 12);
            const monthMonth = monthIndex % 12;
            // Stop if beyond Aug 2024 per original logic
            if (new Date(Date.UTC(monthYear, monthMonth, 1)) > new Date("2024-08-01T00:00:00Z")) break;
            const eventsThisMonth = randInt(3, 12);
            for (let ev = 0; ev < eventsThisMonth; ev++) {
                const day = randInt(1, 28);
                const event_date = new Date(Date.UTC(monthYear, monthMonth, day));
                const event = {
                    user_id,
                    event_date: isoDateOnly(event_date),
                    event_type: pick(eventTypes),
                    minutes_spent: randInt(2, 90),
                    feature: pick(features)
                };
                user_events.push(event);
            }
        }
    }

    // Determine cohort selection similarly to original
    const cohortMonths = Array.from(new Set(user_profiles.map(u => u.cohort_month))).map(s => new Date(s));
    const D = new Date(pick(cohortMonths)); // selected cohort_month (Date)
    const chosenPlan = pick(plans);
    let chosenCountry = pick(countries);
    // get set of users in cohort with plan & country
    let cohortUserIds = new Set(user_profiles.filter(u =>
        new Date(u.cohort_month).getTime() === D.getTime() &&
        u.plan === chosenPlan &&
        u.country === chosenCountry
    ).map(u => u.user_id));
    // If empty, pick the last user's country (like original fallback)
    if (cohortUserIds.size === 0) {
        chosenCountry = user_profiles[user_profiles.length - 1].country;
        cohortUserIds = new Set(user_profiles.filter(u =>
            new Date(u.cohort_month).getTime() === D.getTime() &&
            u.plan === chosenPlan &&
            u.country === chosenCountry
        ).map(u => u.user_id));
    }

    // Active month p: pick month between May and Aug 2024 (original used random)
    const pMonthOffset = randInt(4, 7); // 4..7 -> May..Aug (0=Jan)
    const p = new Date(Date.UTC(2024, pMonthOffset, 1));
    const I = new Date(Date.UTC(p.getUTCFullYear(), p.getUTCMonth() + 1, 1));

    // Compute session-based retention metrics for cohort users in month p
    const usersWithSessionThisMonth = new Set();
    let totalSessions = 0;
    let totalMinutes = 0;

    for (const ev of user_events) {
        if (!cohortUserIds.has(ev.user_id)) continue;
        const evDate = new Date(ev.event_date + 'T00:00:00Z');
        // only count session events that are within [p, I)
        if (ev.event_type === 'session' && evDate >= p && evDate < I) {
            usersWithSessionThisMonth.add(ev.user_id);
            totalSessions += 1;
            totalMinutes += ev.minutes_spent;
        }
    }

    const n = cohortUserIds.size; // cohort_users
    const d = usersWithSessionThisMonth.size; // retained_users
    const active_rate = n === 0 ? 0 : d / n;
    const avg_sessions_per_user = d === 0 ? 0 : totalSessions / d;
    const avg_minutes_per_user = d === 0 ? 0 : totalMinutes / d;

    return {
        user_profiles,
        user_events,
        cohort: {
            cohort_month: isoDateOnly(D),
            plan: chosenPlan,
            country: chosenCountry,
            active_month: p.toLocaleString('en-US', { year: 'numeric', month: 'long', timeZone: 'UTC' }),
            cohort_users: n,
            retained_users: d,
            active_rate,
            avg_sessions_per_user,
            avg_minutes_per_user
        }
    };
}

// Run and display
(async () => {
    const { user_profiles, user_events, cohort } = await generate({ userEmail: 'alice@example.com' });

    console.log('Generated user_profiles:', user_profiles.length, 'rows');
    console.table(user_profiles.slice(0, 50)); // show first 50 rows

    console.log('Generated user_events:', user_events.length, 'rows');
    console.table(user_events.slice(0, 50)); // show first 50 rows

    console.log('Cohort summary:');
    console.table([{
        cohort_month: cohort.cohort_month,
        plan: cohort.plan,
        country: cohort.country,
        active_month: cohort.active_month,
        cohort_users: cohort.cohort_users,
        retained_users: cohort.retained_users,
        active_rate: Number(cohort.active_rate.toFixed(4)),
        avg_sessions_per_user: Number(cohort.avg_sessions_per_user.toFixed(4)),
        avg_minutes_per_user: Number(cohort.avg_minutes_per_user.toFixed(4))
    }]);

    console.log('Note: only first 50 rows shown for each table. Adjust slices if you want to see more.');
})();