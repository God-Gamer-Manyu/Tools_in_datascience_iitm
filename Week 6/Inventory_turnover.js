// test.js
// Deterministic dataset generator (no DuckDB) based on your snippet
const user = { email: "24f3001383@ds.study.iitm.ac.in" }; // as requested
const seedString = `${user.email}#q-duckdb-inventory-turnover`;

// small string -> seed number hash (xfnv1a)
function xfnv1a(str) {
    let h = 2166136261 >>> 0;
    for (let i = 0; i < str.length; i++) {
        h ^= str.charCodeAt(i);
        h = Math.imul(h, 16777619) >>> 0;
    }
    return h >>> 0;
}
// mulberry32 PRNG from seed number
function mulberry32(a) {
    return function () {
        a |= 0;
        a = (a + 0x6D2B79F5) | 0;
        let t = Math.imul(a ^ (a >>> 15), 1 | a);
        t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
        return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
}

const seedNum = xfnv1a(seedString);
const rand = mulberry32(seedNum); // function that returns 0..1

// helpers matching original logic
const locations = ["RTP-1","RTP-2","AMS-1","SIN-2","LHR-1","DFW-3"];
const categories = ["Electronics","Spare Parts","Perishables","Packaging","Calibration","Finished Goods"];

// build SKUs (8 per category)
const SKUs = [];
categories.forEach((cat, idx) => {
    for (let d = 0; d < 8; d++) {
        const sku = `SKU-${idx+1}${String(d).padStart(2,"0")}`;
        SKUs.push({ sku, category: cat });
    }
});

function randint(min, max) { // inclusive
    return Math.floor(rand()*(max-min+1)) + min;
}
function randChoice(arr) {
    return arr[Math.floor(rand()*arr.length)];
}
function randDateBetween(a, b) {
    const at = a.getTime();
    const bt = b.getTime();
    const t = at + rand()*(bt - at);
    return new Date(t);
}
function isoDate(d) { return d.toISOString().split("T")[0]; }

// build sku_attributes
const sku_attributes = SKUs.map(({sku, category}) => ({
    sku,
    category,
    safety_stock: randint(40,160),
    lead_time_days: randint(7,35)
}));

// build inventory_movements
const movements = [];
const movementTypes = ["INBOUND","OUTBOUND","ADJUSTMENT"];
const adjDirections = ["add","remove"];
const qualityFlags = ["normal","cycle_count","scrap","vendor_return"];

const L = new Date("2024-01-01T00:00:00Z");
const B = new Date("2024-07-31T00:00:00Z");

const F = 720;
for (let i = 0; i < F; i++) {
    const skuObj = randChoice(SKUs);
    const loc = randChoice(locations);
    const mvType = randChoice(movementTypes);
    const quantity = randint(5,140);
    const unit_cost = Math.round((rand()*120 + 25) * 100) / 100;
    const adj_dir = mvType === "ADJUSTMENT" ? randChoice(adjDirections) : null;
    const qflag = mvType === "ADJUSTMENT" ? randChoice(qualityFlags) : "normal";
    const mdate = randDateBetween(L, B);
    const rec = {
        movement_id: `MV-${String(i+1).padStart(4,"0")}`,
        sku: skuObj.sku,
        category: skuObj.category,
        location: loc,
        movement_type: mvType,
        quantity,
        unit_cost,
        adjustment_direction: adj_dir,
        quality_flag: qflag,
        movement_date: mdate
    };
    movements.push(rec);
}

// pick a random location & category & window and ensure there's at least one inbound in the window
let D = randChoice(locations);
let C = randChoice(categories);
let q = randDateBetween(L,B);
let j = new Date(q.getTime() + randint(30,70)*24*60*60*1000);

let windowRecords = movements.filter(m => (m.location === D && m.category === C && m.movement_date >= q && m.movement_date <= j));
if (!windowRecords.length || !windowRecords.some(m => m.movement_type === "INBOUND")) {
    // take a random existing movement and change its location/category to match selection (to ensure some data)
    const e = randChoice(movements);
    e.location = D;
    e.category = C;
    // optionally set one as INBOUND
    e.movement_type = "INBOUND";
    e.movement_date = randDateBetween(q, j);
    windowRecords = movements.filter(m => (m.location === D && m.category === C && m.movement_date >= q && m.movement_date <= j));
}

// compute stats function like original
function computeStats() {
    const e = movements.filter(s => (s.location === D && s.category === C && s.movement_date >= q && s.movement_date <= j));
    const inbound = e.filter(s => s.movement_type === "INBOUND");
    const outbound = e.filter(s => s.movement_type === "OUTBOUND");
    const adjustments = e.filter(s => s.movement_type === "ADJUSTMENT");
    const skuSet = new Set(e.map(s => s.sku));
    const total_inbound = inbound.reduce((acc, r) => acc + r.quantity, 0);
    const total_outbound = outbound.reduce((acc, r) => acc + r.quantity, 0);
    const adjustment_net = adjustments.reduce((acc, r) => acc + (r.adjustment_direction === "remove" ? -r.quantity : r.quantity), 0);
    const net_quantity = total_inbound - total_outbound + adjustment_net;
    const avg_inbound_unit_cost = total_inbound === 0 ? 0 : inbound.reduce((acc, r) => acc + r.quantity*r.unit_cost, 0) / total_inbound;
    return {
        sku_count: skuSet.size,
        total_inbound,
        total_outbound,
        adjustment_net,
        net_quantity,
        avg_inbound_unit_cost
    };
}

let stats = computeStats();
if (stats.total_inbound === 0 || stats.sku_count === 0) { stats = computeStats(); } // repeat as in original

// Print summary and samples to terminal
console.log("User email:", user.email);
console.log("Selected location:", D, "category:", C);
console.log("Window start:", isoDate(q), "end:", isoDate(j));
console.log("\nStats for window:");
console.table([stats]);

console.log("\nSKU attributes sample (first 10):");
console.table(sku_attributes.slice(0, 10));

console.log("\nInventory movements sample (first 20):");
const sampleMovements = movements
    .sort((a,b) => a.movement_date - b.movement_date)
    .slice(0, 20)
    .map(m => ({
        movement_id: m.movement_id,
        sku: m.sku,
        category: m.category,
        location: m.location,
        movement_type: m.movement_type,
        quantity: m.quantity,
        unit_cost: m.unit_cost,
        adjustment_direction: m.adjustment_direction,
        quality_flag: m.quality_flag,
        movement_date: isoDate(m.movement_date)
    }));
console.table(sampleMovements);

// If you want to dump full arrays to disk uncomment the block below (requires fs):
/*
const duckdb = require('duckdb');

async function runQueryWithDuckDB() {
    const db = new duckdb.Database(':memory:');
    const con = db.connect();

    const run = (sql) => new Promise((res, rej) => con.run(sql, (err) => err ? rej(err) : res()));
    const all = (sql) => new Promise((res, rej) => con.all(sql, (err, rows) => err ? rej(err) : res(rows)));

    const esc = (v) => {
        if (v === null || v === undefined) return 'NULL';
        if (typeof v === 'number') return v;
        return "'" + String(v).replace(/'/g, "''") + "'";
    };

    // Create tables matching the schema you specified:
    // inventory_movements: movement_id, sku, location, movement_type, quantity, unit_cost, adjustment_direction, quality_flag, movement_date
    // sku_attributes: sku, category, safety_stock, lead_time_days
    await run(`CREATE TABLE sku_attributes (
        sku VARCHAR, category VARCHAR, safety_stock INTEGER, lead_time_days INTEGER
    );`);
    await run(`CREATE TABLE inventory_movements (
        movement_id VARCHAR, sku VARCHAR, location VARCHAR,
        movement_type VARCHAR, quantity INTEGER, unit_cost DOUBLE,
        adjustment_direction VARCHAR, quality_flag VARCHAR, movement_date DATE
    );`);

    // Insert sku_attributes
    if (sku_attributes.length) {
        const skuVals = sku_attributes.map(s =>
            `(${esc(s.sku)},${esc(s.category)},${s.safety_stock},${s.lead_time_days})`
        ).join(',');
        await run(`INSERT INTO sku_attributes VALUES ${skuVals};`);
    }

    // Insert inventory_movements (omit category column here, it's in sku_attributes)
    if (movements.length) {
        const movVals = movements.map(m =>
            `(${esc(m.movement_id)},${esc(m.sku)},${esc(m.location)},` +
            `${esc(m.movement_type)},${m.quantity},${Number(m.unit_cost)},` +
            `${esc(m.adjustment_direction)},${esc(m.quality_flag)},${esc(isoDate(m.movement_date))})`
        ).join(',');
        await run(`INSERT INTO inventory_movements VALUES ${movVals};`);
    }

    // Query: join inventory_movements with sku_attributes to filter by category
    const sql = `
        WITH filtered AS (
            SELECT m.*
            FROM inventory_movements m
            JOIN sku_attributes s ON m.sku = s.sku
            WHERE m.location = 'LHR-1'
                AND s.category = 'Spare Parts'
                AND m.movement_date BETWEEN DATE '2024-01-13' AND DATE '2024-03-04'
                -- ignore adjustment write-offs already accounted elsewhere
                AND NOT (m.movement_type = 'ADJUSTMENT' AND m.quality_flag = 'scrap')
        )
        SELECT
            COUNT(DISTINCT sku) AS sku_count,
            COALESCE(SUM(CASE WHEN movement_type = 'INBOUND' THEN quantity ELSE 0 END), 0) AS total_inbound,
            COALESCE(SUM(CASE WHEN movement_type = 'OUTBOUND' THEN quantity ELSE 0 END), 0) AS total_outbound,
            COALESCE(SUM(
                CASE
                    WHEN movement_type = 'INBOUND' THEN quantity
                    WHEN movement_type = 'OUTBOUND' THEN -quantity
                    WHEN movement_type = 'ADJUSTMENT' THEN (CASE WHEN adjustment_direction = 'remove' THEN -quantity ELSE quantity END)
                    ELSE 0
                END
            ), 0) AS net_quantity,
            COALESCE(
                SUM(CASE WHEN movement_type = 'INBOUND' THEN quantity * unit_cost ELSE 0 END) /
                NULLIF(SUM(CASE WHEN movement_type = 'INBOUND' THEN quantity ELSE 0 END), 0),
            0) AS avg_inbound_unit_cost
        FROM filtered;
    `;

    const rows = await all(sql);

    if (rows.length) {
        console.log('\nDuckDB query result:');
        console.table(rows);
    } else {
        console.log('No rows returned by query.');
    }

    con.close();
    db.close();
}

runQueryWithDuckDB().catch(err => {
    console.error('DuckDB error:', err);
    process.exit(1);
});
*/